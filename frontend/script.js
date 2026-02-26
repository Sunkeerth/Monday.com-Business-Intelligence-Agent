// const API_URL = "https://monday-com-business-intelligence-agent.onrender.com";
//   // Change to deployed URL later
const API_URL = "https://monday-com-business-intelligence-agent.onrender.com/chat";
let chartInstance = null;

async function sendMessage() {
    const input = document.getElementById('user-input');
    const msg = input.value.trim();
    if (!msg) return;

    // Display user message
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML += `<div class="message user">You: ${msg}</div>`;
    input.value = '';

    // Scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;

    // Call backend
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg})
    });
    const data = await response.json();

    // Display bot answer
    chatBox.innerHTML += `<div class="message bot">Bot: ${data.answer}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    // Speak the answer
    speak(data.answer);

    // Display trace
    const traceDiv = document.getElementById('trace');
    traceDiv.innerHTML = '<h3>🔍 Action Trace</h3><ul>' + 
        data.trace.map(t => `<li>${t}</li>`).join('') + '</ul>';

    // Display chart if available
    if (data.chart) {
        renderChart(data.chart.labels, data.chart.values);
    } else {
        // Hide chart container
        document.getElementById('chart-container').style.display = 'none';
    }
}

function speak(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 1;
        utterance.pitch = 1;
        window.speechSynthesis.cancel(); // Stop any ongoing speech
        window.speechSynthesis.speak(utterance);
    } else {
        console.log('Speech synthesis not supported');
    }
}

function renderChart(labels, values) {
    const ctx = document.getElementById('myChart').getContext('2d');
    if (chartInstance) {
        chartInstance.destroy();
    }
    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Count',
                data: values,
                backgroundColor: 'rgba(26, 74, 128, 0.6)',
                borderRadius: 8,
                barPercentage: 0.7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { 
                    beginAtZero: true,
                    grid: { color: '#e0e9f2' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
    document.getElementById('chart-container').style.display = 'block';
}

// Allow Enter key to send
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});