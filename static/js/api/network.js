/*
The goejson data is a dictionnary with the folowing keys : ["bbox", "features", "type"]
The data is containing in the "features" key.

data.features[0].properties.oneway
*/
window.onload = function() {
    html = document.getElementById("divToMove");
    document
      .querySelector("#destinationDiv")
      .insertAdjacentHTML("afterbegin", html.innerHTML)

    html.remove();
};

// get map id and geojson data.

for (var name in this) {
    if (name.includes("layer_control_")){
        var {Roads, Intersections} = window[name].overlays;
    };

    if (name.includes("map_")) {
        var map = window[name];
    }
};

// Define colorscale arrays
/*
var colorscale_lanes = ['#00e600', '#b3ffb3', '#e6ffe6']
var colorscale_length = ['#8080ff', '#b3b3ff', '#ccccff', '#e6e6ff']
var colorscale_speed = ['#666600', '#b3b300', '#ffff1a', '#ffffcc']
*/
//colorscale_lucas
// return colorscale_lucas(d/m)
/*
function getColor_by_lanes(d) {
    return d > 2  ? colorscale_lanes[0]:
           d > 1  ? colorscale_lanes[1] :
           d > 0  ? colorscale_lanes[2] :
                    ''
}

function getColor_by_length(d){
    return d > 10 ? colorscale_length[0] :
           d > 5  ? colorscale_length[1] :
           d > 2  ? colorscale_length[2] :
           d > 0  ? colorscale_length[3]:
                    '';
    }


function getColor_by_speed(d){
    return d > 110 ? colorscale_speed[0] :
           d > 80  ? colorscale_speed[1] :
           d > 50  ? colorscale_speed[2] :
           d > 10  ? colorscale_speed[3] :
                     '';
}

function getColor_by_capacity(d){
    return d > 110  ? '#800026' :
           d > 80  ? '#BD0026' :
           d > 50  ? '#E31A1C' :
           d > 10  ? '#FC4E2A' :
                      '#FFEDA0';
}

// Create a legendLanes
var legendLanes = L.control({position: 'bottomright'});
legendLanes.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0, 1, 2],
        labels = [];

    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor_by_lanes(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }

    return div;
};

// Create a legendLength
var legendLength = L.control({position: 'bottomright'});
legendLength.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0, 2, 5, 10],
        labels = [];

    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor_by_length(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }

    return div;
};

// Create a legendSpeed
var legendSpeed = L.control({position: 'bottomright'});
legendSpeed.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [10, 50, 80, 110],
        labels = [];

    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor_by_speed(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }

    return div;
};
*/
// Fetch data from api.
    var edges_from_api;
    // Get the current url
    current_url  = window.location.href // document.url
    // Get networ id
    network_id = parseInt(current_url.split('/')[5])
    fetch(`http://127.0.0.1:8000/api/network/${network_id}/edges/`)
        .then((response) => {
            return response.json()
        })
        .then((data) => edges_from_api=data)
        //.then(() => data_from_api)
/*
function drawLinkLegend(dataset, colorscale, min, max) {
            // Show label+
    linkLabel.style.display = 'block'

    var legendWidth = 100
        legendMargin = 10
        legendLength = document.getElementById('legend-links-container').offsetHeight - 2*legendMargin
        legendIntervals = Object.keys(colorscale).length
        legendScale = legendLength/legendIntervals

            // Add legend

    var legendSvg = d3.select('#legend-links-svg')
          .append('g')
          .attr("id", "linkLegendSvg");

    var bars = legendSvg.selectAll(".bars")
        //.data(d3.range(legendIntervals), function(d) { return d})
        .data(dataset)
        .enter().append("rect")
        .attr("class", "bars")
        .attr("x", 0)
        .attr("y", function(d, i) { return legendMargin + legendScale * (legendIntervals - i-1); })
        .attr("height", legendScale)
        .attr("width", legendWidth-50)
        .style("fill", function(d) { return colorscale(d) })

  // create a scale and axis for the legend
  var legendAxis = d3.scaleLinear()
      .domain([min, max])
      .range([legendLength, 0]);

  legendSvg.append("g")
           .attr("class", "legend axis")
           .attr("transform", "translate(" + (legendWidth - 50) + ", " + legendMargin + ")")
           .call(d3.axisRight().scale(legendAxis).ticks(10))
}
*/

function drawLinkLegend(dataset, colorscale, min, max) {
    // Show label
    linkLabel.style.display = 'block'

    var legendWidth = 100
        legendMargin = 10
        legendLength = document.getElementById('legend-links-container').offsetHeight - 2*legendMargin


    // Add legend
    var legendSvg = d3.select('#legend-links-svg')
                .append('g')
                .attr("id", "linkLegendSvg");



    var dif = colorscale.domain()[1] - colorscale.domain()[0];
    var intervals = d3.range(200).map(function(d,i) {
        return dif * i / 200 + colorscale.domain()[0]
    })
    intervals.push(colorscale.domain()[1]);
    var intervalHeight = legendLength / intervals.length;



    var bars = legendSvg.selectAll(".bars")
      .data(intervals)
      .enter().append("rect")
        .attr("class", "bars")
        .attr("x", 0)
        .attr("y", function(d, i) { return Math.round((intervals.length - 1 - i)  * intervalHeight) + legendMargin; })
        .attr("height", intervalHeight)
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


function linkDropDown(){
  Roads.eachLayer(function (layer) {
      let mydata = edges_from_api.find(element => element.edge_id===layer.feature.properties.edge_id)
      layer.bindTooltip("name: "+mydata.name + "<br>"+
                        "id: "+mydata.edge_id +"<br>"+
                        "lanes: "+mydata.lanes +"<br>"+
                        "speed: "+mydata.speed + "<br>"+
                        "length: "+mydata.length.toFixed(2))
    });

  // Remove any previous legend
    d3.select('#linkLegendSvg').remove();
    dataset = Roads.toGeoJSON().features
    var linkSelector = document.getElementById('linkSelector')

    if (linkSelector.value ==="default"){
        Roads.eachLayer(function (layer) {
            layer.setStyle({fillColor: layer.feature.properties.color})
            layer.on('mouseout', function(){
            layer.setStyle({fillColor: layer.feature.properties.color})
            })
        });
    }

    else if (linkSelector.value ==="lanes"){
      let arrayObject = edges_from_api.map(object => object.lanes);
      //Get min and max values
      let max = d3.max(arrayObject);
      let min = d3.min(arrayObject);
      let colorscale = d3.scaleSequential()
          .domain(d3.extent(arrayObject))
          .interpolator(d3.interpolateOranges);
    /*  let colorscale = d3.scaleLinear()
          .domain([min, max])
          .range(['#c1e3c1', '#e6ffe6', '#94e094', '#97FF33', '#C1FF33', '#4CFF33', '#33FFE6', '#33D1FF', '#3398FF', '#FF33E1', '#FF3387']);
      */
      drawLinkLegend(arrayObject, colorscale, min, max);
      Roads.eachLayer(function (layer) {
            //layer.feature.properties.lanes = data_from_api.find(data.edge_id===layer.feature.properties.edge_id)
          let mydata = edges_from_api.find(element => element.edge_id===layer.feature.properties.edge_id)
          layer.setStyle({fillColor:colorscale(mydata.lanes)})
          layer.on('mouseout', function(){
              layer.setStyle({fillColor: colorscale(mydata.lanes)})
          })
        });
    }

    else if (linkSelector.value === "length"){
      let arrayObject = edges_from_api.map(object => object.length);
      let max = d3.max(arrayObject);
      let min = d3.min(arrayObject);
      let colorscale = d3.scaleLinear()
          .domain([min, max])
          .range(['#c1e3c1', '#e6ffe6', '#94e094', '#97FF33', '#C1FF33', '#4CFF33', '#33FFE6', '#33D1FF']);
      drawLinkLegend(arrayObject, colorscale, min, max);
      Roads.eachLayer(function (layer) {
            let mydata = edges_from_api.find(element => element.edge_id===layer.feature.properties.edge_id)
            layer.setStyle({fillColor: colorscale(mydata.length)})
            layer.on('mouseout', function(){
            layer.setStyle({fillColor: colorscale(mydata.length)})
            })
        });
    }
    else if (linkSelector.value === "speed"){
      let arrayObject = edges_from_api.map(object => object.speed);
      let max = d3.max(arrayObject);
      let min = d3.min(arrayObject);
      /*let colorscale = d3.scaleLinear()
          .domain([min, max])
          .range(['#c1e3c1', '#e6ffe6', '#94e094', '#97FF33', '#C1FF33', '#4CFF33', '#33FFE6', '#33D1FF']);*/
          let colorscale = d3.scaleSequential()
              .domain(d3.extent(arrayObject))
              .interpolator(d3.interpolateGreys);
      drawLinkLegend(arrayObject, colorscale, min, max);
        Roads.eachLayer(function (layer) {
            let mydata = edges_from_api.find(element => element.edge_id===layer.feature.properties.edge_id)
            layer.setStyle({fillColor: colorscale(mydata.speed)})
            layer.on('mouseout', function(){
            layer.setStyle({fillColor: colorscale(mydata.speed)})
          })
        });
        /*legendSpeed.addTo(map)
        map.removeControl(legendLength)
        map.removeControl(legendLanes)*/
    }
}
