const API = "http://127.0.0.1:8000";

function addMessage(text, sender) {
    const div = document.createElement("div");
    div.classList.add("message", sender);
    div.innerText = text;
    return div;
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    const chatBox = document.getElementById("chat-box");
    const loading = document.getElementById("loading");
    if (!text) return;
    // Show user message, then show loading indicator while waiting for bot response1   
    chatBox.insertBefore(addMessage("You: " + text, "user"), loading);
    input.value = "";
    
    loading.style.display = "block";
    chatBox.scrollTop = chatBox.scrollHeight;
    try {
        const res = await fetch(`${API}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const data = await res.json();
        chatBox.insertBefore(addMessage("Assistant: " + data.reply, "bot"), loading);
        
    } catch (err) {
        addMessage("Cannot connect to backend", "bot");
    } finally {
        // Hide loading indicator after response is received or if there's an error
        loading.style.display = "none";
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}