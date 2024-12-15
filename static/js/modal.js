function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function openEditNurseModal() {
    document.getElementById('editNurseModal').classList.remove('hidden');
}

function closeEditNurseModal() {
    document.getElementById('editNurseModal').classList.add('hidden');
}

function openCreatePatientModal() {
    document.getElementById('createPatientModal').classList.remove('hidden');
}

function closeCreatePatientModal() {
    document.getElementById('createPatientModal').classList.add('hidden');
}

function openEditPatientModal() {
    document.getElementById('editPatientModal').classList.remove('hidden');
}

function closeEditPatientModal() {
    document.getElementById('editPatientModal').classList.add('hidden');
}
