// Dashboard JavaScript para Monitoramento Suricata
// Autor: Wilker Junio Coelho Pimenta

// Variáveis globais
let charts = {};
let statsUpdateInterval;
let logsEventSource = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    init();
});

function init() {
    updateStatus();
    loadStats();
    loadAlerts();
    loadPhishingAlerts();
    
    // Atualizar stats a cada 30 segundos
    statsUpdateInterval = setInterval(() => {
        loadStats();
        loadAlerts();
        loadPhishingAlerts();
    }, 30000);
    
    // Atualizar status a cada 10 segundos
    setInterval(updateStatus, 10000);
}

// Status do sistema
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const indicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        
        if (data.suricata_running && data.eve_json_exists) {
            indicator.classList.add('active');
            statusText.textContent = 'Suricata Ativo';
        } else {
            indicator.classList.remove('active');
            statusText.textContent = 'Suricata Inativo ou Log não encontrado';
        }
    } catch (error) {
        console.error('Erro ao atualizar status:', error);
        document.getElementById('status-text').textContent = 'Erro ao conectar';
    }
}

// Carregar estatísticas e atualizar gráficos
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Atualizar cards
        document.getElementById('total-alerts').textContent = data.total_alerts.toLocaleString();
        document.getElementById('phishing-alerts').textContent = data.phishing_alerts.toLocaleString();
        document.getElementById('total-flows').textContent = data.total_flows.toLocaleString();
        document.getElementById('total-dns').textContent = data.total_dns.toLocaleString();
        
        // Atualizar gráficos
        updateTimeChart(data.alerts_by_hour);
        updateSeverityChart(data.severity);
        updateSignaturesChart(data.top_signatures);
        updateProtocolsChart(data.protocols);
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// Gráfico de alertas por tempo
function updateTimeChart(data) {
    const ctx = document.getElementById('alertsTimeChart');
    if (!ctx) return;
    
    const labels = Object.keys(data).sort();
    const values = labels.map(label => data[label] || 0);
    
    if (charts.timeChart) {
        charts.timeChart.destroy();
    }
    
    charts.timeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.map(l => {
                const date = new Date(l);
                return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
            }),
            datasets: [{
                label: 'Alertas',
                data: values,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                }
            }
        }
    });
}

// Gráfico de severidade
function updateSeverityChart(data) {
    const ctx = document.getElementById('severityChart');
    if (!ctx) return;
    
    const labels = Object.keys(data).map(s => `Severidade ${s}`);
    const values = Object.values(data);
    const colors = ['#ef4444', '#f59e0b', '#eab308', '#10b981'];
    
    if (charts.severityChart) {
        charts.severityChart.destroy();
    }
    
    charts.severityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 15
                    }
                }
            }
        }
    });
}

// Gráfico de assinaturas top
function updateSignaturesChart(data) {
    const ctx = document.getElementById('signaturesChart');
    if (!ctx) return;
    
    const sorted = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    const labels = sorted.map(([name]) => {
        return name.length > 40 ? name.substring(0, 40) + '...' : name;
    });
    const values = sorted.map(([, count]) => count);
    
    if (charts.signaturesChart) {
        charts.signaturesChart.destroy();
    }
    
    charts.signaturesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ocorrências',
                data: values,
                backgroundColor: '#2563eb',
                borderColor: '#1e40af',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                },
                y: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                }
            }
        }
    });
}

// Gráfico de protocolos
function updateProtocolsChart(data) {
    const ctx = document.getElementById('protocolsChart');
    if (!ctx) return;
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    const colors = ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];
    
    if (charts.protocolsChart) {
        charts.protocolsChart.destroy();
    }
    
    charts.protocolsChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 15
                    }
                }
            }
        }
    });
}

// Carregar alertas gerais
async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts/recent');
        const data = await response.json();
        
        const tbody = document.getElementById('alerts-table-body');
        tbody.innerHTML = '';
        
        if (data.alerts && data.alerts.length > 0) {
            data.alerts.forEach(alert => {
                const row = createAlertRow(alert);
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Nenhum alerta encontrado</td></tr>';
        }
    } catch (error) {
        console.error('Erro ao carregar alertas:', error);
        document.getElementById('alerts-table-body').innerHTML = 
            '<tr><td colspan="6" class="loading">Erro ao carregar alertas</td></tr>';
    }
}

// Carregar alertas de phishing
async function loadPhishingAlerts() {
    try {
        const response = await fetch('/api/phishing');
        const data = await response.json();
        
        const tbody = document.getElementById('phishing-table-body');
        tbody.innerHTML = '';
        
        if (data.alerts && data.alerts.length > 0) {
            data.alerts.forEach(alert => {
                const row = createAlertRow(alert);
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Nenhum alerta de phishing encontrado</td></tr>';
        }
    } catch (error) {
        console.error('Erro ao carregar alertas de phishing:', error);
        document.getElementById('phishing-table-body').innerHTML = 
            '<tr><td colspan="6" class="loading">Erro ao carregar alertas</td></tr>';
    }
}

// Criar linha de alerta na tabela
function createAlertRow(alert) {
    const row = document.createElement('tr');
    
    const timestamp = new Date(alert.timestamp).toLocaleString('pt-BR');
    const severity = alert.severity || 0;
    const severityClass = severity >= 3 ? 'severity-high' : severity >= 2 ? 'severity-medium' : 'severity-low';
    
    row.innerHTML = `
        <td>${timestamp}</td>
        <td>${escapeHtml(alert.signature || 'N/A')}</td>
        <td>${escapeHtml(alert.src_ip || 'N/A')}</td>
        <td>${escapeHtml(alert.dest_ip || 'N/A')}</td>
        <td>${escapeHtml(alert.proto || 'N/A')}</td>
        <td class="${severityClass}">${severity}</td>
    `;
    
    return row;
}

// Função auxiliar para escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Trocar entre tabs
function switchTab(tabName) {
    // Remover active de todas as tabs
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Ativar tab selecionada
    event.target.classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Logs em tempo real
document.getElementById('start-logs')?.addEventListener('click', startLogs);
document.getElementById('stop-logs')?.addEventListener('click', stopLogs);
document.getElementById('clear-logs')?.addEventListener('click', clearLogs);

function startLogs() {
    if (logsEventSource) {
        return;
    }
    
    const logsOutput = document.getElementById('logs-output');
    logsOutput.innerHTML = '<div class="log-entry">Conectando ao stream de logs...</div>';
    
    logsEventSource = new EventSource('/api/logs/stream');
    
    logsEventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.error) {
                logsOutput.innerHTML += `<div class="log-entry">Erro: ${escapeHtml(data.error)}</div>`;
                return;
            }
            
            if (data.event_type === 'alert') {
                const timestamp = new Date(data.timestamp).toLocaleString('pt-BR');
                const signature = data.alert?.signature || 'N/A';
                const isPhishing = signature.toUpperCase().includes('PHISHING') || 
                                 signature.toUpperCase().includes('MALWARE') ||
                                 signature.toUpperCase().includes('TROJAN');
                
                const entryClass = isPhishing ? 'phishing' : 'alert';
                
                logsOutput.innerHTML += `
                    <div class="log-entry ${entryClass}">
                        <span class="log-timestamp">[${timestamp}]</span>
                        <span class="log-signature">${escapeHtml(signature)}</span>
                        <br>
                        <small>${escapeHtml(data.src_ip || 'N/A')} → ${escapeHtml(data.dest_ip || 'N/A')}</small>
                    </div>
                `;
                
                // Scroll para baixo
                logsOutput.scrollTop = logsOutput.scrollHeight;
            }
        } catch (error) {
            console.error('Erro ao processar log:', error);
        }
    };
    
    logsEventSource.onerror = function(error) {
        console.error('Erro no EventSource:', error);
        logsOutput.innerHTML += '<div class="log-entry">Erro na conexão. Tentando reconectar...</div>';
    };
    
    document.getElementById('start-logs').disabled = true;
    document.getElementById('stop-logs').disabled = false;
}

function stopLogs() {
    if (logsEventSource) {
        logsEventSource.close();
        logsEventSource = null;
        
        document.getElementById('start-logs').disabled = false;
        document.getElementById('stop-logs').disabled = true;
        
        const logsOutput = document.getElementById('logs-output');
        logsOutput.innerHTML += '<div class="log-entry">Monitoramento parado.</div>';
    }
}

function clearLogs() {
    document.getElementById('logs-output').innerHTML = '';
}


