document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const chatBox = document.getElementById('chat-box');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    console.log("CSRF Token:", csrftoken); // CSRFトークンをコンソールに出力して確認

    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const userMessage = document.getElementById('message').value;
        if (userMessage.trim() === '') return;

        // Display user message in chat box
        const userMessageDiv = document.createElement('div');
        userMessageDiv.classList.add('message', 'user');
        userMessageDiv.textContent = `You: ${userMessage}`;
        chatBox.appendChild(userMessageDiv);

        // Clear the input field
        document.getElementById('message').value = '';

        try {
            const response = await fetch('/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken
                },
                body: new URLSearchParams({ message: userMessage })
            });

            const result = await response.json();
            const chatgptResponse = result.response;

            // Display ChatGPT response in chat box
            const chatgptMessageDiv = document.createElement('div');
            chatgptMessageDiv.classList.add('message', 'chatgpt');
            chatgptMessageDiv.innerHTML = chatgptResponse.replace(/\n/g, '<br>');
            chatBox.appendChild(chatgptMessageDiv);

            chatBox.scrollTop = chatBox.scrollHeight;
        } catch (error) {
            console.error('Error:', error);
        }
    });

})