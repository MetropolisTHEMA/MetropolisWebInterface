// display only features with the 'name' property 'USA'
/*  map.setFilter('my-layer', ['==', ['get', 'name'], 'USA']);

  // display only features with five or more 'available-spots'
  map.setFilter('bike-docks', ['>=', ['get', 'available-spots'], 5]);

  // remove the filter for the 'bike-docks' style layer
  map.setFilter('bike-docks', null);
  */

function Play() {
  var first_color = hex2rgb(document.getElementById("first").value)
  var second_color = hex2rgb(document.getElementById("second").value)
  
    for (let i = 0; i <25; i++) {
      document.getElementById('slider').addEventListener('input', (event) => {
        //const hour = parseInt(event.target.value)
        map.setPaintProperty('lines', 'fill-color', [
          'interpolate', ['linear'],
          ['at', i, ['get', 'speed_output']],
          30, first_color,
          70, second_color,
        ]);
        document.getElementById('active-hour').innerText = time[i]
      });
    }
}

async function GetFieldAttribute(field) {
  // Get url of the current network
  const current_url = window.location.href // document.url
  const network_id = parseInt(current_url.split('/')[5]) // Get network id

  let get_field_request = await fetch(
    `http://127.0.0.1:8000/api/network/${network_id}/edges/${field}`);
  let get_field_dictionary = await get_field_request.json();
  return get_field_dictionary
}

async function GetOutputFieldAttribute(field) {
  const current_url = window.location.href // document.url
  //const network_id = parseInt(current_url.split('/')[5]) // Get network id

  let get_field_request = await fetch(
    `http://127.0.0.1:8000/api/run/1/edges_results/${field}`);

  let get_field_dictionary = await get_field_request.json();
  return get_field_dictionary
}

/* The following convert hex code to rgb */
function hex2rgb(hex) {
  var validHEXInput = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!validHEXInput) {
    return false;
  }

  r = parseInt(validHEXInput[1], 16);
  g = parseInt(validHEXInput[2], 16);
  b = parseInt(validHEXInput[3], 16);
  return 'rgb(' + r + ',' + g + ',' + b + ')';
}

function ColorScale(array, rgb1, rgb2) {
  const max = d3.max(array);
  const min = d3.min(array);
  const colorscale = d3.scaleLinear().domain(d3.extent(array))
    .interpolate(d3.interpolateHcl)
    .range([d3.rgb(rgb1), d3.rgb(rgb2)]);
  drawLinkLegend(colorscale, min, max);
}

function MapLibreSetPaintProperty(field, array, number1, number2, color1, color2) {
  map.setPaintProperty('lines', 'fill-color', [
    'interpolate', ['linear'],
    ['get', field],
    number1, color1, //'rgb(255, 245,0 )',
    number2, color2, //'rgb(255, 0, 0)',
  ]);
  ColorScale(array, color1, color2)
}

function MapLibreSetPaintProperty2(field, array, number1, number2, color1, color2) {
  let time = ["06h:00", "06h:15", "06h:30", "06h:45",
    "07h:00", "07h:15", "07h:30", "07h:45",
    "08h:00", "08h:15", "08h:30", "08h:45",
    "09h:00", "09h:15", "09h:30", "09h:45",
    "10h:00", "10h:15", "10h:30", "10h:45",
    "11h:00", "11h:15", "11h:30", "11h:45",
    "12h:00"]
  
  document.getElementById('slider').addEventListener('input', (event) => {
    const hour = parseInt(event.target.value);
    // update the map
    map.setPaintProperty('lines', 'fill-color', [
      'interpolate', ['linear'],
      ['at', hour, ['get', field]],
      number1, color1,
      number2, color2,
    ]);
    d3.select('#linkLegendSvg').remove();
    // update text in the UI
    document.getElementById('active-hour').innerText = time[hour]

    ColorScale(array[hour], color1, color2)
  });
}

async function linkDropDown() {
  d3.select('#linkLegendSvg').remove();
  var linkSelector = document.getElementById('linkSelector')
  var first_color = hex2rgb(document.getElementById("first").value)
  var second_color = hex2rgb(document.getElementById("second").value)

  if (linkSelector.value == "default") {
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
    let max = lanes_array[lanes_array.indexOf(Math.max(...lanes_array))];
    let min = lanes_array[lanes_array.indexOf(Math.min(...lanes_array))];
    MapLibreSetPaintProperty('lanes', lanes_array, min, max, first_color, second_color)
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
    let max = length_array[length_array.indexOf(Math.max(...length_array))];
    let min = length_array[length_array.indexOf(Math.min(...length_array))];
    MapLibreSetPaintProperty('length', length_array, min, max, first_color, second_color)
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
   let max = speed_array[speed_array.indexOf(Math.max(...speed_array))];
   let min = speed_array[speed_array.indexOf(Math.min(...speed_array))];
    MapLibreSetPaintProperty('speed',speed_array, min, max, first_color, second_color)
  }
  /*................. The output value .....................*/
  else if (linkSelector.value == "speed_output") {
    d3.select('#linkLegendSvg').remove();
    const speed_output = await GetOutputFieldAttribute("speed")

    data.features.map(
      feature => {
        feature.properties.speed_output = speed_output[feature.properties.edge_id]
      });
    map.getSource('roads').setData(data)
    var speed_output_array = Object.values(speed_output)
    MapLibreSetPaintProperty2('speed_output', speed_output_array, 30, 130, first_color, second_color)
    
    document.getElementById('console').style.display = 'block'
  }
  else if (linkSelector.value == "congestion") {
    const congestion = await GetOutputFieldAttribute("congestion")
    data.features.map(
      feature => {
        feature.properties.congestion = congestion[feature.properties.edge_id]
      });
    map.getSource('roads').setData(data)
    var speed_output_array = Object.values(speed_output)
    
    MapLibreSetPaintProperty2('congestion', 0.3, 0.7, first_color, second_color)
    document.getElementById('console').style.display = 'block'
  }

  else if (linkSelector.value == "") {
    const travel_time = await GetOutputFieldAttribute("travel_time")

    data.features.map(
      feature => {
        feature.properties.congestion = travel_time[feature.properties.edge_id]
      });
    map.getSource('roads').setData(data)
    //var speed_output_array = Object.values(speed_output)

    MapLibreSetPaintProperty2('congestion', 0.3, 0.7, first_color, second_color)
    document.getElementById('console').style.display = 'block'
  }

} //End function

