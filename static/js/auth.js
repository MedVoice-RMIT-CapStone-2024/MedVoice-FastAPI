document.getElementById('signupButton').addEventListener('click', async function () {
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;

    try {
        const response = await fetch(`${apiUrl}nurses/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Signup failed');
        }

        if (data.detail) {
            alert(data.detail);
        } else {
            alert('Signup successful');
            closeModal('signupModal');
            // Refresh the nurses table
            await fetchNurses();
        }
    } catch (error) {
        console.error('Error during signup:', error);
        alert(error.message || 'An error occurred during signup. Please try again.');
    }
});

document.getElementById('loginButton').addEventListener('click', async function () {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${apiUrl}nurses/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        if (data.detail) {
            alert(data.detail);
        } else {
            alert('Login successful\nNurse ID: ' + data.nurse_id);
            closeModal('loginModal');
            // Refresh the nurses table
            await fetchNurses();
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert(error.message || 'An error occurred during login. Please try again.');
    }
});
