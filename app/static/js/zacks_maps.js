function initialize(la_data,lo_data) {
  var mapDiv = document.getElementById('map-canvas');
        var map = new google.maps.Map(mapDiv, {
          center: new google.maps.LatLng(37.7563659, -122.4496905),
          zoom: 12,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        });
      
        var infoWindow = new google.maps.InfoWindow({
          position: new google.maps.LatLng(la_data, lo_data),
          content: 'THIS IS WHERE YOUR SEARCH APPEARED'
        });
        infoWindow.open(map);

        
      }
      
    

      google.maps.event.addDomListener(window, 'load', initialize);