/*----------------------------- ---------------------*/
/* ------------------ Fetching api data -------------*/
/*---------------------------------------------------*/

var edges_data_api;
// Get url of the current network
current_url  = window.location.href // document.url
network_id = parseInt(current_url.split('/')[5]) // Get networ id
fetch(`http://127.0.0.1:8000/api/network/${network_id}/edges/`)
  .then((response) => {
    return response.json()
}).then((data) => edges_data_api=data)

var edges_results;
fetch(`http://127.0.0.1:8000/api/run/1/edges_results/`)
  .then((response) => {
    return response.json()
}).then((edges) => edges_results=edges)
