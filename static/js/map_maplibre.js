// Get url of the current network
current_url = window.location.href // document.url
network_id = parseInt(current_url.split('/')[5]) // Get networ id
var total_bounds = data['total_bounds']

if(network_type) {
  var map = new maplibregl.Map({
    container: 'map',
    style: {
      version: 8,
      sources: {},
      layers: []
    },
    zoom: 4
  })
} else {
  var map = new maplibregl.Map({
    container: 'map',
    //style: 'https://api.maptiler.com/maps/pastel/style.json?key=H3QHO1MyRW0VntDUexsM',
    style: 'https://api.maptiler.com/maps/a656d271-f1f7-4b23-927a-5af6559f7049/style.json?key=6OYzFVmHZSrmbPQ2uqDd',
  // center: center, //[2.333, 48.8934]
  zoom: 8
  });
}

map.fitBounds(total_bounds)
map.addControl(new maplibregl.NavigationControl(), 'top-right');
map.addControl(new maplibregl.FullscreenControl())

var hoveredStateId = null;

  var hoveredStateId = null;
  map.on('load', function() {

    map.addSource('roads', {
      type: 'geojson',
      data: data,
      'generateId': true // It generate an automatic id which is undefined by defautre
    });
    map.addLayer({
      'id': 'lines',
      'type': 'fill',
      'source': 'roads',
      'layout': {},
      'paint': {
        'fill-color': ['get', 'color'],
        'fill-opacity': [
          'case',
          ['boolean', ['feature-state', 'hover'], false],
          1,
          0.6
        ]
      }
    });

    /*...... Start Blog create a hover effect ......*/

    // When the user hover their mouse over the 'lines' layer, we'll update the
    // feature state for the feature under the mouse.
    map.on('mousemove', 'lines', (e) => {
      map.getCanvas().style.cursor = 'pointer'

      if (e.features.length > 0) {
        if (hoveredStateId !== null) {
          map.setFeatureState({
            source: 'roads',
            id: hoveredStateId
          }, {
            hover: false
          });
        }
        hoveredStateId = e.features[0].id;
        map.setFeatureState({
          source: 'roads',
          id: hoveredStateId
        }, {
          hover: true
        });
      }
    });

    // When the mouse leaves the 'lines' layer, update the feature state of the
    // previously hovered feature.
    map.on('mouseleave', 'lines', () => {
      if (hoveredStateId !== null) {
        map.setFeatureState({
          source: 'roads',
          id: hoveredStateId
        }, {
          hover: false
        });
      }
      hoveredStateId = null;
      map.getCanvas().style.cursor = ''
      popup.remove()

    });
    /*...... End Blog create a hover effect ......*/

  }) // End map.on load

  /*...... Start Blog Displaying links information  ......*/

  // Create a popup, but don't add it to the map yet.
    var popup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false
    });
    map.on('mousemove', 'lines', async function(e) {
      let edge_id = e.features[0].properties.edge_id;
      var edge_instance_api = await fetch(
        `http://127.0.0.1:8000/api/network/${network_id}/edge_id/${edge_id}`)
        edge_instance = await edge_instance_api.json()

      popup.setLngLat(e.lngLat).setHTML(
        JSON.stringify(edge_instance, null, 2)
      ).addTo(map)
    });
  /*...... End Blog Displaying links information  ......*/
