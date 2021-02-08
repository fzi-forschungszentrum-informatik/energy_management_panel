function sum(arr) {
    return arr.reduce((acc, val) => acc + val, 0);
}

function mean(arr) {
    return (sum(arr) / arr.length).toFixed(3);
}

var origEval = eval;

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
    if(formula.includes("sum") || formula.includes("mean")) {
        if(datapointStrings.length != 1) return "0"
        var match = datapointStrings[0].match("\\d");
        var datapoint = await getDatapoint(match);
        //TODO Error if datapoint is on/off
        var datapoints = [];
        var values = [];
        if (data == null && timestamp == null) {
            datapoints = await getDatapointValues(match);
        }
        else if (data != null && timestamp == null) {
            datapoints = data[datapoint["origin_id"]];
        }
        else {
            //TODO Error message
            console.error("This is not possible");
        }

        for (var datapoint of datapoints) {
            values.push(datapoint.value);
        }
        output = output.replace(datapointStrings[0], "["+ values.toString() +"]")
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

async function calculate(formula, data=null){
    var parsedFormula = await parse_formula(formula, data);
    var result = eval(parsedFormula);
    return result;
}

async function calculateMetricDataSet(formula, timestamps, data=null) {
    var dataset = [];
    for(var timestamp of timestamps) {
        var parsedFormula = await parse_formula(formula, data, timestamp);
        var result = eval(parsedFormula);
        dataset.push(result);
    }
    return dataset;
}

async function setUpAllMetricElements() {
    var allMetricElements = $("[class*=realtime_metric]");
    for (var metricElement of allMetricElements) {
        var formula = metricElement.getAttribute("formula");
        var result = await calculate(formula);
        metricElement.innerHTML = result;
    }
}