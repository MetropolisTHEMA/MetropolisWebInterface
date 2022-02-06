// display only features with the 'name' property 'USA'
/*  map.setFilter('my-layer', ['==', ['get', 'name'], 'USA']);

  // display only features with five or more 'available-spots'
  map.setFilter('bike-docks', ['>=', ['get', 'available-spots'], 5]);

  // remove the filter for the 'bike-docks' style layer
  map.setFilter('bike-docks', null);
  */

  var linkSelector = document.getElementById('linkSelector')
  var slider = document.getElementById('slider')
  var current_time = document.getElementById('active-hour')
  var first_color = document.getElementById("first")
  var second_color = document.getElementById("second")
  var color1 = hex2rgb(first_color.value)
  var color2 = hex2rgb(second_color.value)
  var time = ["06:00", "06:15", "06:30", "06:45",
      "07h:00", "07h:15", "07h:30", "07h:45",
      "08:00", "08:15", "08:30", "08:45",
      "09:00", "09:15", "09:30", "09:45",
      "10:00", "10:15", "10:30", "10:45",
      "11:00", "11:15", "11:30", "11:45",
      "12:00"]
  
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
  
  function ColorScale(min, max, rgb1, rgb2) {
    const colorscale = d3.scaleLinear().domain([min, max])
      .interpolate(d3.interpolateHcl)
      .range([d3.rgb(rgb1), d3.rgb(rgb2)]);
    drawLinkLegend(colorscale, min, max);
  }
  
  function InputSetPaintProperty(field, array, min, color2){
    let max = Math.max(...array);
     map.setPaintProperty('lines', 'fill-color', [
        'interpolate-hcl', ['linear'],
        ['get', field],
        min, color1, //'rgb(255, 245,0 )',
        max, color2, //'rgb(255, 0, 0)',
      ]);
      d3.select('#linkLegendSvg').remove();
      ColorScale(min, max, color1, color2)
  }
  
  
  function OutputSetPaintProperty(field,array_of_array, min){
    var counter = 0;
    var intervalId = 25;
  
    /* Initializing the slider when the drop down list change */
    slider.addEventListener('mouseenter', (e) => {
      linkSelector.addEventListener('change',function(){
        slider.value = 0;
        counter = 0;
        intervalId = 0;
        current_time.innerText = '6:00'
      })
  
      function stop(){
        clearInterval(intervalId);
      }
      
      function start(){
        if (counter==intervalId) stop()
        else {
          slider.value = counter
          const _data = [];
          const _max_ = [];
          array_of_array.forEach(item => {
            _data.push(item[counter])
            _max_.push(Math.max(...item))
          });
        var max_of_max = Math.max(..._max_)
        var max = Math.round(Math.max(..._data)); 
        map.setPaintProperty('lines', 'fill-color', [
          'interpolate-hcl', ['linear'],
           ['at', counter, ['get', field]],
            min, color1,
            max, color2,
          ]);
        d3.select('#linkLegendSvg').remove();
        ColorScale(min, max_of_max, color1, color2)
        current_time.innerText = time[counter]
        counter++;
        } 
       // ColorScale(min, max_of_max, color1, color2)
      }
      setInterval(start, 1500)
    })
  }
  
  async function linkDropDown() {
    d3.select('#linkLegendSvg').remove();
    document.getElementById('console').style.display = 'none'
  
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
      var min = 1;
      InputSetPaintProperty('lanes', lanes_array, min, color2)
  
      second_color.addEventListener('input', function(){
        let color = hex2rgb(second_color.value)
        InputSetPaintProperty('lanes', lanes_array, min, color)
      });
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
      let min = 0;
      InputSetPaintProperty('length', length_array, min,color2)
  
      second_color.addEventListener('input', function(){
        let color = hex2rgb(second_color.value)
        InputSetPaintProperty('length', length_array, min, color)
      });
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
  
     let min = 0; 
      InputSetPaintProperty('speed',speed_array, min, color2)
  
      second_color.addEventListener('input', function(){
        let color = hex2rgb(second_color.value)
        InputSetPaintProperty('speed', speed_array, min, color)
      });
    }
    /*................. The output value .....................*/
    else if (linkSelector.value === "speed_output") {
      d3.select('#linkLegendSvg').remove();
      const speed_output = await GetOutputFieldAttribute("speed")
      console.log(speed_output)
      data.features.map(
        feature => {
          feature.properties.speed_output = speed_output[feature.properties.edge_id]
        });
      map.getSource('roads').setData(data)
      var speed_output_array = Object.values(speed_output)
      //console.log(speed_output_array)
      let min = 0; 
      OutputSetPaintProperty('speed_output', speed_output_array, min)
      document.getElementById('console').style.display = 'block'
  
      /* To execute the first position (first hour) when a field is selected */
      map.setPaintProperty('lines', 'fill-color', [
        'interpolate-hcl', ['linear'],
        ['at', 0, ['get', 'speed_output']],
        0, color1,
        130, color2,
      ]);
      
    }
    else if (linkSelector.value === "congestion") {
      d3.select('#linkLegendSvg').remove();
      const congestion = await GetOutputFieldAttribute("congestion")
      data.features.map(
        feature => {
          feature.properties.congestion = congestion[feature.properties.edge_id]
        });
      map.getSource('roads').setData(data)
      var congestion_array = Object.values(congestion)
      let min = 0; 
      OutputSetPaintProperty('congestion', congestion_array, min)
      document.getElementById('console').style.display = 'block'
  
      /* To execute the first position (first hour) when a field is selected */
      map.setPaintProperty('lines', 'fill-color', [
        'interpolate-hcl', ['linear'],
        ['at', 0, ['get', 'congestion']],
        0, color1,
        1, color2,
      ]);
    }
    else if (linkSelector.value === "travel_time") {
      d3.select('#linkLegendSvg').remove();
      const travel_time = await GetOutputFieldAttribute("travel_time")
  
      data.features.map(
        feature => {
          feature.properties.travel_time = travel_time[feature.properties.edge_id]
        });
      map.getSource('roads').setData(data)
      var travel_time_array = Object.values(travel_time)
      let min = 0; 
      OutputSetPaintProperty('travel_time', travel_time_array, min)
      document.getElementById('console').style.display = 'block'
  
      /* To execute the first position (first hour) when a field is selected */
      map.setPaintProperty('lines', 'fill-color', [
        'interpolate-hcl', ['linear'],
        ['at', 0, ['get', 'travel_time']],
        0, color1,
        2000, color2,
      ]);
    }
  } //End function
  
  
  