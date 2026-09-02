const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const messages = document.getElementById("messages");
const welcome = document.getElementById("welcome");
const newChatBtn = document.getElementById("newChatBtn");
const clearBtn = document.getElementById("clearBtn");
const mobileMenuBtn = document.getElementById("mobileMenuBtn");
const sidebar = document.querySelector(".sidebar");

function addMessage(text, type) {
  welcome.style.display = "none";

  const row = document.createElement("div");
  row.className = `message-row ${type === "user" ? "user" : ""}`;

  const bubble = document.createElement("div");
  bubble.className = `message ${type}`;

  if (type === "ai") {
    const label = document.createElement("div");
    label.className = "ai-label";
    label.textContent = "StudyMind AI";
    bubble.appendChild(label);
  }

  const content = document.createElement("div");
  content.textContent = text;
  bubble.appendChild(content);

  row.appendChild(bubble);
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
}

function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";
  input.style.height = "auto";

  // Temporary frontend response.
  // Later this will be replaced by a real AI API call.
  setTimeout(() => {
    addMessage(
      "Thanks! I received your question. The AI backend will be connected here next. For now, this is a frontend demo of the StudyMind conversation flow.",
      "ai"
    );
  }, 500);
}

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 130) + "px";
});

document.querySelectorAll(".suggestions button").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.prompt;
    input.focus();
  });
});

newChatBtn.addEventListener("click", () => {
  messages.innerHTML = "";
  messages.appendChild(welcome);
  welcome.style.display = "block";
  input.value = "";
});

clearBtn.addEventListener("click", () => {
  messages.innerHTML = "";
  messages.appendChild(welcome);
  welcome.style.display = "block";
});

mobileMenuBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
});
