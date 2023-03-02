// Google map
var map;
// Marker overlay
var marker;
// List of bus polylines
var busPolylines = {
  'P101_1': null,
  'P102_1': null,
  'P102_2': null,
  'P106_1': null,
  'P202_1': null,
  'P211_1': null,
  'P211_2': null,
  'P411_1': null,
  'P411_2': null,
  'P403_1': null,
};
// List of bus route colors
var busRouteColors = {
  'P101_1': '#FF0000',
  'P102_1': '#00FF00',
  'P102_2': '#0000FF',
  'P106_1': '#0000FF',
  'P202_1': '#0FF000',
  'P211_1': '#000FF0',
  'P211_2': '#000FF0',
  'P411_1': '#F0000F',
  'P411_2': '#F0000F',
  'P403_1': '#000000',
};
// List of shown overlays
var showOverlays = {
  'P101_1': false,
  'P102_1': false,
  'P102_2': false,
  'P106_1': false,
  'P202_1': false,
  'P211_1': false,
  'P211_2': false,
  'P411_1': false,
  'P411_2': false,
  'P403_1': false,
};

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
//   overlayBusRoute('P101', 1, "#FF0000", map);
//   overlayBusRoute('P102', 1, "#00FF00", map);
//   overlayBusRoute('P102', 2, "#0000FF", map);
//   overlayBusRoute('P106', 1, "#0000FF", map);
//   overlayBusRoute('P202', 1, "#0FF000", map);
//   overlayBusRoute('P211', 1, "#000FF0", map);
//   overlayBusRoute('P211', 2, "#000FF0", map);
//   overlayBusRoute('P411', 1, "#F0000F", map);
//   overlayBusRoute('P411', 2, "#F0000F", map);
//   overlayBusRoute('P403', 1, "#000000", map);

  // Add bus-dropdown event listener
  var checkList = document.getElementById('bus-dropdown');
  checkList.getElementsByClassName('anchor')[0].onclick = function(evt) {
    if (checkList.classList.contains('visible'))
      checkList.classList.remove('visible');
    else
      checkList.classList.add('visible');
  }

  // Add bus-dropdown items event listeners
  var busItems = document.getElementsByClassName('bus-checkbox');
  for (let i=0; i<busItems.length; i++) {
    const busCheckbox = busItems[i];
    const busItemValue = busCheckbox.value;
    // Set default checkbox as unchecked
    busCheckbox.checked = false;
    // Add bus-checkbox event listener
    busCheckbox.addEventListener('click', function() {
      var busCheckboxes = document.getElementsByClassName('bus-checkbox');
      const busCheckboxEvent = busCheckboxes[busItemValue];
      const busItemChecked = busCheckboxEvent.checked;
      // Update overlay depending on checkbox
      updateOverlay(busItemValue, busItemChecked);
    });
  }

  // Add button event listeners
  document.getElementById('show-overlay').addEventListener('click', showOverlay);
  document.getElementById('hide-overlay').addEventListener('click', hideOverlay);
}

function overlayBusRoute(busNumber, direction, color, googleMap) {
  var key = busNumber + '_' + direction;
  // Retrieve bus routes via GET request
  if (busPolylines[key] === null) {
    getBusRoute(busNumber, direction).then(function(busRoute) {
      // Build bus route polyline array
      busPolylines[key] = new google.maps.Polyline({
        path: busRoute,
        geodesic: true,
        strokeColor: color,
        strokeOpacity: 1.0,
        strokeWeight: 3,
      });
      const busPolyline = busPolylines[key];
      // Apply polyline overlay on google map
      busPolyline.setMap(googleMap);
      showOverlays[key] = true;
    });
  } else {
    const busPolyline = busPolylines[key];
    // Apply polyline overlay on google map
    busPolyline.setMap(googleMap);
    showOverlays[key] = true;
  }
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

function overlayBusRoutes(googleMap) {
  // Iterate through list of shown overlays
  for (var key in showOverlays) {
    // Check if overlay is previously shown
    if (showOverlays[key] == true) {
      // Split key into busNumber and direction
      var keySplit = key.split('_');
      // Apply overlay on google map
      overlayBusRoute(keySplit[0], keySplit[1], busRouteColors[key], googleMap);
    }
  }
}

function updateOverlay(busNumber, isShown) {
  // Toggle shown overlay
  showOverlays[busNumber] = isShown;
  if (isShown)
    // Show overlay
    showOverlay();
  else {
    // Hide overlay
    var keySplit = busNumber.split('_');
    overlayBusRoute(keySplit[0], keySplit[1], busRouteColors[busNumber], null);
  }
}

function showOverlay() {
  // Apply overlay on global map
  overlayBusRoutes(map);
}

function hideOverlay() {
  // Hide overlay by applying on null
  overlayBusRoutes(null);
}

