$( document ).ready(function() {
    setUpAllMetricElements();
});

/**
 * A simple sum function.
 * @param {*} arr Takes an array of values and sums them up to one array.
 */
function sum(arr) {
    return arr.reduce((acc, val) => acc + val, 0);
}


/**
 * A simple mean function.
 * Uses the sum function to sum the numbers up first.
 * @param {*} arr Takes an array of numbers and computes the mean value of them.
 */
function mean(arr) {
    return (sum(arr) / arr.length).toFixed(3);
}

/**
 * Parses a given formula for datapoint identifiers and replaces them with their values
 * @param {*} formula Takes a String as formula. It contains identifiers like 'dp_1' as links to datapoints and 'sum()' and 'mean()' funciton calls.
 * @param {*} data May take data if data shall not be queried from the database via the api. If data is null the data will be taken from the api.
 * @param {*} timestamp May take a timestamp if the formulas data values shall be taken from a specified timestamp. Formula will use the last value of the linked datapoint if no timestamp is given.
 */
async function parse_formula(formula, data, timestamp=null) {
    var datapoint_linkings = formula.matchAll("dp_\\d+");
    var datapointStrings = [];
    for (var link of datapoint_linkings) {
        value = link[0];
        if (value == undefined) {
            continue;
        }
        else {
            datapointStrings.push(value);
        }
    }
    var output = formula;
    //If sum or mean are used there has to be an array of values instead of one single value. Thats why we differenciate.
    if(formula.includes("sum") || formula.includes("mean")) {
        if(datapointStrings.length != 1) return "0"
        var match = datapointStrings[0].match("\\d");
        var datapoint = await getDatapoint(match);
        if (datapoint["data_format"] == "discrete_numeric" && datapoint["allowed_values"] == "[0,1") {
            showError("You or your system admin used a metric over on/off values. This is not possivble. Please fix that or contact your system administrator!");
            output = "0";
        }
        else {
            var datapoints = [];
            var values = [];
            if (data == null && timestamp == null) {
                datapoints = await getDatapointValues(match);
            }
            else if (data != null && timestamp == null) {
                datapoints = data[datapoint["origin_id"]];
            }
            else {
                showError("You or your system admin used a metric over timestamps. This is not possivble. Please fix that or contact your system administrator!");
            }
    
            for (var datapoint of datapoints) {
                values.push(datapoint.value);
            }
            output = output.replace(datapointStrings[0], "["+ values.toString() +"]")
        }
    }
    else {
        for (var datapointString of datapointStrings) {
            var match = datapointString.match("\\d");
            var datapoint = await getDatapoint(match);
            var value;
            if (data == null && timestamp == null)  {
                value = datapoint["last_value"];
            }
            else if (data == null && timestamp != null) {
                value = (await getDatapointValueOf(match, timestamp))["value"]
            }
            else if (data != null & timestamp != null) {
                value = data[datapoint["origin_id"]].reduce((acc, object) => acc + ((object["timestamp"] == timestamp) ? parseFloat(object["value"]) : 0), 0);
            }
            else {
                value = data[datapoint["origin_id"]][data[datapoint["origin_id"]].length - 1]["value"];
            }
            output = output.replace(datapointString, value);
        }
    }
    return output 
}

/**
 * This function calculates the result of a formula.
 * For evaluation the JavaScript build in eval() funtion is used. Therefore, it is possible to use all JavaScript functions in the formulas.
 * The formulas result will be returned.
 * @param {*} formula The formula is given as String in the paramters. It contains 'dp_1' as links to datapoints and 'sum()' and 'mean()' funciton calls.
 * The formula will be parsed and the paresed formula evlauated.
 *  @param {*} data If the values of the linked datapoints shall not be queried from the database, one can give additional data as parameter.
 *   The additional data has to be in the following structure: 
 *  {
 *      "datapoint_origin_id" : [Array of JSON objects with timestamps and values]
 *      ...
 *  }
 */
async function calculate(formula, data=null){
    console.log(data)
    var parsedFormula = await parse_formula(formula, data);
    var result = eval(parsedFormula);
    return result;
}

/**
 * This function calculates the result of a formula given multiple timestamps.
 * For evaluation the JavaScript build in eval() funtion is used. Therefore, it is possible to use all JavaScript functions in the formulas.
 * The formulas result will be returned as array with one entry for each timestamp.
 * @param {*} formula The formula is given as String in the paramters. It contains 'dp_1' as links to datapoints and 'sum()' and 'mean()' funciton calls.
 * The formula will be parsed and the paresed formula evlauated.
 * @param {*} timestamps The timestamps are given in an array.
 * @param {*} data If the values of the linked datapoints shall not be queried from the database, one can give additional data as parameter.
 *   The additional data has to be in the following structure: 
 *  {
 *      "datapoint_origin_id" : [Array of JSON objects with timestamps and values]
 *      ...
 *  }
 */ 
async function calculateMetricDataSet(formula, timestamps, data=null) {
    var dataset = [];
    for(var timestamp of timestamps) {
        var parsedFormula = await parse_formula(formula, data, timestamp);
        var result = eval(parsedFormula);
        dataset.push(result);
    }
    return dataset;
}

/**
 * Setting up all realtime (not simulated) metric elements on the page 
 */ 
async function setUpAllMetricElements() {
    var allMetricElements = $("[class*=realtime_metric]");
    for (var metricElement of allMetricElements) {
        var formula = metricElement.getAttribute("formula");
        var result = await calculate(formula);
        metricElement.innerHTML = result;
    }
}