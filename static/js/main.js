// CareCompanion front-end logic.
// Talks to the Flask API for symptom checks, chat, and health tips.

// Symptom vocabulary is loaded from the backend (/api/symptoms) so the UI
// always matches what the ML model understands. This is a fallback list.
let COMMON_SYMPTOMS = [
  "fever", "cough", "sore throat", "runny nose", "nasal congestion", "sneezing",
  "headache", "fatigue", "body aches", "chills", "nausea", "vomiting",
  "diarrhea", "abdominal pain", "shortness of breath", "chest pain", "dizziness",
];

const selectedSymptoms = new Set();

async function loadSymptomVocabulary() {
  try {
    const res = await fetch("/api/symptoms");
    const data = await res.json();
    if (Array.isArray(data.symptoms) && data.symptoms.length) {
      COMMON_SYMPTOMS = data.symptoms;
    }
  } catch (err) {
    // Keep the fallback list if the request fails.
  }
  renderSymptomGrid();
}

// ----- Symptom chips -----
function renderSymptomGrid() {
  const grid = document.getElementById("symptom-grid");
  grid.innerHTML = "";
  COMMON_SYMPTOMS.forEach((symptom) => {
    const label = document.createElement("label");
    label.className = "symptom-chip";
    label.innerHTML = `<input type="checkbox" value="${symptom}" /> ${symptom}`;
    const input = label.querySelector("input");
    input.addEventListener("change", () => {
      if (input.checked) {
        selectedSymptoms.add(symptom);
        label.classList.add("checked");
      } else {
        selectedSymptoms.delete(symptom);
        label.classList.remove("checked");
      }
    });
    grid.appendChild(label);
  });
}

function addCustomSymptom() {
  const field = document.getElementById("custom-symptom");
  const value = field.value.trim().toLowerCase();
  if (!value || selectedSymptoms.has(value)) {
    field.value = "";
    return;
  }
  selectedSymptoms.add(value);

  const grid = document.getElementById("symptom-grid");
  const label = document.createElement("label");
  label.className = "symptom-chip checked";
  label.innerHTML = `<input type="checkbox" value="${value}" checked /> ${value}`;
  const input = label.querySelector("input");
  input.addEventListener("change", () => {
    if (input.checked) {
      selectedSymptoms.add(value);
      label.classList.add("checked");
    } else {
      selectedSymptoms.delete(value);
      label.classList.remove("checked");
    }
  });
  grid.appendChild(label);
  field.value = "";
}

async function analyzeSymptoms() {
  const box = document.getElementById("symptom-result");
  if (selectedSymptoms.size === 0) {
    box.hidden = false;
    box.innerHTML = `<p class="muted">Please select at least one symptom.</p>`;
    return;
  }

  const res = await fetch("/api/symptom-check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symptoms: [...selectedSymptoms] }),
  });
  const data = await res.json();
  renderResult(data);
}

function renderResult(data) {
  const box = document.getElementById("symptom-result");
  box.hidden = false;

  let html = `<span class="urgency ${data.overall_urgency}">Urgency: ${data.overall_urgency.toUpperCase()}</span>`;
  if (data.engine) {
    html += ` <span class="engine-badge">🧠 ${data.engine}</span>`;
  }

  if (data.red_flags && data.red_flags.length) {
    html += `<div class="red-flag">🚨 Warning signs detected (${data.red_flags.join(", ")}).
      These can indicate an emergency — seek immediate care.</div>`;
  }

  if (data.unrecognized_symptoms && data.unrecognized_symptoms.length) {
    html += `<p class="muted note">Not recognized by the model: ${data.unrecognized_symptoms.join(", ")}.</p>`;
  }

  if (data.possible_conditions.length === 0) {
    html += `<p class="muted">The model couldn't match your symptoms to a condition. If symptoms persist, consult a clinician.</p>`;
  } else {
    html += `<h3>AI-ranked possible conditions</h3>`;
    data.possible_conditions.forEach((c) => {
      const pct = Math.round(c.probability * 100);
      const matched = c.matched_symptoms.length ? c.matched_symptoms.join(", ") : "—";
      html += `
        <div class="condition">
          <h4>${c.name} <span class="urgency ${c.urgency}">${c.urgency}</span></h4>
          <div class="confidence-bar"><span style="width:${pct}%"></span></div>
          <small class="muted">Model probability: ${pct}% · matched: ${matched}</small>
          <p>${c.description}</p>
          <p><strong>Guidance:</strong> ${c.self_care}</p>`;
      if (c.reference && c.reference.summary) {
        const link = c.reference.url
          ? ` <a href="${c.reference.url}" target="_blank" rel="noopener">Read more ↗</a>`
          : "";
        html += `
          <div class="reference">
            <span class="reference-source">${c.reference.source}</span>
            <p>${c.reference.summary}${link}</p>
          </div>`;
      }
      html += `</div>`;
    });
  }

  html += `<p class="result-disclaimer">${data.disclaimer}</p>`;
  box.innerHTML = html;
  box.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ----- Chat -----
function appendMessage(text, sender, source) {
  const win = document.getElementById("chat-window");
  const div = document.createElement("div");
  div.className = `msg ${sender}`;
  div.textContent = text;
  if (source) {
    const tag = document.createElement("small");
    tag.className = "msg-source";
    tag.textContent = source;
    div.appendChild(tag);
  }
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}

async function sendChat(event) {
  event.preventDefault();
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (!message) return;

  appendMessage(message, "user");
  input.value = "";

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  const data = await res.json();
  appendMessage(data.reply, "bot", data.source);
}

async function loadAssistantMode() {
  const badge = document.getElementById("assistant-mode");
  if (!badge) return;
  try {
    const res = await fetch("/api/assistant-mode");
    const data = await res.json();
    badge.textContent = data.llm ? "🤖 AI (OpenAI) active" : "💡 Offline rule-based mode";
    badge.classList.toggle("llm-on", !!data.llm);
  } catch (err) {
    badge.textContent = "💡 Offline rule-based mode";
  }
}

// ----- Tips -----
async function loadTips() {
  const res = await fetch("/api/health-tips");
  const data = await res.json();
  const list = document.getElementById("tips-list");
  list.innerHTML = "";
  data.tips.forEach((tip) => {
    const li = document.createElement("li");
    li.textContent = tip;
    list.appendChild(li);
  });
}

// ----- Init -----
document.addEventListener("DOMContentLoaded", () => {
  loadSymptomVocabulary();
  loadTips();
  loadAssistantMode();

  document.getElementById("check-btn").addEventListener("click", analyzeSymptoms);
  document.getElementById("add-symptom").addEventListener("click", addCustomSymptom);
  document.getElementById("custom-symptom").addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addCustomSymptom();
    }
  });
  document.getElementById("chat-form").addEventListener("submit", sendChat);
});
