function getLastDatapointValueOfSet(set) {
    return set[Object.keys(set).length - 1].value
}

function getLastDatapointTimestampOfSet(set) {
    return set[Object.keys(set).length - 1].timestamp
}

function getLastXDatapointValuesOfSet(set, x) {
    var filteredSet = set.filter(function(el, index) {
        return index >= set.length - x;
    });
    return $.map(filteredSet, (n) => n.value);   
}

function getLastDatapointTimestampOf(datapointId) {
    getDatapointValues(datapointId).then((data) => { return getLastDatapointTimestampOf(data) })
}

var minuteInMillisec = 60000;
var hourInMillisec = minuteInMillisec * 60;
var dayInMillisec = hourInMillisec * 24;
var weekInMillisec = dayInMillisec * 7;

function getLast24Hours(timestamp) {
    //Get array from 0 to 23 and multiply these values with hourInMillisec and subtract timestamp
    return Array.from({length:24},(v,k)=>k).map((n) => timestamp - hourInMillisec * n)
}

function getLast7Days(timestamp) {
    return Array.from({length:7},(v,k)=>k).map((n) => timestamp - dayInMillisec * n)
}

function getLast4Weeks(timestamp) {
    return Array.from({length:4},(v,k)=>k).map((n) => timestamp - weekInMillisec * n)
}

function getTimestampOfLastFullHour() {
    return getTimestampOfLastFullHourOf(Date.now());
}

function getTimestampOfLastFullHourOf(timestamp) {
    var timestampDate = new Date(timestamp);
    timestampDate.setMilliseconds(0);
    timestampDate.setSeconds(0);
    timestampDate.setMinutes(0);
    return timestampDate;
}

function getTimestampOfLastFullDayOf(timestamp) {
    var timestampDate = new Date(timestamp);
    timestampDate.setMilliseconds(0);
    timestampDate.setSeconds(0);
    timestampDate.setMinutes(0);
    timestampDate.setHours(0);
    return timestampDate;
}
