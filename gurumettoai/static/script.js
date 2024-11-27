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

    function displaySuggestion() {
        fetch('/suggest-restaurant-with-reviews/') // 上記のビューにリクエストを送信
            .then(response => response.json())
            .then(data => {
                const chatBox = document.getElementById('chatBox'); // チャットエリア
                if (data.error) {
                    chatBox.innerHTML += `<p>${data.error}</p>`;
                } else {
                    const restaurant = data.suggested_restaurant;
                    const details = data.details;
    
                    chatBox.innerHTML += `
                        <div>
                            <h3>おすすめ: ${restaurant}</h3>
                            <p>評価: ${details.rating || "情報なし"}</p>
                            <h4>口コミ:</h4>
                            <ul>
                                ${details.reviews
                                    ? details.reviews
                                          .map(
                                              review =>
                                                  `<li>${review.author_name}: ${review.text} (評価: ${review.rating})</li>`
                                          )
                                          .join('')
                                    : '<li>口コミ情報がありません。</li>'}
                            </ul>
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
    
});
