async function linkDropDown() {
  // display only features with the 'name' property 'USA'
  /*  map.setFilter('my-layer', ['==', ['get', 'name'], 'USA']);

    // display only features with five or more 'available-spots'
    map.setFilter('bike-docks', ['>=', ['get', 'available-spots'], 5]);

    // remove the filter for the 'bike-docks' style layer
    map.setFilter('bike-docks', null);
    */

  // Get url of the current network
  current_url = window.location.href // document.url
  network_id = parseInt(current_url.split('/')[5]) // Get networ id
  var linkSelector = document.getElementById('linkSelector')

  if (linkSelector.value == "lanes") {
    // map.fitBounds(map.getBounds().toArray())

    const lanes_field = await fetch(
      `http://127.0.0.1:8000/api/network/${network_id}/edges/lanes`);
    const lanes = await lanes_field.json();

    //Maping api data with the map features data
    //Regarder s'il y a lanes dans properties, si ou on ne refait pas
    // la requete pour la deuxième
    data.features.map(
      item =>{
        item.properties.lanes = lanes[item.properties.edge_id]
      });

    //Updating the already map data.
    map.getSource('roads').setData(data)

    map.setPaintProperty('lines', 'fill-color', [
      'interpolate', ['linear'],
      ['get', 'lanes'],
      1, 'rgb(255, 245,0 )',
      5, 'rgb(255, 0, 0)',
    ]);
  } else if (linkSelector.value == "length") {
    const length_field = await fetch(`http://127.0.0.1:8000/api/network/${network_id}/edges/length`);
    const length = await length_field.json();

    //Maping api data with the map features data
    data.features.map(
      item =>{
        item.properties.length = length[item.properties.edge_id]
      });

    //Updating the already map data.
    map.getSource('roads').setData(data)

    map.setPaintProperty('lines', 'fill-color', [
      'interpolate', ['linear'],
      ['get', 'length'],
      0, 'rgb(255, 245, 0 )',
      3, 'rgb(255, 0, 0)',
    ]);
  } else if (linkSelector.value == "speed") {

    const speed_field = await fetch(`http://127.0.0.1:8000/api/network/${network_id}/edges/speed`);
    const speed = await speed_field.json();

    //Maping api data with the map features data
    data.features.map(
      item =>{
        item.properties.speed = speed[item.properties.edge_id]
      });
    //Updating the already map data.
    map.getSource('roads').setData(data)

    map.setPaintProperty('lines', 'fill-color', [
      'interpolate', ['linear'],
      ['get', 'speed'],
      50, 'rgb(255, 255, 0 )',
      100, 'rgb(0, 255, 0)',
    ]);
  }




} //End function
