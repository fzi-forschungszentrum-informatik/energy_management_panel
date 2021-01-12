function getDatapointValues(datapointId) {
    return $.getJSON("http://localhost:8000/api/datapoint/"+datapointId+"/value/");
}

function getDataPointSetpoints(datapointId) {
    return $.getJSON("http://localhost:8000/api/datapoint/"+datapointId+"/schedule/");
}

function getDataPointSchedules(datapointId) {
    return $.getJSON("http://localhost:8000/api/datapoint/"+datapointId+"/schedule/");
}
