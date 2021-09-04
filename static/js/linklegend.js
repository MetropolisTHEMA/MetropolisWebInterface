function drawLinkLegend(colorscale, min, max) {
    // Show label
    linkLabel.style.display = 'block'

    var legendWidth = 100
      legendMargin = 10
      legendLength = document.getElementById(
        'legend-links-container').offsetHeight - 2*legendMargin

    // Add legend
    var legendSvg = d3.select('#legend-links-svg')
                .append('g')
                .attr("id", "linkLegendSvg");

    var dif = colorscale.domain()[1] - colorscale.domain()[0];
    var intervals = d3.range(400).map(function(d,i) {
        return dif * i / 400 + colorscale.domain()[0]
    })
    intervals.push(colorscale.domain()[1]);
    var intervalHeight = legendLength / intervals.length;



    var bars = legendSvg.selectAll(".bars")
      .data(intervals)
      .enter().append("rect")
        .attr("class", "bars")
        .attr("x", 0)
        //.attr("y", function(d, i) { return Math.round((intervals.length - 1 - i)  * intervalHeight) + legendMargin; })
        .attr("y", function(d, i) { return ((intervals.length - 1 - i)  * intervalHeight) + legendMargin; })
        //.attr("height", intervalHeight)
        .attr("height", Math.ceil(intervalHeight))
        .attr("width", legendWidth-50)
        .style("fill", function(d, i) { return colorscale(d) })
        .attr("stroke-width",0)

    // create a scale and axis for the legend
    var legendAxis = d3.scaleLinear()
        .domain([min, max])
        .range([legendLength, 0]);

    legendSvg.append("g")
         .attr("class", "legend axis")
         .attr("transform", "translate(" + (legendWidth - 50) + ", " + legendMargin + ")")
         .call(d3.axisRight().scale(legendAxis).ticks(10))
}
