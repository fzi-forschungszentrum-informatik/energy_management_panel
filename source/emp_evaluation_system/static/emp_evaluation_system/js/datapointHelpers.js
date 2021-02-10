/**
 * Takes a map of datapoints and returns the value of the last datapoint.
 * @param {*} map map of datapoints
 */
function getLastDatapointValueOfSet(map) {
    return map[Object.keys(map).length - 1].value
}

/*
    Defining different time units in milliseconds.
    These are used to claculate timestamps.
*/
var minuteInMillisec = 60000;
var hourInMillisec = minuteInMillisec * 60;
var dayInMillisec = hourInMillisec * 24;
var weekInMillisec = dayInMillisec * 7;
//TODO Month can have from 28 to 31 days. Therefore 30 days is not accurate.
var monthInMillisec = dayInMillisec * 30;



/**
 * Takes and timestamp and an number n and returns the last n hours calculated of the given timestamp as array.
 * @param {*} timestamp starting timestamp
 * @param {*} n number of hours
 */
function getLastHours(timestamp, n) {
    return Array.from({length:n},(v,k)=>k).map((x) => timestamp - hourInMillisec * x)
}

/**
 * Takes and timestamp and an number n and returns the last n days calculated of the given timestamp as array.
 * @param {*} timestamp starting timestamp
 * @param {*} n number of days
 */
function getLastDays(timestamp, n) {
    return Array.from({length:n},(v,k)=>k).map((x) => timestamp - dayInMillisec * x)
}

/**
 * Takes and timestamp and an number n and returns the last n weeks calculated of the given timestamp as array.
 * @param {*} timestamp starting timestamp
 * @param {*} n number of weeks
 */
function getLastWeeks(timestamp, n) {
    return Array.from({length:n},(v,k)=>k).map((x) => timestamp - weekInMillisec * x)
}

/**
 * Takes and timestamp and an number n and returns the last n months calculated of the given timestamp as array.
 * @param {*} timestamp starting timestamp
 * @param {*} n number of months
 */
function getLastMonth(timestamp, n) {
    return Array.from({length:n},(v,k)=>k).map((x) => timestamp - monthInMillisec * x)
}

/**
 * Takes a timstamp and returns the timestamp that represents the last full hour.
 * @param {*} timestamp timestamp to calculate the last full hour from.
 */
function getTimestampOfLastFullHourOf(timestamp) {
    var timestampDate = new Date(timestamp);
    timestampDate.setMilliseconds(0);
    timestampDate.setSeconds(0);
    timestampDate.setMinutes(0);
    return timestampDate.getTime();
}

/*
    
*/
/**
 * Takes a interval type and a starting timestamp and returns the last n timestamps of the given time interval type.
 * @param {*} type The interval type ('hourly', 'daily', 'weekly', 'monthly')
 * @param {*} timestamp The first timestamp
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
    
    These labels are used as axis abels of a chart.
*/
/**
 * Takes a interval type and an array of timestamps and returns an array of labels as Strings constucted out of these timestamps.
 * @param {*} type The interval type ('hourly', 'daily', 'weekly', 'monthly')
 * @param {*} timestampset The timestamps as array to create the labels of.
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

/**
 * Takes a JSON object of a datapoint and returns whether the datapoints uses on/off values (discret numeric values that only may be set as 0 or 1).
 * @param {*} datapoint The datapoint to check.
 */
function usesOnOffValue(datapoint) {
    return (datapoint["data_format"] == "discrete_numeric") && ((datapoint["allowed_values"] == "[0,1]") || (datapoint["allowed_values"] == "[0, 1]"));
}

/**
 * Takes an numeric value as String an calculates the boolean value of it. 0 Turns into Falso, everything else into True
 * @param {*} value The value to convert
 */
function onOfValueToText(value) {
    return Boolean(parseInt(value))
}
