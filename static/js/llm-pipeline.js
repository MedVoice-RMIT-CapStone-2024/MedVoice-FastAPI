document.getElementById('audioForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var fileId = document.getElementById('fileId').value;
    var fileExtension = document.getElementById('fileExtension').value;
    var userId = document.getElementById('userId').value;
    var fileName = document.getElementById('fileName').value;

    const url = new URL(`https://medvoice-fastapi.ngrok.dev/process_audio_v2/${userId}`);

    if (fileId) url.searchParams.append('file_id', fileId);
    if (fileExtension) url.searchParams.append('file_extension', fileExtension);
    if (fileName) url.searchParams.append('file_name', fileName);

    processAudioRequest(url);
});

function processAudioRequest(url) {
    fetch(url, { method: 'POST' })
        .then(response => response.json())
        .then(data => createTaskRow(data))
        .catch(error => {
            console.error('Error processing audio:', error);
            alert('An error occurred while processing the audio.');
        });
}

function createTaskRow(data) {
    const tr = document.createElement('tr');
    const td1 = document.createElement('td');
    const td2 = document.createElement('td');
    
    td1.textContent = data.task_id;
    td1.className = "border px-6 py-4";
    
    td2.className = "border px-6 py-4";
    
    const checkStatusButton = createCheckStatusButton(data.task_id);
    td2.appendChild(checkStatusButton);
    
    tr.appendChild(td1);
    tr.appendChild(td2);
    document.getElementById('taskTable').getElementsByTagName('tbody')[0].appendChild(tr);
}

function createCheckStatusButton(taskId) {
    const button = document.createElement('button');
    button.textContent = 'Check Status';
    button.className = "bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded text-lg";
    
    button.addEventListener('click', () => checkTaskStatus(taskId, button));
    
    return button;
}

function checkTaskStatus(taskId, button) {
    fetch('https://medvoice-fastapi.ngrok.dev/get_audio_task/' + taskId)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'SUCCESS') {
                handleSuccessStatus(data, button);
            } else {
                alert('Task Status: ' + data.status);
            }
        })
        .catch(error => {
            console.error('Error fetching task result:', error);
            alert('An error occurred. Please try again.');
        });
}

function handleSuccessStatus(data, button) {
    button.textContent = 'Done';
    createJsonModal(data.llama3_json_output);
}

function createJsonModal(jsonData) {
    const modal = createModalStructure();
    const modalContent = createModalContent();
    const closeButton = createCloseButton(modal);
    const table = createJsonTable(jsonData);
    const viewAsTextBtn = createViewAsTextButton(jsonData, table);
    
    modalContent.appendChild(closeButton);
    modalContent.appendChild(table);
    modalContent.appendChild(viewAsTextBtn);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
}

// Helper functions for modal creation
function createModalStructure() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full';
    modal.id = 'jsonModal';
    return modal;
}

function createModalStructure() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full';
    modal.id = 'jsonModal';
    return modal;
}

function createModalContent() {
    const modalContent = document.createElement('div');
    modalContent.className = 'relative top-20 mx-auto p-5 border w-4/5 shadow-lg rounded-md bg-white';
    return modalContent;
}

function createCloseButton(modal) {
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '×';
    closeButton.className = 'absolute right-2 top-2 text-gray-600 text-2xl font-bold hover:text-gray-900';
    closeButton.onclick = () => modal.remove();
    return closeButton;
}

function createJsonTable(jsonData) {
    const table = document.createElement('table');
    table.className = 'min-w-full bg-white border border-gray-300';
    createTableFromJSON(jsonData, table.createTBody());
    return table;
}

function createTableFromJSON(obj, parent, indent = 0) {
    for (let key in obj) {
        const tr = document.createElement('tr');
        const tdKey = document.createElement('td');
        const tdValue = document.createElement('td');
        
        tdKey.className = 'px-4 py-2 border border-gray-300 font-semibold';
        tdValue.className = 'px-4 py-2 border border-gray-300';
        
        tdKey.style.paddingLeft = `${indent * 20}px`;
        tdKey.textContent = key;
        
        if (typeof obj[key] === 'object' && obj[key] !== null) {
            parent.appendChild(tr);
            tr.appendChild(tdKey);
            tr.appendChild(tdValue);
            createTableFromJSON(obj[key], parent, indent + 1);
        } else {
            tdValue.textContent = obj[key];
            parent.appendChild(tr);
            tr.appendChild(tdKey);
            tr.appendChild(tdValue);
        }
    }
}

function createViewAsTextButton(jsonData, table) {
    const viewAsTextBtn = document.createElement('button');
    viewAsTextBtn.textContent = 'View as Text';
    viewAsTextBtn.className = 'mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded';
    
    viewAsTextBtn.onclick = () => {
        const formattedText = JSON.stringify(jsonData, null, 2);
        const textArea = document.createElement('textarea');
        textArea.value = formattedText;
        textArea.className = 'w-full h-96 mt-4 p-2 font-mono text-sm border rounded';
        textArea.readOnly = true;
        
        table.replaceWith(textArea);
        viewAsTextBtn.textContent = 'View as Table';
        viewAsTextBtn.onclick = () => {
            textArea.replaceWith(table);
            viewAsTextBtn.textContent = 'View as Text';
            viewAsTextBtn.onclick = () => viewAsTextBtn.click();
        };
    };
    
    return viewAsTextBtn;
}

