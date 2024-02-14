function initMap() {
    const origin = {lat: 44.9727, lng: -93.23540000000003};
    const map = new google.maps.Map(document.getElementById("map"), {
      zoom: 18,
      center: origin,
    });
  
    new ClickEventHandler(map, origin);
  }