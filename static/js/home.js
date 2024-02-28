window.addEventListener("load", ()=> {
    document.getElementById("curr-location").addEventListener("click", getLocation);
});

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(setPosition);
    } else {
        document.getElementById("create-lat").value="0";
        document.getElementById("create-long").value="0";
        document.getElementById("sort-form").submit();
    }
}

function setPosition(pos) {
    document.getElementById("create-lat").value=pos.coords.latitude;
    document.getElementById("create-long").value=pos.coords.longitude;
    document.getElementById("sort-form").submit();
}

function formatTime(isoString) {
    const date = new Date(isoString);
    return date.getFullYear() + '-' +
           String(date.getMonth() + 1).padStart(2, '0') + '-' +
           String(date.getDate()).padStart(2, '0') + ' ' +
           String(date.getHours()).padStart(2, '0') + ':' +
           String(date.getMinutes()).padStart(2, '0');
}

window.addEventListener("load", ()=> {
    document.querySelectorAll('.post-date').forEach(element => {
        const originalTime = element.textContent;
        const formattedTime = formatTime(originalTime);
        element.textContent = formattedTime;
    });
    document.getElementById("curr-location").addEventListener("click", getLocation);
});
