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
          //console.log(data)
          const html = data.map(edge => {
            return `<p>Name: ${edge.name} <br> Lanes: ${edge.lanes} <br> Speed: ${edge.speed}</p>`
          }).join("");
          document
            .querySelector("#root")
            .insertAdjacentHTML("afterbegin", html);
        }).
        catch(error => {
          console.log(error);
        });
}
fetchData();
