document.getElementById("submitBtn").addEventListener("click", function () {
    var file = document.getElementById("audioUpload").files[0];
    var formData = new FormData();
    formData.append("file", file);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload", true);
    xhr.onload = function () {
        if (xhr.status == 200) {
            var data = JSON.parse(xhr.responseText);
            document.getElementById("transcription").value = data.protocol;
        } else {
            alert("Upload failed!");
        }
    };
    xhr.send(formData);
});