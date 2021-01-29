/*
    This file only defines api calls to the EMP API.
    The api calls should speak for them self.

    Every function returns the Promise received of the API call. 
    The Promise hold the requested JSON.

    These funtions will be used in other files.
*/

var apiUrl = "http://localhost:8000/api/datapoint/";
function getDatapointValues(datapointId) {
    return $.getJSON(apiUrl+datapointId+"/value/");
}

function getDataPointSetpoints(datapointId) {
    return $.getJSON(apiUrl+datapointId+"/schedule/");
}

function getDataPointSchedules(datapointId) {
    return $.getJSON(apiUrl+datapointId+"/schedule/");
}

function getDatapointValueOf(datapointId, timestamp) {
    return $.getJSON(apiUrl+datapointId+"/value/"+timestamp+"/");
}

function getDataPointSetpointsOf(datapointId, timestamp) {
    return $.getJSON(apiUrl+datapointId+"/setpint/"+timestamp+"/");
}

function getDataPointSchedulesOf(datapointId, timestamp) {
    return $.getJSON(apiUrl+datapointId+"/schedule/"+timestamp+"/");
}

