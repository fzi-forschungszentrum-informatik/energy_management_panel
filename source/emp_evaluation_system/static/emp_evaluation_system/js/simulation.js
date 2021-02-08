class Simulation {
    constructor(name, start, end) {
        this.name = name;
        this.start = start;
        this.end = end;
    }

    get string() {
        return this.asString();
    }

    asString() {
        return "?scenario_name=" + this.name + "&from_ts=" + this.start + "&to_ts=" + this.end;
    }
    get data() {
        return this.asData();
    }

    get dataWithoutName() {
        return this.asDataWithoutName();
    }

    asData() {
        return {
            "scenario_name": this.name,
            "from_ts": this.start, 
            "to_ts": this.end,
        }
    }

    asDataWithoutName() {
        return {
            "from_ts": this.start, 
            "to_ts": this.end,
        }
    }
}

function onAlgorithmSelectChange(element, side) {
    var algorithm = element[element.selectedIndex].value;
    var start = $('#start_time').val();
    var end = $('#end_time').val();
    var startTimestamp = (new Date(start)).getTime();
    var endTimestamp = (new Date(end)).getTime();
    var simulation = new Simulation(algorithm, startTimestamp, endTimestamp);
    var statusCodes = {
        400: function() {
            alert('400: Unknown optimization algorithm, please edit the Algortihm object\'s backend_identifier field' +
            'at the admin page or contact your system administrator.');
        },
    }
    var req = postSimulationStartRequest(simulation, statusCodes);
    waitForSimulationResults(simulation, req, side);
}

async function waitForSimulationResults(simulation, req, side) {
    var noAlgorithmScreen = (side == 'left') ? $("#noAlgorithmScreenLeft") : $("#noAlgorithmScreenRight");
    var waitingScreen = (side == 'left') ? $("#waitingScreenLeft") : $("#waitingScreenRight");
    var canlceButton = (side == 'left') ? $("#btnCancleLeft") : $("#btnCancleRight");
    var dataColumn = (side == 'left') ? $("#leftDataColumn") : $("#rightDataColumn");
    var waitingTimeLable = (side == 'left') ? $("#leftWaitingTime") : $("#rightWaitingTime");
    
    noAlgorithmScreen.hide();
    $('#comparisonGraphs').show();
    waitingScreen.show();
    canlceButton.click(() => req.abort());
    dataColumn.hide(); 
    var waitingInterval = setInterval(() => {
            getSimulationStatus(simulation.name, simulation.dataWithoutName, {}).then((result) => {
                if(result["percent complete"] != 100) {
                    waitingTimeLable.html(result["ETA seconds"]);
                }
                else {
                    clearInterval(waitingInterval);
                    waitingScreen.hide();
                    dataColumn.show();
                    updateUiElements(simulation, side);
                }
            })
    }, 10000);
}

async function updateUiElements(simulation, side) {
    var json = await getSimulationResult(simulation.name, simulation.dataWithoutName, {});
    
    var values = json["values"];

    updateComparisonPage(values, side);
}

async function updateComparisonPage(values, side) {
    updateComparisonPageValueElements(values, side);
    updateComparisonPageMetricElements(values, side);
    updateComparisonGraphs(values, side);
}

async function updateComparisonPageValueElements(values, side) {
    var value = "N/A";
    for (var valueName in values) {
        var element = $('.dp_' + valueName + "_simulated_value_" + side);

        if (element.length) {
            value = values[valueName][values[valueName].length - 1]["value"];
            element[0].textContent = value;
        }       
        element = $('[class^=dp_' + valueName +'][class$='+ "chart_simulated_value_" + side +']');
        if (element.length) {
            await setUpChart(element[0], values[valueName]);
        }
    }
}

async function updateComparisonPageMetricElements(values, side) {
    var value = "N/A";

    var metric_elements = $('[class^=mt_][class$='+ "simulated_metric_" + side +']');
    for (var metric_element of metric_elements) {
        if(!metric_element.className.includes("chart")) {
            value = await calculate(metric_element.getAttribute("formula"), values);
            metric_element.textContent = value;
        }
    }

    metric_elements = $('[class^=mt_][class$='+ "chart_simulated_metric_" + side +']');
    for (var metric_element of metric_elements) {
        await setUpChart(metric_element, values);
    }
}

async function updateComparisonGraphs(values, side) {

}
