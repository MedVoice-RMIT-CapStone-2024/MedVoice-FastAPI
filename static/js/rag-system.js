document.getElementById('ask-button').addEventListener('click', async function() {
    const userId = document.getElementById('user-id').value;
    const question = document.getElementById('question').value;
    const sourceType = document.getElementById('source-type').value;
    const spinner = document.getElementById('rag-spinner');
    
    spinner.style.display = 'block';
    this.style.display = 'none';

    const endpoint = `ask_v2/${userId}`;

    try {
        const response = await fetch(`https://medvoice-fastapi.ngrok.dev/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question, source_type: sourceType }),
        });
        const data = await response.json();
        const conversation = document.getElementById('conversation');
        conversation.value += 'User: ' + question + '\n';
        conversation.value += 'RAG System: ' + data.response + '\n\n';
        document.getElementById('question').value = '';
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        spinner.style.display = 'none';
        this.style.display = 'block';
    }
});
