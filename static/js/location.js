window.addEventListener("load", ()=> {
    document.getElementById("curr-location").addEventListener("click", getLocation);
});

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(setPosition);
    } else {
        document.getElementById("create-lat").value="0";
        document.getElementById("create-long").value="0";
    }
}

function setPosition(pos) {
    document.getElementById("create-lat").value=pos.coords.latitude;
    document.getElementById("create-long").value=pos.coords.longitude;
}
