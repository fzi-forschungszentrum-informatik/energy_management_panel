var colorSet = ["78, 115, 223", "189, 60, 48", "23, 123, 47",]

function createChart(elementId, chartType,  datasets,  lables_x, lables_datasets, unit="$", maxTicksLimit=7) {
  var ctx = document.getElementById(elementId);
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
      console.log(data)
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
  //TODO Implement Donut
  /*else if (chartType == "doughnut") {
    for (var i = 0; i < datasets.length; i++) {
      var colorOpaque = "rgba("+ colorSet[i] +", 1)";
      var colorTransparent = "rgba("+ colorSet[i] +", 0.05)";
      data.push(
          {
          backgroundColor: colorOpaque,
          hoverBackgroundColor: colorTransparent,
          hoverBorderColor: colorTransparent,
          data: datasets[i]
          }
      )
    }
  }*/
  var myLineChart = new Chart(ctx, {
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
}

function setUpChartXAxes(chartType, maxTicksLimit) {
  var xAxes = [{
    time: {
      //TODO set unit
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