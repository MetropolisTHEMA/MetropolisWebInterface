/*var map = L.map("app", {​​
  zoom: 3,
  center: [38.705, 1.15],
  timeDimension: true,
  timeDimensionControl: true,
  timeDimensionOptions: {​​
    times: [1496314227000, 1504263027000],
    currentTime: 1496314227000,
    // period: "P1M",
  }​​,
  timeDimensionControlOptions: {​​
    playerOptions: {​​ transitionTime: 1000, startOver: true }​​,
  }​​
}​​);*/

var map = L.map('app', {​​
  zoom: 3,
  center: [38.705, 1.15],
  timeDimension: true,
  fullscreenControl: true,
  timeDimensionControl: true,
  timeeDimensionOptions: {​​
    timeInterval: [1496314227000, 1504263027000],
    currentTime: 1496314227000,
    period: "PT1M"
  }​​,
  timeDimensionControlOptions: {​​
    playerOptions: {​​ transitionTime: 1000, startOver: true }​​,
  }​​
}​​);

L.tileLayer('https://{​​s}​​.tile.openstreetmap.org/{​​z}​​/{​​x}​​/{​​y}​​.png', {​​
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}​​).addTo(map);


const dataLayer = L.geoJson(data);
L.timeDimension.layer.geoJson(dataLayer).addTo(map);
 
