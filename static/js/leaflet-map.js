var geojsonLayer;

function highlightFeature(e) {
  var layer = e.target;
  layer.setStyle({
    weight: 2,
    color: 'cyan',
    fillColor: 'cyan',
  });

  if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
    layer.bringToFront();
  }
}

function resetHighlight(e) {
  geojsonLayer.resetStyle(e.target);

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
var roads = L.layerGroup();

var map = L.map('map', {
  preferCanvas: true,
  layers: roads
}).setView([48.833, 2.333], 9);

var darkMatter = L.tileLayer('http://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
  attribution: 'Dark matter'
})
/* abstract or real network */
if(network_type==false){
  map.addLayer(darkMatter)
}
//map.addLayer(osmLayer);
//map.addLayer(CartoDBLayer)

function style(feature) {
  return {
  color: feature.properties.color,
    fillColor: feature.properties.color,
    weight: 3,
    opacity: 0.5,
    fillOpacity: 0.5
  }
};

<!-- - leaflet geojson - vt options-- - >
  var options = {
    maxZoom: 20,
    tolerance: 3,
    debug: 0,
    style: style
  };


/*current_url  = window.location.href // document.url
network_id = parseInt(current_url.split('/')[5]) // Get networ id
fetch(`http://127.0.0.1:8000/api/network/${network_id}/edges/`)*/

/* Fetching the saved file edges.geoson data (from python module
   make_network_visualization) througth the api. */
current_url = window.location.href
network_id = parseInt(current_url.split('/')[5])

const request = async () => {
const response = await fetch(`http://127.0.0.1:8000/network/${network_id}/edges.geojson/`);
  const data = await response.json();
  geojsonLayer = L.geoJSON(data["features"], {
    style: style,
    onEachFeature: onEachFeature
  }).addTo(map)
  map.fitBounds(geojsonLayer.getBounds())
  geojsonLayer.addTo(roads)

  /*geojsonLayer = L.geoJSON.vt(data, options).addTo(map);
  geojsonLayer.addTo(roads)*/

  const links = await fetch(`http://127.0.0.1:8000/api/network/${network_id}/edges/`);
  const linksdata = await links.json();
  geojsonLayer.eachLayer(function(layer) {
    let currentLayer = linksdata.find(
      element => element.edge_id === layer.feature.properties.edge_id)
    layer.bindTooltip(
      "name: " + currentLayer.name + "<br>" +
      "lanes: " + currentLayer.lanes + "<br>" +
      "speed: " + currentLayer.speed + "<br>" +
      "length: " + currentLayer.length.toFixed(2)
    )
  })
  return linksdata
}
request();

let stamenLite = L.tileLayer('//{s}.tile.stamen.com/toner-lite/{z}/{x}/{y}.png', {
  attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> — Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
  subdomains: 'abcd',
  maxZoom: 20,
  minZoom: 0,
  label: 'Toner Lite' // Libellé pour le tooltip en option
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
  maxZoom: 20,
  minZoom: 1,
  label: 'Watercolor'
});

var cartoDBLayer = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors, © CartoDB'
});

var osmLayer = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 20
});

var darkTheme = L.tileLayer('http://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
  attribution: 'Dark matter'
})

var baseLayers = {
  "cartoDBLayer": cartoDBLayer,
  "osmLayer": osmLayer,
  "stamenLite": stamenLite,
  "stamenToner": stamenToner,
  "stamenColor": stamenColor,
  "darkTheme": darkTheme
}
var overlays = {
  "Roads": roads,
};

L.control.layers(  baseLayers,  overlays,
  {
    "autoZIndex": true,
    "collapsed": true,
    "position": "topright"
  }).addTo(map);
