const apiUrl = 'https://medvoice-fastapi.ngrok.dev/';

async function fetchNurses() {
    try {
        const response = await fetch(`${apiUrl}nurses/`);
        const nurses = await response.json();
        populateNurseTable(nurses);
    } catch (error) {
        console.error('Error fetching nurses:', error);
    }
}

async function fetchPatients() {
    try {
        const response = await fetch(`${apiUrl}patients/`);
        const patients = await response.json();
        populatePatientTable(patients);
    } catch (error) {
        console.error('Error fetching patients:', error);
    }
}

async function fetchPatientsByNurse() {
    const nurseId = document.getElementById('nurseIdFilter').value;

    if (!nurseId) {
        alert('Please enter a Nurse ID');
        return;
    }

    try {
        const response = await fetch(`${apiUrl}patients/nurse/${nurseId}`);
        const patients = await response.json();
        populatePatientTable(patients);
    } catch (error) {
        console.error('Error fetching patients by nurse:', error);
    }
}
