document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const chatBox = document.getElementById('chat-box');

    chatForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const userMessage = document.getElementById('message').value.trim();
        if (!userMessage) return;

        // ユーザーのメッセージを表示
        const userMessageDiv = document.createElement('div');
        userMessageDiv.classList.add('message', 'user');
        userMessageDiv.textContent = userMessage; // ユーザーのメッセージをそのまま表示
        chatBox.appendChild(userMessageDiv);

        document.getElementById('message').value = '';

        // AIの応答を取得
        try {
            const response = await fetch('/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    message: userMessage
                })
            });

            const result = await response.json();
            const aiMessage = result.response;

            const aiMessageDiv = document.createElement('div');
            aiMessageDiv.classList.add('message', 'chatgpt');
            aiMessageDiv.innerHTML = aiMessage; // HTMLを直接レンダリング
            chatBox.appendChild(aiMessageDiv);

            chatBox.scrollTop = chatBox.scrollHeight; // スクロールを最下部に
        } catch (error) {
            console.error('Error:', error);
        }
    });
});