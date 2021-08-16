var edges_data_api;
// Get the current url
current_url  = window.location.href // document.url
network_id = parseInt(current_url.split('/')[5]) // Get networ id
fetch(`http://127.0.0.1:8000/api/network/${network_id}/edges/`)
  .then((response) => {
    return response.json()
}).then((data) => edges_data_api=data)

var edges_results;
fetch(`http://127.0.0.1:8000/api/run/1/edges_results/`)
  .then((response) => {
    return response.json()
}).then((edges) => edges_results=edges)


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


var geojsonLayer;

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 2,
        color: 'yellow',
        fillColor: 'yellow',
        dashArray: '',
        opacity: 0.5,
        fillOpacity: 3
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
}

function resetHighlight(e) {
    //geojson.resetStyle(e.target);
    let layer = e.target;

    layer.setStyle({
        color: "#ff7800",
        fillColor: "#ff7800",
        weight: 3,
        opacity: 0.5,
        fillOpacity: 0.5
        });
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        //click: zoomToFeature
    });
}

// ... our listeners
geojsonLayer = L.geoJSON();

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

Roads = L.layerGroup();

var map = L.map('map', {preferCanvas: true }).setView([48.833, 2.333], 7); // LIGNE 18
var osmLayer = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', { // LIGNE 20
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        });

//map.addLayer(osmLayer);

var style = {
    color: "#ff7800",
    fillColor: "#ff7800",
    weight: 3,
    opacity: 0.5,
    fillOpacity: 0.5
};
/*
fetch('http://127.0.0.1:8000/edges.geojson/')
  .then((reponse) => reponse.json())
  .then((data) => {
  	geojsonLayer = L.geoJSON(data["features"], {
  		style: style,
      onEachFeature: onEachFeature
  	}).addTo(map)
  	//map.addLayer(geojsonLayer)
  	map.fitBounds(geojsonLayer.getBounds())
    geojsonLayer.addTo(Roads)

  });
*/

const request = async () => {
  const response = await fetch('http://127.0.0.1:8000/network/1/edges.geojson/');
  const data = await response.json();
  geojsonLayer = L.geoJSON(data["features"], {
    style: style,
    onEachFeature: onEachFeature
  }).addTo(map)
    //map.addLayer(geojsonLayer)
  map.fitBounds(geojsonLayer.getBounds())
  geojsonLayer.addTo(Roads)
}
request();

  let stamenLite = L.tileLayer('//{s}.tile.stamen.com/toner-lite/{z}/{x}/{y}.png', {
    attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> — Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    subdomains: 'abcd',
    maxZoom: 20,
    minZoom: 0,
    label: 'Toner Lite'  // Libellé pour le tooltip en option
    });

let stamenToner = L.tileLayer('//{s}.tile.stamen.com/toner/{z}/{x}/{y}.png', {
    attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> — Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    subdomains: 'abcd',
    maxZoom: 20,
    minZoom: 0,
    label: 'Toner'
});

let stamenColor = L.tileLayer('//{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.png', {
    attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> — Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    subdomains: 'abcd',
    maxZoom: 16,
    minZoom: 1,
    label: 'Watercolor'
});


var baseLayers = {
	"stamenLite": stamenLite,
	"stamenToner": stamenToner,
	"stamenColor": stamenColor
}

var overlays = {
			"Roads": Roads
};


L.control.layers(
	baseLayers,
	overlays,
	{
		"autoZIndex": true,
		"collapsed": true,
		"position": "topright"
	}).addTo(map);


/* -----------------------------------------------------*/
/*              Time player                             */
/* -----------------------------------------------------*/

/*var timeDimension = new L.TimeDimension({
        period: "PT1H",
});

map.timeDimension = timeDimension;

var player = new L.TimeDimension.Player({
    transitionTime: 100,
    loop: false,
    startOver:true
}, timeDimension);

var timeDimensionControlOptions = {
    player:        player,
    timeDimension: timeDimension,
    position:      'bottomleft',
    autoPlay:      true,
    minSpeed:      1,
    speedStep:     1,
    maxSpeed:      15,
    timeSliderDragUpdate: true
};
var timeDimensionControl = new L.Control.TimeDimension(timeDimensionControlOptions);
map.addControl(timeDimensionControl);

function style(feature) {
    return {
      weight: 2,
      opacity: 1,
      color: 'rgba(35,35,35,1.0)',
      dashArray: '',
      fillOpacity: 1,
      fillColor: getColor(feature.properties.insol)
    };
  }*/

/* ----------------------------------------------------------------------------*/


function linkDropDown(){
 // Remove any previous legend
  d3.select('#linkLegendSvg').remove();
  var linkSelector = document.getElementById('linkSelector')
    if (linkSelector.value =="default"){
        geojsonLayer.eachLayer(function (layer) {
            layer.setStyle({fillColor: layer.feature.properties.color})
        });
    }
    else if (linkSelector.value =="lanes"){
      console.log(edges_results)
      var lanes_array = edges_data_api.map(object => object.lanes);
      var lanes_max = d3.max(lanes_array);
      var lanes_min = d3.min(lanes_array);
      var lanes_colorscale = d3.scaleLinear().domain(d3.extent(lanes_array))
          .interpolate(d3.interpolateHcl)
          .range([d3.rgb('#FFF500'), d3.rgb("#FF0000")]);
      drawLinkLegend(lanes_colorscale, lanes_min, lanes_max);
      geojsonLayer.eachLayer(function (layer) {
        let currentLayer = edges_data_api.find(element => element.edge_id===layer.feature.properties.edge_id)
        let lanes_color = lanes_colorscale(currentLayer.lanes)
        layer.setStyle({
          fillColor: lanes_color,
          color: lanes_color,
        });

        layer.on('mouseover', function(e){
          layer.setStyle({
          color: 'green',
          fillColor: 'green'
          })
        });
        layer.on('mouseout', function(e){
          layer.setStyle({
           color: lanes_color,
           fillColor: lanes_color
          })
        });
      });
    }
    else if (linkSelector.value == "length"){

      var length_array = edges_data_api.map(object => object.length);
      var length_colorscale = d3.scaleLinear()
          .domain(d3.extent(length_array))
          .interpolate(d3.interpolateHcl)
          .range([d3.rgb("#FFF500"), d3.rgb("#00ff00")]);

      var length_max = d3.max(length_array);
      var length_min = d3.min(length_array);
      drawLinkLegend(length_colorscale, length_min,length_max);
      geojsonLayer.eachLayer(function (layer) {
        let currentLayer = edges_data_api.find(element => element.edge_id===layer.feature.properties.edge_id)
        var length_color = length_colorscale(currentLayer.length)
        layer.setStyle({
          fillColor: length_color,
          color:  length_color
        });
        layer.on('mouseover', function(e){
          layer.setStyle({
          color: 'red',
          fillColor: 'red'
          })
        });
        layer.on('mouseout', function(e){
          layer.setStyle({
           color: length_color,
           fillColor: length_color
          })
        });
      });
    }
    else if (linkSelector.value == "speed"){
      var speed_array = edges_data_api.map(object => object.speed);
      var speed_colorscale = d3.scaleLinear().domain(d3.extent(speed_array))
          .interpolate(d3.interpolateHcl)
          .range([d3.rgb("#FFF500"), d3.rgb("#000066")]);
      var speed_max = d3.max(speed_array);
      var speed_min = d3.min(speed_array);
      drawLinkLegend(speed_colorscale, speed_min,speed_max);
      geojsonLayer.eachLayer(function (layer) {
        let currentLayer = edges_data_api.find(element => element.edge_id===layer.feature.properties.edge_id)
        var speed_color = speed_colorscale(currentLayer.speed)
        layer.setStyle({
          fillColor: speed_color,
          color: speed_color,
        })
        layer.on('mouseover', function(e){
          layer.setStyle({
          color: 'red',
          fillColor: 'red'
          })
        });
        layer.on('mouseout', function(e){
          layer.setStyle({
           color: speed_color,
           fillColor: speed_color
          })
        });
      });
    }

    /* ....................................................................................... */
    /* ---------------------------- Output ................................................... */

    else if (linkSelector.value == "travel_time"){
      var currentLayer_travel_time;
      var copie=[];
      var travel_time_array = edges_results.map(object => object.travel_time);
      travel_time_array.forEach(element => {
        tv = element.split(':')
        tv = (+tv[0]) * 3600 + (+tv[1]) * 60 + (+tv[2]);
        copie.push(tv)
      })

      var travel_time_colorscale = d3.scaleLinear().domain(d3.extent(copie))
          .interpolate(d3.interpolateHcl)
          .range([d3.rgb("#FFF500"), d3.rgb("#000066")]);
      var travel_time_max = d3.max(copie);
      var travel_time_min = d3.min(copie);
      drawLinkLegend(travel_time_colorscale, travel_time_min,travel_time_max);
      geojsonLayer.eachLayer(function (layer) {
        let travelLayer = edges_results.filter(edge => edge.edge==layer.feature.properties.edge_id)
        console.log(travelLayer);
        travelLayer.forEach(element => {
          currentLayer_travel_time = element.travel_time.split(':')
          currentLayer_travel_time = (+currentLayer_travel_time[0]) * 3600 + (+currentLayer_travel_time[1]) * 60 + (+currentLayer_travel_time[2]);
          /*var geojsonp = L.timeDimension.layer.geoJson(geojsonLayer);
          geojsonp.addTo(map);*/
        })
        //console.log(currentLayer_travel_time)
        var travel_time_color = travel_time_colorscale(currentLayer_travel_time)
        layer.setStyle({
          fillColor: travel_time_color,
          color: travel_time_color,
        })
        layer.on('mouseover', function(e){
          layer.setStyle({
          color: 'red',
          fillColor: 'red'
          })
        });
        layer.on('mouseout', function(e){
          layer.setStyle({
           color: travel_time_color,
           fillColor: travel_time_color
          })
        });
      });
    }
    else if (linkSelector.value == "speed_output"){
    var currentLayer_speed_output;
      var speed_output_array = edges_results.map(object => object.speed);
      var speed_output_colorscale = d3.scaleLinear().domain(d3.extent(speed_output_array ))
          .interpolate(d3.interpolateHcl)
          .range([d3.rgb("#33F6FF"), d3.rgb("#4933FF")]);
      var speed_output_max = d3.max(speed_output_array);
      var speed_output_min = d3.min(speed_output_array );
      drawLinkLegend(speed_output_colorscale, speed_output_min, speed_output_max);
      geojsonLayer.eachLayer(function (layer) {
        let speed_outputlLayer = edges_results.filter(edge => edge.edge==layer.feature.properties.edge_id)
        speed_outputlLayer.forEach(element =>{
          currentLayer_speed_output = element.speed
        })
        console.log(currentLayer_speed_output)
        var speed_output_color = speed_output_colorscale(currentLayer_speed_output)
        layer.setStyle({
          fillColor: speed_output_color,
          color: speed_output_color,
        })
        layer.on('mouseover', function(e){
          layer.setStyle({
          color: 'red',
          fillColor: 'red'
          })
        });
        layer.on('mouseout', function(e){
          layer.setStyle({
           color: speed_output_color,
           fillColor: speed_output_color
          })
        });
      });
    }


}
