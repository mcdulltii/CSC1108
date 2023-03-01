// Google map
var map;
// Marker overlay
var marker;

function initialize() {
  // Google map options
  var mapOptions = {
    // Hardcoded center
    center: {lat: 1.5573879239318515, lng: 103.70745681228475},
    // Zoom out to view all routes
    zoom: 12.55
  };
  // Initialize map on html canvas
  map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
  // Add mouseclick event listener to overlay marker
  google.maps.event.addListener(map, 'click', function(event){
    placeMarker(event.latLng);
  });

  // Overlay bus routes
  overlayBusRoute('P101', 1, "#FF0000");
  overlayBusRoute('P102', 1, "#00FF00");
  overlayBusRoute('P102', 2, "#0000FF");
  overlayBusRoute('P106', 1, "#0000FF");
  overlayBusRoute('P202', 1, "#0FF000");
  overlayBusRoute('P211', 1, "#000FF0");
  overlayBusRoute('P211', 1, "#000FF0");
  overlayBusRoute('P411', 1, "#F0000F");
  overlayBusRoute('P411', 2, "#F0000F");
  overlayBusRoute('P403', 1, "#000000");
}

function overlayBusRoute(busNumber, direction, color) {
  // Retrieve bus routes via GET request
  getBusRoute(busNumber, direction).then(function(busRoute) {
    // Build bus route polyline array
    const busPolyline = new google.maps.Polyline({
      path: busRoute,
      geodesic: true,
      strokeColor: color,
      strokeOpacity: 1.0,
      strokeWeight: 3,
    });
    // Apply polyline overlay on google map
    busPolyline.setMap(map);
  });
}

function placeMarker(location) {
  if (marker) {
    // Overlay marker at clicked position
    marker.setPosition(location);
  } else {
    // Initialize new marker
    marker = new google.maps.Marker({
      position: location,
      map: map
    });
  }
}

function getBusRoute(busNumber, direction) {
  // Return bus route after GET request succeeds
  return new Promise(function(resolve, reject) {
    // Bus number and direction as key
    const key = busNumber + '_' + direction;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        var res = JSON.parse(this.responseText);
        // Return bus route from GET request
        resolve(res[key]);
      }
    };
    // Flask api route
    xhttp.open("GET", "/route/" + busNumber + "/" + direction, true);
    xhttp.send();
  });
}
