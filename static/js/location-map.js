function initMap() {
    var locations = locations_data;

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 2,
        center: {lat: 0, lng: 0},
        mapId: "clyde-ryde-map"
    });

    var bounds = new google.maps.LatLngBounds();
    var infoWindow = new google.maps.InfoWindow();

    locations.forEach(function(location) {
        var marker = new google.maps.marker.AdvancedMarkerElement({
            position: {lat: location.lat, lng: location.lng},
            map: map,
            title: location.name
        });
        bounds.extend(marker.position);

        marker.addListener('click', function() {
            var contentString = `<h5><a href="${location.url}">${location.name}</a></h5>
                ${location.address}
            `;
            infoWindow.setContent(contentString);
            infoWindow.open(map, marker);
        });
    });

    map.fitBounds(bounds);
}

window.onload = initMap;
