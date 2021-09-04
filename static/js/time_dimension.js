// start of TimeDimension manual instantiation
var timeDimension = new L.TimeDimension({
  period: "PT5H",
});
// helper to share the timeDimension object between all layers
map.timeDimension = timeDimension;
// otherwise you have to set the 'timeDimension' option on all layers.

var player = new L.TimeDimension.Player({
  transitionTime: 100,
  loop: false,
  startOver: true
}, timeDimension);

var timeDimensionControlOptions = {
  player: player,
  timeDimension: timeDimension,
  position: 'bottomleft',
  autoPlay: true,
  minSpeed: 1,
  speedStep: 0.5,
  maxSpeed: 15,
  timeSliderDragUpdate: true
};

var timeDimensionControl = new L.Control.TimeDimension(timeDimensionControlOptions);
map.addControl(timeDimensionControl);

/*var timeSeriesLayer = L.geoJSON(geojsonLayer, {style: style});
var geojson = L.timeDimension.layer.geoJson(geojsonLayer);
geojson.addTo(map);*/
