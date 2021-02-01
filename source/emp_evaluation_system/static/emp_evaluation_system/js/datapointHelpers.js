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
Constructs a Map of chart datasets out of a datapoint id, an initial timestamp, 
the data set types (e.g. history, forecast...) 
and the data intervals (e.g hourly, daily,...).
After Construction a obect scructure looks like the following example

ChartDataset:Map
    | "history"
        | "hourly" : Dataset
        | "daily" : Dataset 
    | "forecast"
        | "hourly" : Dataset
        | "daily" : Dataset 
    | "schedule"
        | "hourly" : Dataset
        | "daily" : Dataset 

Each Dataset contains x-axis labels and data values to print a chart
*/

async function getChartDataset(datapointId, initialTimestamp, datasetTypes, dataIntervals) {
        var lastFullHour = getTimestampOfLastFullHourOf(initialTimestamp);
        var datasetMap = new Map();
        for (var type of datasetTypes) { 
            var map = new Map(); 
            for (var intervalType of dataIntervals) {
                var timestamps = getTimestampsForIntervalType(intervalType, lastFullHour);
                var labels = getTimestampLablesFor(intervalType, timestamps);
                var data = []
                //API call for every datapoint/timestamp needed
                if(type == "history") {
                    for (var timestamp of timestamps) {
                        var json = await getDatapointValueOf(datapointId, timestamp);
                        data.push(json.value);
                    }
                }
                //TODO Include this when data is ready
                /*else if (type == "setpoints") {
                    timestamps.forEach((timestamp) => {
                        getDataPointSetpointsOf(datapointId, timestamp).then((result) => data.push(result.value))
                    });
                }
                else if (type == "schedule") {
                    timestamps.forEach((timestamp) => {
                        getDataPointSchedulesOf(datapointId, timestamp).then((result) => data.push(result.value))
                    });
                }*/
                map.set(intervalType, new Dataset(labels, data));
            }  
            datasetMap.set(type, map);
        }
        return datasetMap;
    
}

/*
    Simple data container class consistion of thwo arrays.
*/
class Dataset {
    constructor(labels, data) {
        this.labels = labels;
        this.data = data;
    }  
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
            //TODO Implement
            console.error("Monthly Interval not implemented yet");
            break;
        case "yearly":
            console.error("Yearly Interval not implemented yet");
            break;
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
            //return getLast4Weeks(timestamp);
        case "monthly":
            //TODO Implement
            console.error("Monthly Interval not implemented yet");
            break;
        case "yearly":
            console.error("Yearly Interval not implemented yet");
            break;
        default:
            console.error("No such time interval type.");
            break
    }
}
