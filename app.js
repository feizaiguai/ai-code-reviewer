// AI代码审查器 - Interactive Demo
const features = [
  { icon: "⚡", label: "Fast" }, { icon: "🎨", label: "Beautiful" },
  { icon: "🔧", label: "Functional" }, { icon: "📱", label: "Responsive" },
  { icon: "🧠", label: "Smart" }, { icon: "🔒", label: "Secure" },
];
let actionCount = 0;
let startTime = Date.now();

function init() {
  const container = document.getElementById("features");
  features.forEach((f, i) => {
    const card = document.createElement("div");
    card.className = "card";
    card.style.animationDelay = (i * 0.1) + "s";
    card.innerHTML = `<div class="icon">${f.icon}</div><div class="label">${f.label}</div>`;
    card.onclick = () => {
      actionCount++;
      addOutput(`[${new Date().toLocaleTimeString()}] Feature "${f.label}" activated! (action #${actionCount})`);
      updateStats();
    };
    container.appendChild(card);
  });
  setInterval(updateTimer, 1000);
}

function processInput() {
  const input = document.getElementById("userInput");
  const text = input.value.trim();
  if (!text) return;
  actionCount++;
  const len = text.length;
  const words = text.split(/\s+/).length;
  const upper = text.toUpperCase();
  const reversed = text.split("").reverse().join("");
  addOutput(`Input: "${text}"\nLength: ${len} chars, ${words} words\nUppercase: ${upper}\nReversed: ${reversed}`);
  input.value = "";
  updateStats();
}

function addOutput(text) {
  const out = document.getElementById("output");
  out.textContent = text + "\n\n" + out.textContent;
}

function updateStats() {
  document.getElementById("counter").textContent = `${actionCount} actions`;
}

function updateTimer() {
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  document.getElementById("timer").textContent = `${elapsed}s`;
}

document.getElementById("userInput").addEventListener("keypress", e => {
  if (e.key === "Enter") processInput();
});

init();