function sum(arr) {
    return arr.reduce((acc, val) => acc + val, 0);
}

function mean(arr) {
    return (sum(arr) / arr.length).toFixed(3);
}

var origEval = eval;

async function parse_formula(formula) {
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
        var jsonArr = await getDatapointValues(match);
        var values = [];
        for (var json of jsonArr) {
            values.push(json.value);
        }
        output = output.replace(datapointStrings[0], "["+ values.toString() +"]")
    }
    else {
        for (var datapointString of datapointStrings) {
            var match = datapointString.match("\\d");
            var json = await getDatapoint(match);
            var value = json["last_value"]
            output = output.replace(datapointString, value)
        }
    }
    return output 
}

async function calculate(formula, element){
    var parsedFormula = await parse_formula(formula);
    var result = eval(parsedFormula);
    $(element).html(result);
}