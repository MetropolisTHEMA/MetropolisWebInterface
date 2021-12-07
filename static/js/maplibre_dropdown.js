async function linkDropDown() {
  // display only features with the 'name' property 'USA'
  /*  map.setFilter('my-layer', ['==', ['get', 'name'], 'USA']);

    // display only features with five or more 'available-spots'
    map.setFilter('bike-docks', ['>=', ['get', 'available-spots'], 5]);

    // remove the filter for the 'bike-docks' style layer
    map.setFilter('bike-docks', null);
    */

  var linkSelector = document.getElementById('linkSelector')
  var mapZoom = 8; //map.getZoom();

  if (linkSelector.value == "lanes") {
    // map.fitBounds(map.getBounds().toArray())
    map.setZoom(mapZoom)
    map.setPaintProperty('lines', 'fill-color', [
      'interpolate', ['linear'],
      ['get', 'lanes'],
      1, 'rgb(255, 245,0 )',
      5, 'rgb(255, 0, 0)',
    ]);
  } else if (linkSelector.value == "length") {
    map.setZoom(mapZoom)
    map.setPaintProperty('lines', 'fill-color', [
      'interpolate', ['linear'],
      ['get', 'length'],
      0, 'rgb(255, 245, 0 )',
      3, 'rgb(255, 0, 0)',
    ]);
  } else if (linkSelector.value == "speed") {
    map.setZoom(mapZoom)
    map.setPaintProperty('lines', 'fill-color', [
      'interpolate', ['linear'],
      ['get', 'speed'],
      50, 'rgb(255, 255, 0 )',
      100, 'rgb(0, 255, 0)',
    ]);
  }




} //End function
