document.getElementById("picovoiceSubmitBtn").addEventListener("click", function () {
    // Change the button color to red   
    this.classList.remove("bg-blue-500", "hover:bg-blue-700");
    this.classList.add("bg-red-500", "hover:bg-red-700");

    // Get the user ID and audio file name fields
    var userIdField = document.getElementById("userId");
    var audioFileNameField = document.getElementById("picovoiceAudioUpload");

    // Create a new FormData object
    var formData = new FormData();

    // Append the user ID and audio file name to the form data
    formData.append("user_id", String(userIdField.value));
    formData.append("file_name", String(audioFileNameField.value));

    // Create a new XMLHttpRequest
    var xhr = new XMLHttpRequest();

    // Initialize a POST request with query parameters
    xhr.open("POST", "/process_audio?user_id=" + encodeURIComponent(String(userIdField.value)) + "&file_name=" + encodeURIComponent(String(audioFileNameField.value)));

    // Get the transcription field
    var transcriptionField = document.getElementById("picovoiceTranscription");
    transcriptionField.value = "Transcribing...";

    // Get the spinner and show it
    var spinner = document.getElementById("spinner");
    spinner.style.display = "block";

    xhr.onload = function () {
        if (xhr.status == 200) {
            // Hide the spinner
            spinner.style.display = "none";
            // Parse the response data
            var data = JSON.parse(xhr.responseText);

            // Check if the data is as expected
            if (data && data.sentences_v2) {
                var sentences_v2 = data.sentences_v2;
                var sentenceTexts = sentences_v2.map(function (sentence_info) {
                    return '["start_sec": ' + sentence_info.start_sec + ', "end_sec": ' + sentence_info.end_sec + '] Speaker ' + sentence_info.speaker_tag + ': ' + sentence_info.sentence;
                }).join("\n");
                transcriptionField.value = sentenceTexts;
            } else {

                transcriptionField.value = "Unexpected response format!";
            }
        } else {
            // Hide the spinner
            spinner.style.display = "none";
            transcriptionField.value = "Upload failed with status: " + xhr.status;
        }
    };

    xhr.onerror = function () {
        transcriptionField.value = "Request failed!";
    };

    // Send the form data
    xhr.send(formData);
});