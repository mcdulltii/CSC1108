var map;
var marker;

function initialize() {
  var mapOptions = {
    center: new google.maps.LatLng(-33.30578381949298, 26.523442268371582),
    zoom: 15
  };
  map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
  google.maps.event.addListener(map, 'click', function(event){
    placeMarker(event.latLng);
  });
}

function placeMarker(location) {
  if (marker) {
    marker.setPosition(location);
  } else {
    marker = new google.maps.Marker({
      position: location,
      map: map
    });
  }
}
