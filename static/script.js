function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessage(message, 'user-message');
    input.value = '';
    
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        addMessage(data.response, 'bot-message');
        
        // Check if graph data is included
        if (data.graph_data) {
            addGraphToChat(data.graph_data);
        }
    })
    .catch(error => {
        addMessage('Sorry, something went wrong. Please try again.', 'bot-message');
    });
}

function addMessage(text, className) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.innerHTML = `<p>${text}</p>`;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

let aqiChart = null;

function addGraphToChat(graphData) {
    const chatContainer = document.getElementById('chatContainer');
    
    // Create canvas container
    const graphDiv = document.createElement('div');
    graphDiv.className = 'message bot-message graph-message';
    graphDiv.innerHTML = '<canvas id="aqiChart" width="400" height="200"></canvas>';
    chatContainer.appendChild(graphDiv);
    
    // Prepare data for chart
    const pastData = graphData.past || [];
    const futureData = graphData.future || [];
    
    const labels = [
        ...pastData.map(d => d.day_name.substring(0, 3)),
        'Today',
        ...futureData.map(d => d.day_name.substring(0, 3))
    ];
    
    const values = [
        ...pastData.map(d => d.aqi),
        null, // Today placeholder
        ...futureData.map(d => d.aqi)
    ];
    
    // Destroy existing chart if any
    if (aqiChart) {
        aqiChart.destroy();
    }
    
    // Create chart
    const ctx = document.getElementById('aqiChart').getContext('2d');
    aqiChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'AQI',
                data: values,
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointHoverRadius: 7,
                segment: {
                    borderDash: ctx => {
                        // Dashed line for future predictions
                        const index = ctx.p0DataIndex;
                        return index >= pastData.length ? [5, 5] : [];
                    }
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            const aqi = context.parsed.y;
                            label += aqi.toFixed(0);
                            
                            // Add category
                            if (aqi <= 50) label += ' (Good)';
                            else if (aqi <= 100) label += ' (Moderate)';
                            else if (aqi <= 150) label += ' (Unhealthy for Sensitive)';
                            else if (aqi <= 200) label += ' (Unhealthy)';
                            else if (aqi <= 300) label += ' (Very Unhealthy)';
                            else label += ' (Hazardous)';
                            
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 500,
                    ticks: {
                        callback: function(value) {
                            return value;
                        }
                    },
                    grid: {
                        color: function(context) {
                            // Color code the grid based on AQI ranges
                            if (context.tick.value === 50) return 'rgba(0, 255, 0, 0.3)';
                            if (context.tick.value === 100) return 'rgba(255, 255, 0, 0.3)';
                            if (context.tick.value === 150) return 'rgba(255, 165, 0, 0.3)';
                            if (context.tick.value === 200) return 'rgba(255, 0, 0, 0.3)';
                            if (context.tick.value === 300) return 'rgba(128, 0, 128, 0.3)';
                            return 'rgba(0, 0, 0, 0.1)';
                        }
                    }
                }
            }
        }
    });
    
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
