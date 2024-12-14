function populateNurseTable(nurses) {
    const tableBody = document.getElementById('nurse-table-body');
    tableBody.innerHTML = '';

    nurses.forEach(nurse => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="py-2 px-4 border-b">${nurse.id}</td>
            <td class="py-2 px-4 border-b">${nurse.name}</td>
            <td class="py-2 px-4 border-b">${nurse.email}</td>
            <td class="py-2 px-4 border-b">
                <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded mr-2" onclick="editNurse(${nurse.id}, '${nurse.name}', '${nurse.email}')">Edit</button>
                <button class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded" onclick="deleteNurse(${nurse.id})">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function populatePatientTable(patients) {
    const tableBody = document.getElementById('patient-table-body');
    tableBody.innerHTML = '';

    patients.forEach(patient => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="py-2 px-4 border-b">${patient.id}</td>
            <td class="py-2 px-4 border-b">${patient.patient_name}</td>
            <td class="py-2 px-4 border-b">${patient.patient_age}</td>
            <td class="py-2 px-4 border-b">${patient.patient_gender}</td>
            <td class="py-2 px-4 border-b">${patient.nurse_id}</td>
            <td class="py-2 px-4 border-b">
                <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded mr-2" onclick="editPatient(${patient.id}, '${patient.patient_name}', ${patient.patient_age}, '${patient.patient_gender}', ${patient.nurse_id})">Edit</button>
                <button class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded" onclick="deletePatient(${patient.id})">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}
