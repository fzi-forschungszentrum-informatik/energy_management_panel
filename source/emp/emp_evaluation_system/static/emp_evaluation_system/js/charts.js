$( document ).ready(function() {
  setUpAllCharts();
});

async function setUpAllCharts() {
  var allChartElements = $("[class*=chart_realtime]");
  for (var chartElement of allChartElements) {
      setUpChart(chartElement);
  }
}

// Color set for charts. Add new colors here.
var colorSet = ["78, 115, 223", "189, 60, 48", "23, 123, 47"]

/*
  This function is part selfwritten part copied from sb-admin-2 example page.
  It computes all required data to create and print a chart.

*/
function createChart(elementClass, chartType,  datasets,  lables_x, lables_datasets, unit="$", maxTicksLimit=7) {
  var ctx = document.getElementsByClassName(elementClass);
  var range = 0;
  var data = [];
  var barChartHasNegative = false;
  if (chartType == "bar") {
    barChartHasNegative = datasets.flat().map((element) => element < 0).reduce((acc, val) => acc || val);
    var minvalue = barChartHasNegative ? Math.min.apply(Math, datasets.flat()) : 0
    var maxvalue =  Math.max.apply(Math, datasets.flat());
    range = Math.max(maxvalue, Math.abs(minvalue));
    var data = [];
    for (var i = 0; i < datasets.length; i++) {
      var colorOpaque = "rgba("+ colorSet[i] +", 1)";
      var colorTransparent = "rgba("+ colorSet[i] +", 0.5)";
      data.push(
          {
          label: lables_datasets[i],
          backgroundColor: colorOpaque,
          hoverBackgroundColor: colorTransparent,
          borderColor: colorTransparent,
          data: datasets[i],
          }
      )
    }
  }
  else if (chartType == "line") {
    for (var i = 0; i < datasets.length; i++) {
      var colorOpaque = "rgba("+ colorSet[i] +", 1)";
      var colorTransparent = "rgba("+ colorSet[i] +", 0.05)";
      data.push(
          {
          label: lables_datasets[i],
          lineTension: 0,
          backgroundColor: colorTransparent,
          borderColor: colorOpaque,
          pointRadius: 3,
          pointBackgroundColor: colorOpaque,
          pointBorderColor: colorOpaque,
          pointHoverRadius: 3,
          pointHoverBackgroundColor: colorOpaque,
          pointHoverBorderColor: colorOpaque,
          pointHitRadius: 10,
          pointBorderWidth: 2,
          data: datasets[i]
          }
      )
    }
  }
  var graph = new Chart(ctx, {
    type: chartType,
    data: {
      labels: lables_x,
      datasets: data
    },
    options: {
      maintainAspectRatio: false,
      layout: {
        padding: {
          left: 10,
          right: 25,
          top: 25,
          bottom: 0
        }
      },
      scales: {
        xAxes: setUpChartXAxes(chartType, maxTicksLimit),
        yAxes: [{
          ticks: setUpChartTicks(chartType, unit, barChartHasNegative, range),
          gridLines: {
            color: "rgb(234, 236, 244)",
            zeroLineColor: "rgb(234, 236, 244)",
            drawBorder: false,
            borderDash: [2],
            zeroLineBorderDash: [2]
          }
        }],
      },
      legend: {
        display: true
      },
      tooltips: setUpChartTooltips(chartType, unit),
    }
  });
  return graph;
}

function setUpChartXAxes(chartType, maxTicksLimit) {
  var xAxes = [{
    time: {
      unit: 'time'
    },
    gridLines: {
      display: true,
      drawBorder: false
    },
    ticks: {
      maxTicksLimit: maxTicksLimit
    },
  }]
  if (chartType == "bar") {
    xAxes[0].maxBarThickness = 25;
  }
  return xAxes;
}

function setUpChartTicks(chartType, unit="$", hasNegative=false, range=0) {
  var ticks = {
    padding: 10,
    // Include a dollar sign in the ticks
    callback: function(value, index, values) {
      return number_format(value) + ' ' + unit;
    }
  }
  if (chartType == "bar") {
    if (range == 0) {
      console.error("Bar charts need a chart range!");
    }
    else {

      ticks.min = hasNegative ? -range : 0;
      ticks.max = range;
      ticks.maxTicksLimit = 10;
    }
  }
  else if (chartType == "line") {
    ticks.maxTicksLimit = 5;
  }
  return ticks;
}


function setUpChartTooltips(chartType, unit="$") {

  var tooltips = {
    backgroundColor: "rgb(255,255,255)",
    bodyFontColor: "#858796",
    titleMarginBottom: 10,
    titleFontColor: '#6e707e',
    titleFontSize: 14,
    borderColor: '#dddfeb',
    borderWidth: 1,
    xPadding: 15,
    yPadding: 15,
    displayColors: false,
    caretPadding: 10,
    callbacks: {
      label: function(tooltipItem, chart) {
        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
        return datasetLabel + ': ' + number_format(tooltipItem.yLabel) + ' ' + unit;
      }
    }
  }
  if (chartType == "area") {
    tooltips.intersect = false;
    tooltips.mode = 'index';
  }
  return tooltips;
}

var graphs = new Map();

/*
  This function collects all required data to set up a chart and afterwards creats the chart.
  First of all important data is collected.
  Out of this data the remaining required data is computed.
  Afterwards, the chart will be set up and the data is saved for later use.
*/
async function setUpChart(element, data=null) {
  var element_id = element.className;
  var is_area_chart = element_id.includes("area");

  var datapoint_id = element.getAttribute("datapointId");
  var data_types = element.getAttribute("dataTypes").split(", ");
  var data_intervals = element.getAttribute("dataIntervals").split(", ");
  var formula = element_id.includes("metric") ? element.getAttribute("formula") : null;
  
  var actual_interval = data_intervals[0];

  var datapoint = await getDatapoint(datapoint_id);
  var datapoint_lastValue = await getDatapointLastValue(datapoint_id);
  var datapoint_name = datapoint["short_name"]
  var datapoint_unit = datapoint["unit"];

  var graphLabels = data_types.map((type) => datapoint_name.concat(" " + type.charAt(0).toUpperCase() + type.slice(1)));   
  
  chartDataSet = await getChartDataset(datapoint, datapoint_lastValue, data_types, data_intervals, data, formula); 
  var data = [];
  //Reverse Data so that the newest data value comes last in graph.
  data_types.forEach((type)=> {
      var reversedData = chartDataSet.get(type).get(actual_interval).data.reverse();
      data.push(reversedData);  
  });
  var labels = chartDataSet.get(data_types[0]).get(actual_interval).labels;
  var graph = createChart(element_id, is_area_chart ? "line" : "bar", data, labels.reverse() , graphLabels, datapoint_unit, is_area_chart ? (labels.length / 4) : labels.length);

  graphs.set(element_id, {
    "element_id": element_id,
    "graph" : graph,
    "data_set": chartDataSet,
    "type" : is_area_chart ? "line" : "bar",
    "graph_labels" : graphLabels,
    "datapoint_unit" : datapoint_unit,
    "ticks" : is_area_chart ? (labels.length / 4) : labels.length,
  });
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

async function getChartDataset(datapoint, datapoint_lastValue, datasetTypes, dataIntervals, data=null, formula=null) {
  var initialTimestamp = (new Date(datapoint_lastValue["timestamp"])).getTime()
  var lastFullHour = getTimestampOfLastFullHourOf(initialTimestamp);
  var datasetMap = new Map();
  for (var type of datasetTypes) { 
      var map = new Map(); 
      for (var intervalType of dataIntervals) {
          var timestamps = getTimestampsForIntervalType(intervalType, lastFullHour);

          var labels = getTimestampLablesFor(intervalType, timestamps);
          var data_set = []
          if (data == null && formula == null) {
            if(type == "history") {
                for (var timestamp of timestamps) {
                    var json = await getDatapointValueOf(datapoint["id"], timestamp);
                    data_set.push(json.value);
                }
            }
          }
          else if(data != null && formula == null) {
            for (var timestamp of timestamps) {
              var value;
              if(type == "history") {
                  value = data.reduce((acc, object) => acc + ((object["timestamp"] == timestamp) ? parseFloat(object["value"]) : 0), 0);
              }
              data_set.push(value);
            }           
          }
          else {
            if(type == "history") {
              data_set = await calculateMetricDataSet(formula, timestamps, (data != null) ? data : null) ;
            }          
          }
          map.set(intervalType, new Dataset(labels, data_set));
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
  This funciton is called over every chart's dropdown menu.
  It reads the charts data and set the presented data to the selected time interval.
*/
function changeDataIntervalTo(element, intervalType) {
  var identifier = element.parentElement.parentElement.parentElement.parentElement.getElementsByClassName("card-body")[0].getElementsByClassName("chart-area")[0].getElementsByTagName("canvas")[0].classList[0];

  var graphInfo = graphs.get(identifier);
  
  graphInfo["graph"].destroy();

  var data = []

  var reversedData = graphInfo["data_set"].get("history").get(intervalType).data;
  data.push(reversedData);  

  var labels = graphInfo["data_set"].get("history").get(intervalType).labels;

  var graph = createChart(graphInfo["element_id"], graphInfo["type"], data, labels , graphInfo["graph_labels"], graphInfo["datapoint_unit"], graphInfo["ticks"]);
  
  
  graphs.delete(identifier);
  graphs.set(identifier, {
    "element_id": identifier,
    "graph" : graph,
    "data_set": graphInfo["data_set"],
    "type" : graphInfo["type"],
    "graph_labels" : graphInfo["graph_labels"],
    "datapoint_unit" : graphInfo["datapoint_unit"], 
    "ticks" : graphInfo["ticks"],
  })
}



/*
  This function was copied out of sb-admin-2 example page.
  The function formats numbers for better use in charts.
*/
function number_format(number, decimals, dec_point, thousands_sep) {
    // *     example: number_format(1234.56, 2, ',', ' ');
    // *     return: '1 234,56'
    number = (number + '').replace(',', '').replace(' ', '');
    var n = !isFinite(+number) ? 0 : +number,
      prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
      sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
      dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
      s = '',
      toFixedFix = function(n, prec) {
        var k = Math.pow(10, prec);
        return '' + Math.round(n * k) / k;
      };
    // Fix for IE parseFloat(0.55).toFixed(0) = 0;
    s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
    if (s[0].length > 3) {
      s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '').length < prec) {
      s[1] = s[1] || '';
      s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
  }