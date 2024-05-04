document.getElementById("picovoiceSubmitBtn").addEventListener("click", function () {
    // Change the button color to red   
    this.classList.remove("bg-blue-500", "hover:bg-blue-700");
    this.classList.add("bg-red-500", "hover:bg-red-700");

    // Get the user ID from the input field
    var user_id = document.getElementById('user_id').value;

    // Get the file from the input field
    var file = document.getElementById("picovoiceAudioUpload").files[0];

    var formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", user_id);

    var xhr = new XMLHttpRequest();

    xhr.open("POST", "/process_audio", true);

    // Get the transcription field
    var transcriptionField = document.getElementById("picovoiceTranscription");
    transcriptionField.value = "Transcribing...";

    xhr.onload = function () {
        if (xhr.status == 200) {
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
            transcriptionField.value = "Upload failed with status: " + xhr.status;
        }
    };

    xhr.onerror = function () {
        transcriptionField.value = "Request failed!";
    };

    xhr.send(formData);

});