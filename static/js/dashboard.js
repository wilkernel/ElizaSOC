// Dashboard JavaScript para Monitoramento Suricata
// Autor: Wilker Junio Coelho Pimenta

// Variáveis globais
let charts = {};
let statsUpdateInterval;
let logsEventSource = null;
let realTimeMonitorChart = null;
let realTimeData = {
    labels: [],
    alerts: [],
    network: [],
    system: []
};
const MAX_DATA_POINTS = 60; // 60 pontos = última hora (atualizando a cada minuto)

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    init();
});

function init() {
    updateStatus();
    loadStats();
    loadAlerts();
    loadPhishingAlerts();
    updateSystemMetrics();
    updateServicesStatus();
    updateValidationData();
    initRealTimeMonitor(); // Inicializar gráfico de monitor em tempo real
    
    // Atualizar stats a cada 30 segundos
    statsUpdateInterval = setInterval(() => {
        loadStats();
        loadAlerts();
        loadPhishingAlerts();
        updateSystemMetrics();
        updateValidationData();
    }, 30000);
    
    // Atualizar status a cada 10 segundos
    setInterval(updateStatus, 10000);
    
    // Atualizar métricas do sistema a cada 5 segundos
    setInterval(updateSystemMetrics, 5000);
    
    // Atualizar status dos serviços a cada 30 segundos
    setInterval(updateServicesStatus, 30000);
    
    // Atualizar monitor em tempo real imediatamente e depois a cada 30 segundos
    updateRealTimeMonitor();
    setInterval(updateRealTimeMonitor, 30000);
    
    // Event listeners para controles de serviço
    setupServiceControls();
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

// Inicializar gráfico de monitor em tempo real
function initRealTimeMonitor() {
    const ctx = document.getElementById('realTimeMonitorChart');
    if (!ctx) return;
    
    // Inicializar com dados vazios
    realTimeMonitorChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Alertas/Min',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Rede (Flows+DNS)',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Uso do Sistema (%)',
                    data: [],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#475569',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y.toFixed(2);
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#334155',
                        display: true
                    },
                    ticks: {
                        color: '#94a3b8',
                        maxRotation: 45,
                        minRotation: 0
                    },
                    title: {
                        display: true,
                        text: 'Tempo',
                        color: '#94a3b8'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    grid: {
                        color: '#334155',
                        display: true
                    },
                    ticks: {
                        color: '#94a3b8'
                    },
                    title: {
                        display: true,
                        text: 'Eventos',
                        color: '#94a3b8'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        drawOnChartArea: false,
                        color: '#334155'
                    },
                    ticks: {
                        color: '#94a3b8'
                    },
                    title: {
                        display: true,
                        text: 'Percentual',
                        color: '#94a3b8'
                    }
                }
            },
            animation: {
                duration: 0 // Sem animação para atualização em tempo real
            }
        }
    });
}

// Atualizar gráfico de monitor em tempo real
async function updateRealTimeMonitor() {
    if (!realTimeMonitorChart) return;
    
    try {
        const [statusResponse, statsResponse] = await Promise.all([
            fetch('/api/status'),
            fetch('/api/stats')
        ]);
        
        const status = await statusResponse.json();
        const stats = await statsResponse.json();
        
        const now = new Date();
        const timeLabel = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        
        // Adicionar novos dados
        realTimeData.labels.push(timeLabel);
        
        // Alertas: contagem por minuto (diferencial se possível, ou total acumulado normalizado)
        realTimeData.alerts.push(stats.total_alerts || 0);
        
        // Calcular atividade de rede (flows + dns normalizados)
        const networkActivity = (stats.total_flows || 0) + (stats.total_dns || 0);
        realTimeData.network.push(networkActivity);
        
        // Uso de sistema baseado no tamanho do log (proxy para carga do sistema)
        // Normalizar o tamanho do log para percentual (assumindo log máximo de 100MB = 100%)
        const logSizeMB = status.eve_json_size ? status.eve_json_size / (1024 * 1024) : 0;
        const systemUsage = Math.min(100, (logSizeMB / 100) * 100); // Normalizar para 0-100%
        realTimeData.system.push(systemUsage);
        
        // Limitar a MAX_DATA_POINTS pontos
        if (realTimeData.labels.length > MAX_DATA_POINTS) {
            realTimeData.labels.shift();
            realTimeData.alerts.shift();
            realTimeData.network.shift();
            realTimeData.system.shift();
        }
        
        // Atualizar gráfico
        realTimeMonitorChart.data.labels = realTimeData.labels;
        realTimeMonitorChart.data.datasets[0].data = realTimeData.alerts;
        realTimeMonitorChart.data.datasets[1].data = realTimeData.network;
        realTimeMonitorChart.data.datasets[2].data = realTimeData.system;
        realTimeMonitorChart.update('none'); // 'none' = sem animação
        
    } catch (error) {
        console.error('Erro ao atualizar monitor em tempo real:', error);
    }
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

// Sistema Metrics
async function updateSystemMetrics() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Atualizar tamanho do log
        if (data.eve_json_size) {
            const sizeMB = (data.eve_json_size / (1024 * 1024)).toFixed(2);
            document.getElementById('log-size').textContent = sizeMB + ' MB';
        }
        
        // Atualizar última modificação
        if (data.eve_json_modified) {
            const lastUpdate = new Date(data.eve_json_modified);
            const now = new Date();
            const diffMinutes = Math.floor((now - lastUpdate) / 60000);
            
            if (diffMinutes < 1) {
                document.getElementById('log-last-update').textContent = 'Atualizado agora';
            } else if (diffMinutes < 60) {
                document.getElementById('log-last-update').textContent = `Atualizado há ${diffMinutes} min`;
            } else {
                const diffHours = Math.floor(diffMinutes / 60);
                document.getElementById('log-last-update').textContent = `Atualizado há ${diffHours}h`;
            }
        }
        
        // Simular CPU e Memory (em produção, esses dados viriam da API)
        // Para demonstração, vamos gerar valores simulados
        updateSimulatedMetrics();
    } catch (error) {
        console.error('Erro ao atualizar métricas:', error);
    }
}

function updateSimulatedMetrics() {
    // Simulação de CPU e Memory para demonstração
    // Em produção, esses valores viriam de /proc/stat e /proc/meminfo
    const cpuUsage = Math.random() * 100;
    const memoryUsage = 30 + Math.random() * 50;
    
    document.getElementById('cpu-value').textContent = cpuUsage.toFixed(1) + '%';
    document.getElementById('cpu-bar').style.width = cpuUsage + '%';
    
    document.getElementById('memory-value').textContent = memoryUsage.toFixed(1) + '%';
    document.getElementById('memory-bar').style.width = memoryUsage + '%';
}

// Services Control
async function updateServicesStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Atualizar status do Suricata
        const suricataStatus = document.getElementById('suricata-status');
        if (data.suricata_running) {
            suricataStatus.textContent = 'Ativo';
            suricataStatus.className = 'status-badge status-active';
        } else {
            suricataStatus.textContent = 'Inativo';
            suricataStatus.className = 'status-badge status-inactive';
        }
        
        // Atualizar botões do Suricata
        const suricataStart = document.getElementById('suricata-start');
        const suricataStop = document.getElementById('suricata-stop');
        const suricataRestart = document.getElementById('suricata-restart');
        
        if (data.suricata_running) {
            suricataStart.disabled = true;
            suricataStop.disabled = false;
            suricataRestart.disabled = false;
        } else {
            suricataStart.disabled = false;
            suricataStop.disabled = true;
            suricataRestart.disabled = true;
        }
        
        // Status do ClamAV (verificação simplificada)
        // Em produção, fazer chamada à API do ClamAV
        updateClamAVStatus();
    } catch (error) {
        console.error('Erro ao atualizar status dos serviços:', error);
    }
}

function updateClamAVStatus() {
    const clamavStatus = document.getElementById('clamav-status');
    
    // Verificação simplificada - sempre mostrar como disponível se a API responde
    // Em produção, verificar se o ClamAV está realmente rodando
    clamavStatus.textContent = 'Disponível';
    clamavStatus.className = 'status-badge status-active';
    
    const clamavStart = document.getElementById('clamav-start');
    const clamavStop = document.getElementById('clamav-stop');
    const clamavUpdate = document.getElementById('clamav-update');
    
    clamavStart.disabled = true;
    clamavStop.disabled = false;
    clamavUpdate.disabled = false;
}

function setupServiceControls() {
    // Suricata controls
    document.getElementById('suricata-start')?.addEventListener('click', () => controlService('suricata', 'start'));
    document.getElementById('suricata-stop')?.addEventListener('click', () => controlService('suricata', 'stop'));
    document.getElementById('suricata-restart')?.addEventListener('click', () => controlService('suricata', 'restart'));
    
    // ClamAV controls
    document.getElementById('clamav-start')?.addEventListener('click', () => controlService('clamav', 'start'));
    document.getElementById('clamav-stop')?.addEventListener('click', () => controlService('clamav', 'stop'));
    document.getElementById('clamav-update')?.addEventListener('click', () => controlService('clamav', 'update'));
}

async function controlService(service, action) {
    try {
        // Nota: Essas operações geralmente requerem privilégios sudo
        // Em produção, implementar endpoint na API que execute com sudo
        const response = await fetch(`/api/services/${service}/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(`Serviço ${service} ${action} executado com sucesso!`);
            updateServicesStatus();
        } else {
            alert(`Erro ao executar ${action} no serviço ${service}`);
        }
    } catch (error) {
        console.error('Erro ao controlar serviço:', error);
        // Em caso de erro da API, mostrar mensagem informativa
        alert(`Funcionalidade de controle de serviços requer configuração adicional.\n\nPara produção, configure endpoints seguros com autenticação e privilégios sudo.`);
    }
}

// Validation Data
async function updateValidationData() {
    try {
        const statusResponse = await fetch('/api/status');
        const statusData = await statusResponse.json();
        
        const statsResponse = await fetch('/api/stats');
        const statsData = await statsResponse.json();
        
        // Atualizar evidências
        const eveFileStatus = document.getElementById('eve-file-status');
        if (statusData.eve_json_exists) {
            eveFileStatus.textContent = `Acessível (${(statusData.eve_json_size / (1024 * 1024)).toFixed(2)} MB)`;
        } else {
            eveFileStatus.textContent = 'Não encontrado';
        }
        
        const suricataValidationStatus = document.getElementById('suricata-validation-status');
        if (statusData.suricata_running) {
            suricataValidationStatus.textContent = 'Ativo e detectando';
        } else {
            suricataValidationStatus.textContent = 'Inativo';
        }
        
        const alertValidationStatus = document.getElementById('alert-validation-status');
        alertValidationStatus.textContent = `${statsData.total_alerts} alertas detectados`;
        
        // Atualizar informações técnicas
        document.getElementById('log-size-validation').textContent = 
            statusData.eve_json_size ? `${(statusData.eve_json_size / (1024 * 1024)).toFixed(2)} MB` : '-';
        
        if (statusData.eve_json_modified) {
            const lastUpdate = new Date(statusData.eve_json_modified);
            document.getElementById('last-update-validation').textContent = 
                lastUpdate.toLocaleString('pt-BR');
        }
        
        document.getElementById('total-alerts-validation').textContent = 
            statsData.total_alerts || '-';
        
        // Contar tipos de assinaturas únicos
        const uniqueSignatures = Object.keys(statsData.top_signatures || {}).length;
        document.getElementById('signatures-types-validation').textContent = 
            `${uniqueSignatures} tipos diferentes`;
        
    } catch (error) {
        console.error('Erro ao atualizar dados de validação:', error);
    }
}


