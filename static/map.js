// Google map
var map;
// Marker overlay
var marker;
// Focused element
var activeInput;
// Overlay shown boolean
var isHidden = false;
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
  'P101_1': '#FC2947',
  'P102_1': '#03C988',
  'P102_2': '#03C988',
  'P106_1': '#820000',
  'P202_1': '#F0997D',
  'P211_1': '#B08BBB',
  'P211_2': '#B08BBB',
  'P411_1': '#5E8C88',
  'P411_2': '#5E8C88',
  'P403_1': '#674747',
  'Walking': '#000000',
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
// Bus route name conversion
var busRouteNames = {
  'P101-loop': 'P101_1',
  'P102-01': 'P102_1',
  'P102-02': 'P102_2',
  'P106-loop': 'P106_1',
  'P202-loop': 'P202_1',
  'P211-01': 'P211_1',
  'P211-02': 'P211_2',
  'P411-01': 'P411_1',
  'P411-02': 'P411_2',
  'P403-loop': 'P403_1',
  'Walking': 'Walking',
}

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

  // Add bus-dropdown items event listeners
  var busItems = document.getElementsByClassName('bus-item');
  for (let i=0; i<busItems.length; i++) {
    const busCheckbox = busItems[i];
    const busItemValue = busCheckbox.name;
    // Set default checkbox as unchecked
    busCheckbox.value = 'false';
    // Add bus-item event listener
    busCheckbox.addEventListener('click', function() {
      handleBusCheckbox(busItemValue, null);
    });
  }

  // Add bus selection event listeners
  document.getElementById('bus-select').addEventListener('click', function() {
    toggleAllBusCheckbox(true);
  });
  document.getElementById('bus-deselect').addEventListener('click', function() {
    toggleAllBusCheckbox(false);
  });

  // Add button event listeners
  document.getElementById('show-overlay').addEventListener('click', function() {
    // Show bus routes
    overlayBusRoutes(true);
  });
  document.getElementById('hide-overlay').addEventListener('click', function() {
    // Hide bus routes
    overlayBusRoutes(false);
  });
}

function overlayBusRoute(busNumber, direction, color, googleMap) {
  const key = busNumber + '_' + direction;
  // Retrieve bus routes via GET request
  if (busPolylines[key] === null) {
    getBusRoute(busNumber, direction).then(function(busRoute) {
      // Build bus route polyline array
      busPolylines[key] = new google.maps.Polyline({
        path: busRoute,
        geodesic: true,
        strokeColor: color,
        strokeOpacity: 1.0,
        strokeWeight: 4,
      });
      const busPolyline = busPolylines[key];
      // Apply polyline overlay on google map
      busPolyline.setMap(googleMap);
    });
  } else {
    const busPolyline = busPolylines[key];
    // Apply polyline overlay on google map
    busPolyline.setMap(googleMap);
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

  // Get latitude and longitude of the marker
  var markerLat = location.lat();
  var markerLng = location.lng();

  // Update latitude and longitude to input fields
  if (activeInput.id === "start-location" || activeInput.id === "end-location") {
    activeInput.value = markerLat + "," + markerLng;
  }
}

function setFocusedInput() {
  // Set latest input field as the active element
  activeInput = document.activeElement;
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

function toggleAllBusCheckbox(isSelected) {
  var busItems = document.getElementsByClassName('bus-item');
  for (let i=0; i<busItems.length; i++) {
    const busCheckbox = busItems[i];
    const busItemValue = busCheckbox.name;
    // Toggle all bus checkboxes
    handleBusCheckbox(busItemValue, isSelected);
  }
}

function handleBusCheckbox(busItemValue, overrideCheck) {
  // Retrieve all bus checkboxes
  const busCheckboxes = document.getElementsByClassName('bus-item');
  const busCheckboxEvent = busCheckboxes[busItemValue];
  // Check if dropdown item is checked
  const busItemChecked = overrideCheck == null ? busCheckboxEvent.value == 'false' : overrideCheck;
  busCheckboxEvent.value = 'true' ? busItemChecked : 'false';
  // Update overlay depending on checkbox
  updateOverlay(busItemValue, busItemChecked);
  if (busItemChecked) {
    // Show element is selected
    busCheckboxEvent.setAttribute('style', 'background-color:lightblue');
  } else {
    // Show element is unselected
    busCheckboxEvent.setAttribute('style', '');
  }
}

function updateOverlay(busNumber, isShown) {
  // Toggle shown overlay
  showOverlays[busNumber] = isShown;
  if (!isHidden)
    showBusRoute(busNumber, isShown);
}

function overlayBusRoutes(isShown) {
  // Iterate through list of shown overlays
  for (var key in showOverlays) {
    // Check if overlay is previously shown
    if (showOverlays[key] == true) {
      // Apply overlay on google map
      showBusRoute(key, isShown);
    }
  }
}

function showBusRoute(key, isShown) {
  const keySplit = key.split('_');
  if (isShown)
    // Show overlay
    overlayBusRoute(keySplit[0], keySplit[1], busRouteColors[key], map);
  else {
    // Hide overlay
    overlayBusRoute(keySplit[0], keySplit[1], busRouteColors[key], null);
  }
}

function routeCallback(routeInfo) {
  // Retrieve routes taken
  routeInfo.forEach(shortestRoute => {
    // Iterate shortest routes
    shortestRoute["Routes"].forEach((route, index) => {
      var routeType = route["Type"];
      routeType = busRouteNames[routeType];
      var routePath = route["Route"];
      // Connect paths if route type is walking
      if (routeType === "Walking") {
        if (index > 0)
          routePath.unshift(shortestRoute["Routes"][index - 1]["Route"].slice(-1)[0]);
        if (index < shortestRoute["Routes"].length - 1)
          routePath.push(shortestRoute["Routes"][index + 1]["Route"][0]);
      }
      // Build shortest route polyline array
      const routePolyline = new google.maps.Polyline({
        path: routePath,
        geodesic: true,
        strokeColor: busRouteColors[routeType],
        strokeOpacity: 1.0,
        strokeWeight: 4,
      });
      // Apply polyline overlay on google map
      routePolyline.setMap(map);
    });

    // Create routes-box and append to directions-panel
    const routesBox = document.createElement("div");
    routesBox.classList.add("routes-box");
    const directionsPanel = document.getElementById("directions-panel");
    directionsPanel.appendChild(routesBox);

    // Create time-wrapper and append to routes-box
    const timeWrapperOuter = document.createElement("div");
    timeWrapperOuter.classList.add("time-wrapper");
    const timeWrapper = document.createElement("div");
    timeWrapper.classList.add("time");
    timeWrapperOuter.appendChild(timeWrapper);
    routesBox.appendChild(timeWrapperOuter);

    // Create start and end time spans and append to time-wrapper
    const startTime = document.createElement("span");
    startTime.classList.add("start-time");
    // startTime.textContent = directions["StartTime"];
    timeWrapper.appendChild(startTime);

    const timeSeparator = document.createElement("span");
    timeSeparator.classList.add("time-separator");
    timeSeparator.textContent = " - ";
    timeWrapper.appendChild(timeSeparator);

    const endTime = document.createElement("span");
    endTime.classList.add("end-time");
    // endTime.textContent = directions["EndTime"];
    timeWrapper.appendChild(endTime);

    // Create duration span and append to time-wrapper
    const duration = document.createElement("span");
    duration.classList.add("duration");
    // duration.textContent = directions["Duration"];
    timeWrapper.appendChild(duration);

    // Create details button and append to routes-box
    const detailsBtn = document.createElement("button");
    detailsBtn.classList.add("details-btn");
    detailsBtn.textContent = "Details";
    routesBox.appendChild(detailsBtn);

    // Create selected-route div and append to directions-panel
    const selectedRoute = document.createElement("div");
    selectedRoute.classList.add("selected-route");
    selectedRoute.style.display = "none";
    directionsPanel.appendChild(selectedRoute);

    // Add click event listener to details button
    detailsBtn.addEventListener("click", () => {
      // Hide all selected-route divs
      const selectedRoutes = document.querySelectorAll(".selected-route");
      selectedRoutes.forEach(selectedRoute => {
        selectedRoute.style.display = "none";
      });
      // Show selected-route for this details button
      selectedRoute.innerHTML = "";
      const directionsList = document.createElement("ol");
      selectedRoute.appendChild(directionsList);
      shortestRoute["Routes"].forEach(step => {
        const directionStep = document.createElement("li");
        directionStep.textContent = step["Start"] + " => " + step["End"];
        directionsList.appendChild(directionStep);
      });
      selectedRoute.style.display = "block";
    });
  })
}


