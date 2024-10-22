function initMap() {
    var map = new google.maps.Map(document.getElementById('map'), {
        mapTypeId: 'roadmap'
    });
    var heatmapData = locations_data.map(location => ({
        location: new google.maps.LatLng(location.lat, location.lng),
        weight: location.count
    }));
    var heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatmapData,
        radius: 30,
        opacity: 0.6,
        map: map
    });
    var bounds = new google.maps.LatLngBounds();
    locations_data.forEach(location => {
        var marker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            label: String(location.count),
        });
        bounds.extend(marker.getPosition());
    });
    map.fitBounds(bounds);
}

window.onload = initMap;
