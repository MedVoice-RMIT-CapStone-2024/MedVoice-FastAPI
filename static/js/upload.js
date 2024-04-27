document.getElementById("submitBtn").addEventListener("click", function () {
    // Change the button color to red   
    this.classList.remove("bg-blue-500", "hover:bg-blue-700");
    this.classList.add("bg-red-500", "hover:bg-red-700");

    var file = document.getElementById("audioUpload").files[0];
    var formData = new FormData();
    formData.append("file", file);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload", true);
    xhr.onload = function () {
        if (xhr.status == 200) {
            // Display a success notification
            alert('Upload Successful!');
            // Get the transcription field
            var transcriptionField = document.getElementById("transcription");
            var data = JSON.parse(xhr.responseText);
            setTimeout(function () {
                var cleanedData = data.output.replace(/\x1b\[[0-9;]*m/g, "");
                var jsonData = JSON.parse(cleanedData);
                transcriptionField.value = "Language: " + jsonData.language + ", Number of speakers: " + jsonData.num_speakers + "\n, Segments: " + jsonData.segments;
            }, 2000); // Wait for 2 seconds before displaying the protocol data
        } else {
            alert("Upload failed!");
        }
    };
    xhr.send(formData);
});