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


function startSimulation() {
    var left_select = $('#leftAlgorithmSelection')[0];
    var right_select =$('#rightAlgorithmSelection')[0];
    var start = $('#start_time').val();
    var end = $('#end_time').val();
    var startTimestamp = (new Date(start)).getTime();
    var endTimestamp = (new Date(end)).getTime();

    var algorithm = left_select[left_select.selectedIndex].value;
    var simulation = new Simulation(algorithm, startTimestamp, endTimestamp);
    var statusCodes = {
        400: function() {
            alert('400: Unknown optimization algorithm, please edit the Algortihm object\'s backend_identifier field' +
            'at the admin page or contact your system administrator.');
        },
    }
    var req = postSimulationStartRequest(simulation, statusCodes);
    waitForSimulationResults(simulation, req, "left");

    algorithm = right_select[right_select.selectedIndex].value;
    simulation = new Simulation(algorithm, startTimestamp, endTimestamp);
    var statusCodes = {
        400: function() {
            alert('400: Unknown optimization algorithm, please edit the Algortihm object\'s backend_identifier field' +
            'at the admin page or contact your system administrator.');
        },
    }
    req = postSimulationStartRequest(simulation, statusCodes);
    waitForSimulationResults(simulation, req, "right");

}

async function waitForSimulationResults(simulation, req, side) {
    var waitingScreen = (side == 'left') ? $("#waitingScreenLeft") : $("#waitingScreenRight");
    var dataColumn = (side == 'left') ? $("#leftDataColumn") : $("#rightDataColumn");
    var waitingTimeLable = (side == 'left') ? $("#leftWaitingTime") : $("#rightWaitingTime");

    $('#comparisonGraphs').show();
    waitingScreen.show(); 
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
    }, 1000);
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

var comparison_graph_is_set_up = new Map();
async function updateComparisonGraphs(simulated_data, side) {

    var comparison_graphs = $("[class^=cc_]");
    for (var graph of comparison_graphs) { 
        var using_metric = graph.getAttribute("using_metric").replaceAll("[", "").replaceAll("]", "").split(", ");
        var data = graph.getAttribute("data").replaceAll("[", "").replaceAll("]", "").replaceAll("'", "").split(", ");
        if (comparison_graph_is_set_up.get(graph.className) == undefined) {

            var chart_data_set = [];
            var type = graph.getAttribute("type");
    
            
            var values = [];
            var labels = [];
            for (var index in data) {
                if(type == "area" && index == 1) {
                    break;
                } 
    
                if (using_metric[index] == "True") {
                    values.push(await calculate(data[index], simulated_data));
                    labels.push("");
                }
                else {
                    var datapoint = await getDatapoint(data[index]);
                    values.push(parseInt(datapoint["last_value"]));
                    labels.push(datapoint["origin_id"]);
                }
            }
            chart_data_set.push(values);
            comparison_graph_is_set_up.set(graph.className, {
                "left_is_setup" : side == "left",
                "right_is_setup" : side == "right",
                "type" : type,
                "chart_data_set" : chart_data_set,
                "labels" : labels, 
                "graph_labels" : ["left", "right"]
            });
        }
        else {
            var existing_graph = comparison_graph_is_set_up.get(graph.className);
            var existing_graph_data = existing_graph["chart_data_set"];
            var values = [];
            for (var index in data) {
                if(type == "area" && index == 1) {
                    break;
                } 
                
                if (using_metric[index] == "True") {
                    values.push(await calculate(data[index], simulated_data));
                }
                else {
                    var datapoint = await getDatapoint(data[index]);
                    values.push(parseInt(datapoint["last_value"]));
                }
            }

            if (existing_graph["left_is_setup"] && side == "left") {
                existing_graph_data[0] = values;
            }
            else if (existing_graph["left_is_setup"] && side == "right") {
                existing_graph_data.push(values);
                existing_graph["right_is_setup"] = true;
            }
            else if (existing_graph["right_is_setup"] && side == "left") {
                existing_graph_data.unshift(values);
                existing_graph["left_is_setup"] = true;
            }
            else if (existing_graph["right_is_setup"] && side == "right") {
                existing_graph_data[1] = values;
            }
            existing_graph["chart_data_set"] = existing_graph_data;

            if(existing_graph["left_is_setup"] && existing_graph["right_is_setup"]) {
                graph_element = createChart(graph.className, existing_graph["type"], existing_graph_data,  existing_graph["labels"], existing_graph["graph_labels"], "$", data.length);
            }
        }
    }
}
