function fetchData(){
  fetch('http://127.0.0.1:8000/api/edges/')
    .then( response => {
        console.log(response);
        if(!response.ok){
          throw Error("ERROR");
        }
        return response.json();
        }).
        then(data => {

          const network_attributes= data.map(edges => {

              var linkSelector = document.getElementById('linkSelector')
            switch (linkSelector.value) {
              case "Lanes(input)":
                if ${edge.lanes} ==1){


                }

                break;
              default:
            }
            return ${edge.lanes}
          }).join("");

        }).
        catch(error => {
          console.log(error);
        });
}
fetchData();


