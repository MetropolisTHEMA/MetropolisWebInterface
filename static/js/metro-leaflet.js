// Iniyialize the leadlet map_
var map = L.map('map').setView([48.832091014134825, 2.355001022600193], 11)

Roads = L.featureGroup().addTo(map)
var style = {
    "color": "#ff7800",
    "fillColor": "#ff7800",
    "weight": 1,
    "opacity": 0.65
};

/*L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoiYWJhMnMiLCJhIjoiY2tweWs1MzNhMDVlMTJ2cGY4OXdwcWdnYiJ9.h7Rrc3raFHNkTIoG9R3jyA'
}).addTo(map);*/

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', { // LIGNE 20
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);


fetch('http://127.0.0.1:8000/edges.geojson/')
  .then((reponse) => reponse.json())
  .then((data) => {
  	var geoJSON = L.geoJSON(data["features"], {
  		style: style
  	}).addTo(Roads)
  	map.fitBounds(geoJSON.getBounds())
  });


function linkDropDown(){
  // Remove any previous legend
  d3.select('#linkLegendSvg').remove();
  var linkSelector = document.getElementById('linkSelector')

    if (linkSelector.value =="default"){
    	console.log(Roads.toGeoJSON().features)
        Roads.eachLayer(function (layer) {
            layer.setStyle({fillColor: "#FFF500"})
        });
    }
 }
