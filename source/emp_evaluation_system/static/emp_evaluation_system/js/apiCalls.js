// The API endpoint for datapoint queries.
var datapoint_api_url = "http://localhost:8000/api/datapoint/";

/**
 * Calls the datapoint API, requests and returns a datapoint JSON object.
 * @param {*} datapointId The id of the requested datapoint object
 */
function getDatapoint(datapointId) {
    return $.getJSON(datapoint_api_url + datapointId);
}

function getDatapointLastValue(datapointId) {
    return $.getJSON(datapoint_api_url + datapointId + "/last_value/");
}

/**
 * Calls the datapoint API, requests and returns the value of a datapoint object.
 * @param {*} datapointId The id of the requested datapoint 
 */
function getDatapointValues(datapointId) {
    return $.getJSON(datapoint_api_url + datapointId + "/value/");
}

/**
 * Calls the datapoint API, requests and returns the setpoint of a datapoint object.
 * @param {*} datapointId The id of the requested datapoint 
 */
function getDataPointSetpoints(datapointId) {
    return $.getJSON(datapoint_api_url + datapointId + "/setpoint/");
}

/**
 * Calls the datapoint API, requests and returns the schedule of a datapoint object.
 * @param {*} datapointId The id of the requested datapoint
 */
function getDataPointSchedules(datapointId) {
    return $.getJSON(datapoint_api_url + datapointId + "/schedule/");
}

/**
 * Calls the datapoint API, requests and returns the value of a datapoint object to a specified timestamp.
 * @param {*} datapointId The id of the requested datapoint 
 * @param {*} timestamp The timestamp of the requested value
 */
function getDatapointValueOf(datapointId, timestamp) {
    return $.getJSON(datapoint_api_url + datapointId + "/value/" + timestamp + "/");
}

/**
 * Calls the datapoint API, requests and returns the setpoint of a datapoint object to a specified timestamp.
 * @param {*} datapointId The id of the requested datapoint 
 * @param {*} timestamp The timestamp of the requested setpoint
 */
function getDataPointSetpointsOf(datapointId, timestamp) {
    return $.getJSON(datapoint_api_url + datapointId + "/setpoint/" + timestamp + "/");
}

/**
 * Calls the datapoint API, requests and returns the schedule of a datapoint object to a specified timestamp.
 * @param {*} datapointId The id of the requested datapoint 
 * @param {*} timestamp The timestamp of the requested schedule
 */
function getDataPointSchedulesOf(datapointId, timestamp) {
    return $.getJSON(datapoint_api_url + datapointId + "/schedule/" + timestamp + "/");
}

// The API endpoint for simulation queries
var simulation_api_url = "http://localhost:8018/"

/**
 * Posts a simulation start request to the simulation API. 
 * @param {*} data The data for the requested simulation in the following form: '?scenario_name=name&from_ts=from&to_ts=to'
 * @param {*} statusCodes A JSON object thtat specifies a funciton for each specified status code. These funcitons will be called if status code is thrown in response.
 */
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

/**
 * Requests a simulation status from the simulation API.
 * Returns a JSON object like the following:
 * {
 *  "percent complete": 100,
 *  "ETA seconds": 0
 *  } 
 * @param {*} data The data for the requested simulation stauts in the following form: 
 *        { 
 *          "scenario_name": name,
 *          "from_ts": start, 
 *          "to_ts": end,
 *        }
 * @param {*} statusCodes A JSON object thtat specifies a funciton for each specified status code. These funcitons will be called if status code is thrown in response.
 */
function getSimulationStatus(simulation_name, data, statusCodes) {
    return $.ajax({
        dataType: "json",
        url: simulation_api_url + simulation_name + "/simulation/status/",
        data: data,
        statusCode: statusCodes,
    });
}

/**
 * Requests a simulation result from the simulation API.
 * Returns a JSON object like that contains entries for each data type (values, setpoints, schedules).
 * In each these entries there is anbother entry for each datapoint that contains an array of ALL simulated values (value and timestamp)
 * @param {*} data The data for the requested simulation result in the following form: 
 *        { 
 *          "scenario_name": name,
 *          "from_ts": start, 
 *          "to_ts": end,
 *        }
 * @param {*} statusCodes A JSON object thtat specifies a funciton for each specified status code. These funcitons will be called if status code is thrown in response.
 */
function getSimulationResult(simulation_name, data, statusCodes) {
    return $.ajax({
        dataType: "json",
        url: simulation_api_url + simulation_name + "/simulation/result/",
        data: data,
        statusCode: statusCodes,
    });
}
