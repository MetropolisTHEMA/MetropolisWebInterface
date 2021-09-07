function linkDropDown() {
  // Remove any previous legend
  d3.select('#linkLegendSvg').remove();
  var linkSelector = document.getElementById('linkSelector')

  // Displaying layers (links) information whem mouse hover
  geojsonLayer.eachLayer(function(layer) {
    var currentLayer = edges_data_api.find(
      element => element.edge_id === layer.feature.properties.edge_id)

    //Looping drop down list
    if (linkSelector.value == "default") {
      layer.setStyle({
        fillColor: layer.feature.properties.color,
        color: layer.feature.properties.color
      })
    } else if (linkSelector.value == "lanes") {
      var lanes_array = edges_data_api.map(object => object.lanes);
      var lanes_max = d3.max(lanes_array);
      var lanes_min = d3.min(lanes_array);
      var lanes_colorscale = d3.scaleLinear().domain(d3.extent(lanes_array))
        .interpolate(d3.interpolateHcl)
        .range([d3.rgb('#FFF500'), d3.rgb("#FF0000")]);
      drawLinkLegend(lanes_colorscale, lanes_min, lanes_max);
      let lanes_color = lanes_colorscale(currentLayer.lanes)
      layer.setStyle({
        fillColor: lanes_color,
        color: lanes_color,
      })

      layer.on('mouseover', function(e) {
        layer.setStyle({
          color: 'green',
          fillColor: 'green'
        })
      })
      layer.on('mouseout', function(e) {
        layer.setStyle({
          color: lanes_color,
          fillColor: lanes_color
        })
      })
    } // End else if lanes
    else if (linkSelector.value == "length") {
      var length_array = edges_data_api.map(object => object.length);
      var length_colorscale = d3.scaleLinear()
        .domain(d3.extent(length_array))
        .interpolate(d3.interpolateHcl)
        .range([d3.rgb("#FFF500"), d3.rgb("#00ff00")]);

      var length_max = d3.max(length_array);
      var length_min = d3.min(length_array);
      drawLinkLegend(length_colorscale, length_min, length_max);
      var length_color = length_colorscale(currentLayer.length)
      layer.setStyle({
        fillColor: length_color,
        color: length_color
      });
      layer.on('mouseover', function(e) {
        layer.setStyle({
          color: 'red',
          fillColor: 'red'
        })
      })
      layer.on('mouseout', function(e) {
        layer.setStyle({
          color: length_color,
          fillColor: length_color
        })
      })
    } // End else if length

    else if (linkSelector.value == "speed") {
      var speed_array = edges_data_api.map(object => object.speed);
      var speed_colorscale = d3.scaleLinear().domain(d3.extent(speed_array))
        .interpolate(d3.interpolateHcl)
        .range([d3.rgb("#FFF500"), d3.rgb("#000066")]);
      var speed_max = d3.max(speed_array);
      var speed_min = d3.min(speed_array);
      drawLinkLegend(speed_colorscale, speed_min, speed_max);
        var speed_color = speed_colorscale(currentLayer.speed)
        layer.setStyle({
          fillColor: speed_color,
          color: speed_color,
        })
        layer.on('mouseover', function(e) {
          layer.setStyle({
            color: 'red',
            fillColor: 'red'
          })
        })
        layer.on('mouseout', function(e) {
          layer.setStyle({
            color: speed_color,
            fillColor: speed_color
          })
        })
    } // End else if speed

  }); //End for eachLayer
}
