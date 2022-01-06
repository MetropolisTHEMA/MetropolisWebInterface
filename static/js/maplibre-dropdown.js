// display only features with the 'name' property 'USA'
/*  map.setFilter('my-layer', ['==', ['get', 'name'], 'USA']);

  // display only features with five or more 'available-spots'
  map.setFilter('bike-docks', ['>=', ['get', 'available-spots'], 5]);

  // remove the filter for the 'bike-docks' style layer
  map.setFilter('bike-docks', null);
  */
  
async function GetFieldAttribute(field) {
  // Get url of the current network
  const current_url = window.location.href // document.url
  const network_id = parseInt(current_url.split('/')[5]) // Get network id

  let get_field_request = await fetch(
    `http://127.0.0.1:8000/api/network/${network_id}/edges/${field}`);
  let get_field_dictionnary = await get_field_request.json();
  return get_field_dictionnary
}

function ColorScale(field, rgb1, rgb2) {
  const max = d3.max(field);
  const min = d3.min(field);
  const colorscale = d3.scaleLinear().domain(d3.extent(field))
    .interpolate(d3.interpolateHcl)
    .range([d3.rgb(rgb1), d3.rgb(rgb2)]);
  drawLinkLegend(colorscale, min, max);
}

async function linkDropDown() {
  d3.select('#linkLegendSvg').remove();
  var linkSelector = document.getElementById('linkSelector')

  if (linkSelector.value == "default"){
    map.setPaintProperty('lines', 'fill-color', ['get', 'color'])
  }

  else if (linkSelector.value == "lanes") {
    d3.select('#linkLegendSvg').remove();

    /* The following IF block is to avoid to re-excute the same piece of code
      two times. The id is for the first time we select 'lanes' the IF statement is
      executed. But for the second (without refreshing the browser) the ELSE is executed.
      So in this way, we won't query the api twice and adding the lanes from the api. */
    if (typeof data.features[0].properties.lanes == 'undefined') {
      var lanes = await GetFieldAttribute("lanes")
      
      // Adding lanes from the api as the map properties
      data.features.map(
        item => {
          item.properties.lanes = lanes[item.properties.edge_id];
        });
      //Updating the already map data.
      map.getSource('roads').setData(data);
      var lanes_array = Object.values(lanes);
    }
    else {
      var lanes_array = data.features.map(item => item.properties.lanes)
    }
    map.setPaintProperty('lines', 'fill-color', [
      'interpolate', ['linear'],
      ['get', 'lanes'],
      1, 'rgb(255, 245,0 )',
      5, 'rgb(255, 0, 0)',
    ]);
    //ColorScale(lanes_array, '#FFF500', '#FF0000')
    ColorScale(lanes_array, 'rgb(255, 245,0 )', 'rgb(255, 0, 0)')
  }
  else if (linkSelector.value == "length") {
    d3.select('#linkLegendSvg').remove();
    if (typeof data.features[0].properties.length == 'undefined') {
      const length = await GetFieldAttribute("length")
      // Adding length from the api as the map properties
      data.features.map(
        item => {
          item.properties.length = length[item.properties.edge_id]
        });
      //Updating the already map data.
      map.getSource('roads').setData(data)
      var length_array = Object.values(length);
    }
    else {
        var length_array = data.features.map(item => item.properties.length)
    }

    map.setPaintProperty('lines', 'fill-color', [
      'interpolate', ['linear'],
      ['get', 'length'],
      0, 'rgb(255, 245, 0 )',
      3, 'rgb(255, 0, 0)',
    ]);
    //ColorScale(length_array, '#FFF500', '#FF0000')
    ColorScale(length_array, 'rgb(255, 245, 0 )', 'rgb(255, 0, 0)')
  }
   else if (linkSelector.value == "speed") {
    d3.select('#linkLegendSvg').remove();
     if (typeof data.features[0].properties.speed == 'undefined') {
       const speed = await GetFieldAttribute("speed")
       // Adding speed from the api as the map properties
       data.features.map(
         item => {
           item.properties.speed = speed[item.properties.edge_id]
         });
       //Updating the already map data.
       map.getSource('roads').setData(data)
       var speed_array = Object.values(speed);
     }
     else {
         var speed_array = data.features.map(item => item.properties.speed)
     }

    map.setPaintProperty('lines', 'fill-color', [
      'interpolate', ['linear'],
      ['get', 'speed'],
      50, 'rgb(255, 245, 0 )',
      100, 'rgb(0, 0, 102)',
    ]);
    //ColorScale(speed_array, "#FFF500", "#000066")
    ColorScale(speed_array, 'rgb(255, 245, 0 )', 'rgb(0, 0, 102)')
  }

} //End function
