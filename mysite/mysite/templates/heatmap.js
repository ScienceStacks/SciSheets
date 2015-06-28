var margin = { top: 50, right: 0, bottom: 100, left: 30 },
    // yvals = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    //xvals = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];
    yvals = {{ ycrds|safe }},
    xvals = {{ xcrds|safe }},
    width = 960 - margin.left - margin.right,
    height = 430 - margin.top - margin.bottom,
    gridSize = Math.floor(width / xvals.length),
    legendElementWidth = gridSize*2,
    buckets = 9,
    colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"]; // alternatively colorbrewer.YlGnBu[9]

// Keep this for testing the template
var data = [{"y": 1, "x": 1, "value": 56},
            {"y": 1, "x": 2, "value": 1},
            {"y": 1, "x": 3, "value": 9},
           ];

var data = {{ data|safe }};

    var colorScale = d3.scale.quantile()
        .domain([0, buckets - 1, d3.max(data, function (d) { return d.value; })])
        .range(colors);

    var svg = d3.select("#chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var xLabels = svg.selectAll(".yLabel")
        .data(yvals)
        .enter().append("text")
          .text(function (d) { return d; })
          .attr("x", 0)
          .attr("y", function (d, i) { return i * gridSize; })
          .style("text-anchor", "end")
          .attr("transform", "translate(-6," + gridSize / 1.5 + ")");
//          .attr("class", function (d, i) { return ((i >= 0 && i <= 4) ? "xLabel mono axis axis" : "xLabel mono axis"); });
//          .attr("class", function(d, i) { return ((i >= 7 && i <= 16) ? "xLabel mono axis axis" : "xLabel mono axis"); });

    var xLabels = svg.selectAll(".xLabel")
        .data(xvals)
        .enter().append("text")
          .text(function(d) { return d; })
          .attr("x", function(d, i) { return i * gridSize; })
          .attr("y", 0)
          .style("text-anchor", "middle")
          .attr("transform", "translate(" + gridSize / 2 + ", -6)");

    var heatMap = svg.selectAll(".yval")
        .data(data)
        .enter().append("rect")
        .attr("x", function(d) { return (d.x - 1) * gridSize; })
        .attr("y", function(d) { return (d.y - 1) * gridSize; })
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("class", "yval bordered")
        .attr("width", gridSize)
        .attr("height", gridSize)
        .style("fill", colors[0]);

    heatMap.transition().duration(0)
        .style("fill", function(d) { return colorScale(d.value); });

    heatMap.append("title").text(function(d) { return d.value; });
        
    var legend = svg.selectAll(".legend")
        .data([0].concat(colorScale.quantiles()), function(d) { return d; })
        .enter().append("g")
        .attr("class", "legend");

    legend.append("rect")
      .attr("x", function(d, i) { return legendElementWidth * i; })
      .attr("y", height)
      .attr("width", legendElementWidth)
      .attr("height", gridSize / 2)
      .style("fill", function(d, i) { return colors[i]; });

    legend.append("text")
      .attr("class", "mono")
      .text(function(d) { return "≥ " + Math.round(d); })
      .attr("x", function(d, i) { return legendElementWidth * i; })
      .attr("y", height + gridSize);
