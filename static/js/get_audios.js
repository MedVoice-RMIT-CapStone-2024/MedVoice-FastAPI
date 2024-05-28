document.getElementById('searchBtn').addEventListener('click', function () {
    // Change the button color to red   
    this.classList.remove("bg-blue-500", "hover:bg-blue-700");
    this.classList.add("bg-red-500", "hover:bg-red-700");
    // Get the user ID from the input field
    var userId = document.getElementById('user_id').value;

    // Create a new XMLHttpRequest
    var xhr = new XMLHttpRequest();

    // Configure the request
    xhr.open('GET', '/get_audio/' + userId, true);

    xhr.onload = function () {
        if (xhr.status == 200) {
            // On successful response, parse the JSON response and display the URLs in the textarea
            var data = JSON.parse(xhr.responseText);
            document.getElementById('audioURL').value = data.urls.join('\n');
        } else {
            // On failed response, display an error message
            document.getElementById('audioURL').value = 'Error: ' + xhr.status;
        }
    };

    // Send the request
    xhr.send();
});
