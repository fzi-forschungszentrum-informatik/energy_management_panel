/**
*  The Simulation class serves as data container for important simulation request data.
*  It holds the simulations backend identifier as name, and the simulations start and end timestamp.
*/
class Simulation {
    constructor(name, start, end) {
        this.name = name;
        this.start = start;
        this.end = end;
    }

    get string() {
        return this.asString();
    }

    // Creates and returns a String out of the class fields. This string is used for api calls.
    asString() {
        return "?scenario_name=" + this.name + "&from_ts=" + this.start + "&to_ts=" + this.end;
    }
    get data() {
        return this.asData();
    }

    get dataWithoutName() {
        return this.asDataWithoutName();
    }

    // Creates and returns a JSON object that holds all class fields.
    asData() {
        return {
            "scenario_name": this.name,
            "from_ts": this.start, 
            "to_ts": this.end,
        }
    }

    //Creatses and returns a JSON object of all class fields expect the name.
    asDataWithoutName() {
        return {
            "from_ts": this.start, 
            "to_ts": this.end,
        }
    }
}

/**
 * This function is used as onlick function for the #btn_settings button at the algorithm_selection_form.
 * The function collects all required data that is needed to post a algorithm simulation request.
 * Afterwards, the simulation request is posted and a cyclic waiting and update thread is started.
 *  This function starts simulations for the left AND the right data column at the comparison page.
 */
function startSimulation() {
    var left_select = $('#leftAlgorithmSelection')[0];
    var right_select =$('#rightAlgorithmSelection')[0];
    var start = $('#start_time').val();
    var end = $('#end_time').val();
    var startTimestamp = (new Date(start)).getTime();
    var endTimestamp = (new Date(end)).getTime();
    var right_algorithm = right_select[right_select.selectedIndex].value;
    var left_algorithm = left_select[left_select.selectedIndex].value;

    if (right_algorithm == left_algorithm) {
        showError("Please select two different algorithms!");
    }
    else if (endTimestamp < startTimestamp) {
        showError("Please select an end time that is after the starting time!")
    }
    else if (startTimestamp == endTimestamp) {
        showError("Start and end time can not be the same. Please select two different times");
    }
    else {
        var simulation = new Simulation(left_algorithm, startTimestamp, endTimestamp);
        var statusCodes = {
            400: function() {
                showError("There was an error while computing your simulation data. Please try again with other input or contact your system administrator!")
            },
        }
        postSimulationStartRequest(simulation, statusCodes);
        waitForSimulationResults(simulation, "left");

        simulation = new Simulation(right_algorithm, startTimestamp, endTimestamp);

        postSimulationStartRequest(simulation, statusCodes);
        waitForSimulationResults(simulation, "right");
    }
}

/**
* This function starts a cyclic waiting interval. 
* On each interval tick the simulaiton API is called and active simulation status is requested.
* If the request is finished the funciton to update the UI with the simulation data is called.
* Else the ETA label is updateded and the interval continues.
* @param {*} simulation Takes a simulation object that holds all important data.
* @param {*} side Takes a side ('left' or 'right') to distinguish between the different simulated sites.
*/
async function waitForSimulationResults(simulation, side) {
    var waitingScreen = (side == 'left') ? $("#waitingScreenLeft") : $("#waitingScreenRight");
    
    var waitingTimeLable = (side == 'left') ? $("#leftWaitingTime") : $("#rightWaitingTime");

   
    waitingScreen.show(); 
    var waitingInterval = setInterval(() => {
            getSimulationStatus(simulation.name, simulation.dataWithoutName, {}).then((result) => {
                if(result["percent complete"] != 100) {
                    waitingTimeLable.html(result["ETA seconds"]);
                }
                else {
                    clearInterval(waitingInterval);
                    waitingScreen.hide();
                    updateUiElements(simulation, side);
                }
            })
    }, 1000);
}


/**
 * This funciton is used as container function. 
 * Simulation result data will be requested and each possible UI element will be updated.
 * @param {*} simulation Takes a simulation object that holds all important data.
 * @param {*} side Takes a side ('left' or 'right') to distinguish between the different simulated sites.
 */
async function updateUiElements(simulation, side) {
    var json = await getSimulationResult(simulation.name, simulation.dataWithoutName, {});
    
    var values = json["values"];
    console.log(values)
    updateComparisonPageValueElements(values, side);
    updateComparisonPageMetricElements(values, side);
    updateComparisonGraphs(values, side);
}

/*
    This function updates simulated values in cards and charts.
*/
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
    var dataColumn = (side == 'left') ? $("#leftDataColumn") : $("#rightDataColumn");
    dataColumn.show();
}

/*
    This function updates simulated metrics in cards and charts.
*/
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
    var dataColumn = (side == 'left') ? $("#leftDataColumn") : $("#rightDataColumn");
    dataColumn.show();
}


var comparison_graph_data = new Map();

//Set up JSON objects for every comparison graph. This is used to avoid undfined values later on
$( document ).ready(function() {
    var comparison_graphs = $("[class^=cc_]");
    for (var graph of comparison_graphs) {  
        comparison_graph_data.set(graph.className, {
            "left_data_set" : null,
            "right_data_set" : null,
            "graph_labels" : null,
            "graph_element" : null
        })
    }
});

/*
    This function updates ALL comparison graphs with the given simulated data results and a side.
    First of all every required data point and value is collected. This data will be stored in the comparison_graph_data map.
    A comparison graph will only be set up if there is data for the left AND the right algorithm simulation available.
    Therefore, it is checked if the other side already computed the required data.
    If the data is computed a graph will be set up.
*/
async function updateComparisonGraphs(simulated_data, side) {

    var comparison_graphs = $("[class^=cc_]");
    for (var graph of comparison_graphs) { 
        var using_metric = graph.getAttribute("using_metric").replaceAll("[", "").replaceAll("]", "").split(", ");
        var data = graph.getAttribute("data").replaceAll("[", "").replaceAll("]", "").replaceAll("'", "").split(", ");
       
        var type = graph.getAttribute("type");
        
        var values = [];
        var labels = [];
        for (var index in data) {
            if(type == "area") {
                if (index >= 1) break; 
                if(using_metric[index] == "True") {
                    showError("You or your system admin used a metric inside an area comparison graph. This is not possivble. Please fix that or contact your system administrator!");
                }
                else {
                    var datapoint = await getDatapoint(data[index]);
                    var datapoint_origin_id = datapoint["origin_id"];
                    var first_timestamp = simulated_data[datapoint_origin_id][0]["timestamp"]
                    var last_timestamp = simulated_data[datapoint_origin_id][simulated_data[datapoint_origin_id].length - 1]["timestamp"];

                    var step_cout = 20;
                    var step_size = (last_timestamp - first_timestamp) / step_cout;
                    var timestamps = [];
                    timestamps = getTimestampsForIntervalType("hourly", last_timestamp);
                    /*for (var i = 0; i < step_cout; i++) {
                        timestamps.push(first_timestamp + i * step_size);
                    }*/
                    
                    for (var timestamp of timestamps) {
                        values.push(simulated_data[datapoint_origin_id].reduce((acc, object) => acc + ((object["timestamp"] == timestamp) ? parseFloat(object["value"]) : 0), 0));
                    }
                    labels = getTimestampLablesFor("hourly", timestamps)
                }
            }
            else {
                if (using_metric[index] == "True") {
                    values.push(await calculate(data[index], simulated_data));
                    labels.push(data[index]);
                }
                else {
                    var datapoint = await getDatapoint(data[index]);
                    var datapoint_origin_id = datapoint["origin_id"];
                    var value = simulated_data[datapoint_origin_id][simulated_data[datapoint_origin_id].length - 1]["value"];
                    values.push(value);
                    labels.push(datapoint["origin_id"]);
                }
            }
        }
        var graph_identifier = graph.classList[0];
        var left_data_set = comparison_graph_data.get(graph_identifier)["left_data_set"];
        var right_data_set = comparison_graph_data.get(graph_identifier)["right_data_set"];
        var graph_labels = comparison_graph_data.get(graph_identifier)["graph_labels"];
        var graph_element = comparison_graph_data.get(graph_identifier)["graph_element"]
        
        comparison_graph_data.set(graph_identifier, {
            "left_data_set" : (side == 'left') ? values : left_data_set,
            "right_data_set" : (side == 'right') ? values : right_data_set,
            "graph_labels" : (graph_labels != null) ? graph_labels : labels,
            "graph_element" : graph_element,
        })
        
        
        //update the value of these variables because one of them has changed.
        left_data_set = comparison_graph_data.get(graph_identifier)["left_data_set"];
        right_data_set = comparison_graph_data.get(graph_identifier)["right_data_set"];
        graph_labels = comparison_graph_data.get(graph_identifier)["graph_labels"];

        if(left_data_set != null && right_data_set != null) {
            var graph_data =  [];
            graph_data.push(left_data_set);
            graph_data.push(right_data_set);
            if (graph_element != null) graph_element.destroy();
            if(type == "area") {
                graph_element = createChart(graph_identifier, "line", graph_data,  graph_labels, ["first", "second", "thrid"], "W");
            }
            else {
                graph_element = createChart(graph_identifier, "bar", graph_data,  graph_labels, ["first", "second", "thrid"]);
            }
            comparison_graph_data.set(graph_identifier, {
                "left_data_set" : left_data_set,
                "right_data_set" : right_data_set,
                "graph_element" : graph_element,
            })
            $('#comparisonGraphs').show();
        }
        
    }
}
