// Nurse CRUD operations
function editNurse(id, name, email) {
    document.getElementById('editNurseId').value = id;
    document.getElementById('editNurseName').value = name;
    document.getElementById('editNurseEmail').value = email;
    openEditNurseModal();
}

async function updateNurse() {
    const id = document.getElementById('editNurseId').value;
    const name = document.getElementById('editNurseName').value;
    const email = document.getElementById('editNurseEmail').value;

    const nurse = { name, email };

    try {
        await fetch(`${apiUrl}nurses/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(nurse)
        });
        fetchNurses();
        closeEditNurseModal();
    } catch (error) {
        console.error('Error updating nurse:', error);
    }
}

async function deleteNurse(id) {
    if (!confirm('Are you sure you want to delete this nurse?')) return;

    try {
        await fetch(`${apiUrl}nurses/${id}`, { method: 'DELETE' });
        fetchNurses();
    } catch (error) {
        console.error('Error deleting nurse:', error);
    }
}

// Patient CRUD operations
async function createPatient() {
    const name = document.getElementById('createPatientName').value;
    const age = document.getElementById('createPatientAge').value;
    const gender = document.getElementById('createPatientGender').value;
    const nurseId = document.getElementById('createPatientNurseId').value;

    const patient = { patient_name: name, patient_age: age, patient_gender: gender, nurse_id: nurseId };

    try {
        await fetch(`${apiUrl}patients/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(patient)
        });
        fetchPatients();
        closeCreatePatientModal();
    } catch (error) {
        console.error('Error creating patient:', error);
    }
}

function editPatient(id, name, age, gender, nurseId) {
    document.getElementById('editPatientId').value = id;
    document.getElementById('editPatientName').value = name;
    document.getElementById('editPatientAge').value = age;
    document.getElementById('editPatientGender').value = gender;
    document.getElementById('editPatientNurseId').value = nurseId;
    openEditPatientModal();
}

async function updatePatient() {
    const id = document.getElementById('editPatientId').value;
    const name = document.getElementById('editPatientName').value;
    const age = document.getElementById('editPatientAge').value;
    const gender = document.getElementById('editPatientGender').value;
    const nurseId = document.getElementById('editPatientNurseId').value;

    const patient = { patient_name: name, patient_age: age, patient_gender: gender, nurse_id: nurseId };

    try {
        await fetch(`${apiUrl}patients/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(patient)
        });
        fetchPatients();
        closeEditPatientModal();
    } catch (error) {
        console.error('Error updating patient:', error);
    }
}

async function deletePatient(id) {
    if (!confirm('Are you sure you want to delete this patient?')) return;

    try {
        await fetch(`${apiUrl}patients/${id}`, { method: 'DELETE' });
        fetchPatients();
    } catch (error) {
        console.error('Error deleting patient:', error);
    }
}
