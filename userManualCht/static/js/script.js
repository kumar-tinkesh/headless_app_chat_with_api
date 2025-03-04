document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed.");

    const chatPopup = document.getElementById("chatPopup");
    const chatToggleButton = document.getElementById("chatToggleButton");
    const closeChat = document.getElementById("closeChat");
    const queryInput = document.getElementById("queryInput");
    const chatBox = document.getElementById("chatBox");
    const submitButton = document.getElementById("submitButton");

    console.log("Chat elements initialized.");

    // Toggle chat popup visibility
    chatToggleButton.addEventListener("click", function () {
        chatPopup.style.display = chatPopup.style.display === "block" ? "none" : "block";
        console.log(`Chat popup toggled: ${chatPopup.style.display}`);
    });

    // Close chat popup
    closeChat.addEventListener("click", function () {
        chatPopup.style.display = "none";
        console.log("Chat popup closed.");
    });

    submitButton.addEventListener("click", sendQuery);

    async function sendQuery() {
        const query = queryInput.value.trim();
        if (!query) {
            console.warn("Empty query. No message sent.");
            return;
        }

        console.log(`User input: ${query}`);
        appendMessage(query, "user-message");

        try {
            console.log("Sending request to server...");
            const response = await fetch("/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query })
            });

            console.log("Response received from server.");
            const data = await response.json();
            const botResponse = data["Model Response"] || "No response from server.";
            console.log(`Bot response: ${botResponse}`);

            appendFormattedMessage(botResponse);
        } catch (error) {
            console.error("Error fetching response:", error);
            appendMessage("Error fetching response.", "bot-message");
        }

        queryInput.value = "";
        console.log("Query input cleared.");
    }

    function appendMessage(message, className) {
        console.log(`Appending message: ${message} (Class: ${className})`);
        const messageElement = document.createElement("div");
        messageElement.classList.add("chat-message", className);
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);

        // Ensure the latest message is visible
        setTimeout(() => {
            messageElement.scrollIntoView({ behavior: "smooth", block: "end" });
            console.log("Scrolled to new message.");
        }, 100);
    }

    function appendFormattedMessage(responseText) {
        console.log(`Appending formatted bot response.`);
        const messageElement = document.createElement("div");
        messageElement.classList.add("chat-message", "bot-message");
        messageElement.innerHTML = formatResponse(responseText);
        chatBox.appendChild(messageElement);

        // Ensure the latest message is visible
        setTimeout(() => {
            messageElement.scrollIntoView({ behavior: "smooth", block: "end" });
            console.log("Scrolled to bot response.");
        }, 100);
    }

    function formatResponse(responseText) {
        console.log("Formatting bot response.");
        responseText = responseText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        responseText = responseText.replace(/(<li>.*?<\/li>)+/g, "<ul>$&</ul>");
        responseText = responseText.replace(/\n+/g, "\n").replace(/\n(?!<\/?(ul|li)>)/g, "<br>");
        return responseText;
    }
});
