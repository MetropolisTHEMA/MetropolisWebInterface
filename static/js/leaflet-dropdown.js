/* <!--- index-visualization.html---> */
// Displaying layers (links) information whem mouse hover

/*---  Start Leaflet TimeDimension     ---*/
var timeDimension = new L.TimeDimension({
  timeInterval: "2021-10-01 6:00:00/2021-10-01 12:00:00",
  period: "PT15M",
});

map.timeDimension = timeDimension;

var player = new L.TimeDimension.Player({
  transitionTime: 1000, /* act on cursor vitesse */
  loop: false,
  startOver: true
}, timeDimension);

var timeDimensionControlOptions = {
  player: player,
  timeDimension: timeDimension,
   timeZones: ["Local"],
  position: 'bottomleft',
  autoPlay: true,
  timeSliderDragUpdate: true
};

/*var timeDimensionControl = new L.Control.TimeDimension(timeDimensionControlOptions);
map.addControl(timeDimensionControl);

var geojson = L.timeDimension.layer.geoJson(geojsonLayer, {updateTimeDimensionMode: 'replace'});
geojson.addTo(map);*/
/*---  End Leaflet TimeDimension      ---*/


async function linkDropDown() {
  // Remove any previous legend
  d3.select('#linkLegendSvg').remove();

  const edges_data_api = await request()

  /* Lanes contants variables*/
  var lanes_array = edges_data_api.map(element => element.lanes);
  var lanes_max = d3.max(lanes_array);
  var lanes_min = d3.min(lanes_array);
  var lanes_colorscale = d3.scaleLinear().domain(d3.extent(lanes_array))
    .interpolate(d3.interpolateHcl)
    .range([d3.rgb('#FFF500'), d3.rgb("#FF0000")]);

  /* Length constants variables*/
  var length_array = edges_data_api.map(element => element.length);
  var length_colorscale = d3.scaleLinear()
    .domain(d3.extent(length_array))
    .interpolate(d3.interpolateHcl)
    .range([d3.rgb("#FFF500"), d3.rgb("#00ff00")]);
  var length_max = d3.max(length_array);
  var length_min = d3.min(length_array);

  /* Speed constants variables*/
  var speed_array = edges_data_api.map(element => element.speed);
  var speed_colorscale = d3.scaleLinear().domain(d3.extent(speed_array))
    .interpolate(d3.interpolateHcl)
    .range([d3.rgb("#FFF500"), d3.rgb("#000066")]);
  var speed_max = d3.max(speed_array);
  var speed_min = d3.min(speed_array);

  var linkSelector = document.getElementById('linkSelector')
  if (linkSelector.value == "default") {
    geojsonLayer.eachLayer(function(layer) {
      layer.setStyle({
        fillColor: layer.feature.properties.color,
        color: layer.feature.properties.color
      })
      layer.on('mouseover', function(e) {
        layer.setStyle({
          color: 'cyan',
          fillColor: 'cyan'
        })
      })
      layer.on('mouseout', function(e) {
        geojsonLayer.resetStyle(e.target)
      })
    }) // End geojson.eachLayer
  }
   else if (linkSelector.value == "lanes") {
    drawLinkLegend(lanes_colorscale, lanes_min, lanes_max);
    geojsonLayer.eachLayer(function(layer) {
      let currentLayer = edges_data_api.find(
        element => element.edge_id === layer.feature.properties.edge_id)
      let lanes_color = lanes_colorscale(currentLayer.lanes)
      layer.setStyle({
        fillColor: lanes_color,
        color: lanes_color,
      });

      layer.on('mouseover', function(e) {
        layer.setStyle({
          color: 'cyan',
          fillColor: 'cyan'
        })
      })
      layer.on('mouseout', function(e) {
        layer.setStyle({
          color: lanes_color,
          fillColor: lanes_color
        })
      })
    })
  }
  else if (linkSelector.value == "length") {
    drawLinkLegend(length_colorscale, length_min, length_max);
    geojsonLayer.eachLayer(function(layer) {
      let currentLayer = edges_data_api.find(
        element => element.edge_id === layer.feature.properties.edge_id)
      var length_color = length_colorscale(currentLayer.length)
      layer.setStyle({
        fillColor: length_color,
        color: length_color
      });
      layer.on('mouseover', function(e) {
        layer.setStyle({
          color: 'cyan',
          fillColor: 'cyan'
        })
      });
      layer.on('mouseout', function(e) {
        layer.setStyle({
          color: length_color,
          fillColor: length_color
        })
      });
    });
  }
  else if (linkSelector.value == "speed") {
    drawLinkLegend(speed_colorscale, speed_min, speed_max);
    geojsonLayer.eachLayer(function(layer) {
      let currentLayer = edges_data_api.find(
        element => element.edge_id === layer.feature.properties.edge_id)
      var speed_color = speed_colorscale(currentLayer.speed)
      layer.setStyle({
        fillColor: speed_color,
        color: speed_color,
      })
      layer.on('mouseover', function(e) {
        layer.setStyle({
          color: 'cyan',
          fillColor: 'cyan'
        })
      });
      layer.on('mouseout', function(e) {
        layer.setStyle({
          color: speed_color,
          fillColor: speed_color
        })
      });
    });
  }

  /* ....................................................................................... */
  /* ---------------------------- Output ................................................... */
  else if (linkSelector.value == "travel_time") {

    /*var travel_time_colorscale = d3.scaleLinear().domain(d3.extent(copie))
      .interpolate(d3.interpolateHcl)
      .range([d3.rgb("#FFF500"), d3.rgb("#000066")]);*/
    var travel_time_color;
    var copie = [];
    var timeStamp = Math.floor(Date.now() / 1000);

    geojsonLayer.eachLayer(function(layer) {
      let travelLayer = edges_results.filter(
        edge => edge.edge == layer.feature.properties.edge_id)

      // Add the times in each Layer
      let travel_time = []
      let interval_time = []
      var timeStamp = Math.floor(Date.now() / 1000);
      travelLayer.forEach(
        element => {
          if (element.edge === layer.feature.properties.edge_id) {
            tt = element['travel_time'].split(':') // split of travel time
            tt = (+tt[0]) * 3600 + (+tt[1]) * 60 + (+tt[2])
            travel_time.push(tt)
            layer.feature.properties.travel_time = travel_time

            tt= element['time']//.split(':') // split of time
            //tt = (+tt[0]) * 3600 + (+tt[1]) * 60
            interval_time.push(tt)
            layer.feature.properties.times = interval_time
          }
        }) //End forEach

        // Je souhaite le travel time pour une heure precise (6:00 parexample)
        //console.log(layer)
       //console.log(layer.feature.properties.travel_time)
        /*travel_time_color = travel_time_colorscale(layer.feature.properties.times)
        layer.setStyle({
          fillColor: travel_time_color,
          color: travel_time_color,
        })*/
    }) // end geojsonLayer.eachLayer
  }
  else if (linkSelector.value == "speed_output") {
    var currentLayer_speed_output;
    var speed_output_array = edges_results.map(object => object.speed);
    var speed_output_colorscale = d3.scaleLinear().domain(d3.extent(speed_output_array))
      .interpolate(d3.interpolateHcl)
      .range([d3.rgb("#33F6FF"), d3.rgb("#4933FF")]);
    var speed_output_max = d3.max(speed_output_array);
    var speed_output_min = d3.min(speed_output_array);
    drawLinkLegend(speed_output_colorscale, speed_output_min, speed_output_max);
    geojsonLayer.eachLayer(function(layer) {
      let speed_outputlLayer = edges_results.filter(edge => edge.edge == layer.feature.properties.edge_id)
      speed_outputlLayer.forEach(element => {
        currentLayer_speed_output = element.speed
      })

      var speed_output_color = speed_output_colorscale(currentLayer_speed_output)
      layer.setStyle({
        fillColor: speed_output_color,
        color: speed_output_color,
      })
      layer.on('mouseover', function(e) {
        layer.setStyle({
          color: 'red',
          fillColor: 'red'
        })
      });
      layer.on('mouseout', function(e) {
        layer.setStyle({
          color: speed_output_color,
          fillColor: speed_output_color
        })
      });
    });
  }
}
