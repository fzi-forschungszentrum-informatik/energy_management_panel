/*
    This file only defines api calls to the EMP API.
    The api calls should speak for them self.

    Every function returns the Promise received of the API call. 
    The Promise hold the requested JSON.

    These funtions will be used in other files.
*/

var datapoint_api_url = "http://localhost:8000/api/datapoint/";

function getDatapoint(datapointId) {
    return $.getJSON(datapoint_api_url + datapointId);
}
function getDatapointValues(datapointId) {
    return $.getJSON(datapoint_api_url + datapointId + "/value/");
}

function getDataPointSetpoints(datapointId) {
    return $.getJSON(datapoint_api_url + datapointId + "/schedule/");
}

function getDataPointSchedules(datapointId) {
    return $.getJSON(datapoint_api_url + datapointId + "/schedule/");
}

function getDatapointValueOf(datapointId, timestamp) {
    return $.getJSON(datapoint_api_url + datapointId + "/value/" + timestamp + "/");
}

function getDataPointSetpointsOf(datapointId, timestamp) {
    return $.getJSON(datapoint_api_url + datapointId + "/setpint/" + timestamp + "/");
}

function getDataPointSchedulesOf(datapointId, timestamp) {
    return $.getJSON(datapoint_api_url + datapointId + "/schedule/" + timestamp + "/");
}

var simulation_api_url = "http://localhost:8018/"

function postSimulationStartRequest(data, statusCodes) {
    return $.ajax({
        type: "POST",
        dataType: "json",
        url: simulation_api_url + "simulation/request/"+data.string,
        statusCode: statusCodes,
        accepts: {          
            text: "application/json", 
          }
    });
}

function getSimulationStatus(simulation_name, data, statusCodes) {
    return $.ajax({
        dataType: "json",
        url: simulation_api_url + simulation_name + "/simulation/status/",
        data: data,
        statusCode: statusCodes,
    });
}

function getSimulationResult(simulation_name, data, statusCodes) {
    return $.ajax({
        dataType: "json",
        url: simulation_api_url + simulation_name + "/simulation/result/",
        data: data,
        statusCode: statusCodes,
    });
}
