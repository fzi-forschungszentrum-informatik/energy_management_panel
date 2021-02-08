/*
    This file defines different funcitons all with the goal to ease the work with datapoints,
    their values and timestamps and their api calls.
*/



function getLastDatapointValueOfSet(set) {
    return set[Object.keys(set).length - 1].value
}

/*
    Defining different time units in milliseconds.
    These are used to claculate timestamps.
*/
var minuteInMillisec = 60000;
var hourInMillisec = minuteInMillisec * 60;
var dayInMillisec = hourInMillisec * 24;
var weekInMillisec = dayInMillisec * 7;
var monthInMillisec = dayInMillisec * 30;


/*
    The following functions return an array of n timestamps each in a time interval specified in the method name.
    All these functions work in the same way: 
        - Create an array of the length n
        - Map this array on the specified function. This results in an array consisiting of the requested values.
*/
function getLastHours(timestamp, n) {
    return Array.from({length:n},(v,k)=>k).map((x) => timestamp - hourInMillisec * x)
}

function getLastDays(timestamp, n) {
    return Array.from({length:n},(v,k)=>k).map((x) => timestamp - dayInMillisec * x)
}

function getLastWeeks(timestamp, n) {
    return Array.from({length:n},(v,k)=>k).map((x) => timestamp - weekInMillisec * x)
}

function getLastMonth(timestamp, n) {
    return Array.from({length:n},(v,k)=>k).map((x) => timestamp - monthInMillisec * x)
}

/*
    This function takes a timstamp and returns the timestamp that represents the last full hour.

    Since an hourly interval is the lowest time interval to monitor data that we offer, 
    the last full hour is the startpoint for every timestamp calculation.
*/
function getTimestampOfLastFullHourOf(timestamp) {
    var timestampDate = new Date(timestamp);
    timestampDate.setMilliseconds(0);
    timestampDate.setSeconds(0);
    timestampDate.setMinutes(0);
    return timestampDate.getTime();
}

/*
    Takes a interval type and a starting timestamp and returns the last n timestamps of the given time interval type.
*/
function getTimestampsForIntervalType(type, timestamp) {
    switch(type) {
        case "hourly":
            return getLastHours(timestamp, 24);
        case "daily":
            return getLastDays(timestamp, 7);
        case "weekly":
            return getLastWeeks(timestamp, 4);
        case "monthly":
            return getLastMonth(timestamp,12);
        default:
            console.error("No such time interval type.");
            break
    }
}

/*
    Takes a interval type and an array of timestamps and returns an array of labels constucted out of these timestamps.
    These labels are used as axis abels of a chart.
*/
function getTimestampLablesFor(type, timestampset) {
    switch(type) {
        case "hourly":
            return timestampset.map((timestamp) => new Date(timestamp).getHours().toString().concat(":00"))
        case "daily":
            return timestampset.map((timestamp) => new Date(timestamp).getDate().toString().concat(".").concat((new Date(timestamp).getMonth()+1).toString()))
        case "weekly":
            return timestampset.map((timestamp) => new Date(timestamp).getDate().toString().concat(".").concat((new Date(timestamp).getMonth()+1).toString()))
        case "monthly":
            return timestampset.map((timestamp) => new Date(timestamp).getDate().toString().concat(".").concat((new Date(timestamp).getMonth()+1).toString()))
        default:
            console.error("No such time interval type.");
            break
    }
}

function usesOnOffValue(datapoint) {
    return (datapoint["data_format"] == "discrete_numeric") && ((datapoint["allowed_values"] == "[0,1]") || (datapoint["allowed_values"] == "[0, 1]"));
}

function onOfValueToText(value) {
    return Boolean(parseInt(value))
}
