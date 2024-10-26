function initMap(userPosition) {
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

    if (userPosition) {
        var marker = new google.maps.marker.AdvancedMarkerElement({
            position: userPosition,
            map: map,
            title: "Your Location",
            content: new google.maps.marker.PinElement({
                glyph: "★",
                scale: 1.5
            }).element
        });
        bounds.extend(marker.position);

        marker.addListener('click', function() {
            infoWindow.setContent('<h5>Your Location</h5>');
            infoWindow.open(map, marker);
        });

        setTimeout(() => {
            map.setCenter(userPosition);
            map.setZoom(15);
        }, 100);
    } else {
        map.fitBounds(bounds);
    }
}

window.onload = initMap();
