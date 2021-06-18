/*
The goejson data is a dictionnary with the folowing keys : ["bbox", "features", "type"]
The data is containing in the "features" key.

data.features[0].properties.oneway
*/
window.onload = function() {
    html = document.getElementById("divToMove");
    document
      .querySelector("#destinationDiv")
      .insertAdjacentHTML("afterbegin", html.innerHTML)

    html.remove();

    for (var name in this){
        if (name.includes("layer_control_")){
            let { Roads, Intersections } = window[name].overlays;
            Roads.setStyle({
              'fillColor': "#FF0000",
              'color': "#FF0000"
            });
            Intersections.setStyle({
              'fillColor': "#14db49",
              'color': "#14db49"
            });
        }
    }

};
