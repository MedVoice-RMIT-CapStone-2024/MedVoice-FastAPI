document.getElementById("picovoiceSubmitBtn").addEventListener("click", function () {
    // Change the button color to red   
    this.classList.remove("bg-blue-500", "hover:bg-blue-700");
    this.classList.add("bg-red-500", "hover:bg-red-700");

    var file = document.getElementById("picovoiceAudioUpload").files[0];
    var formData = new FormData();
    formData.append("file", file);
    var xhr = new XMLHttpRequest();

    xhr.open("POST", "/process_audio", true);

    // Get the transcription field
    var transcriptionField = document.getElementById("picovoiceTranscription");
    transcriptionField.value = "Transcribing...";
    xhr.onload = function () {
        if (xhr.status == 200) {
            // Display a success notification
            alert('Upload Successful!');
            var data = JSON.parse(xhr.responseText);
            setTimeout(function () {
                var sentences_v2 = data.sentences_v2;
                var sentenceTexts = sentences_v2.map(function (sentence_info) {
                    return '["start_sec": ' + sentence_info.start_sec + ', "end_sec": ' + sentence_info.end_sec + '] Speaker ' + sentence_info.speaker_tag + ': ' + sentence_info.sentence;
                }).join("\n");
                transcriptionField.value = sentenceTexts;
            }, 1000); // Wait for 1 seconds before displaying the protocol data
        } else {
            transcriptionField.value = "Upload failed!";
        }
    };
    xhr.send(formData);
});