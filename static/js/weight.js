function initWeightChart() {
    const dataEl = document.getElementById('chart-data');
    if (!dataEl) return;

    const chartData = JSON.parse(dataEl.textContent);
    
    if (!chartData.data || chartData.data.length === 0) return;

    const series = [{
        name: 'Peso',
        data: chartData.data,
        color: '#007bff',
        marker: {
            fillColor: '#007bff',
            lineWidth: 2,
            lineColor: '#ffffff'
        }
    }];

    if (chartData.moving_average && chartData.moving_average.some(val => val !== null)) {
        series.push({
            name: 'Média Móvel (7 dias)',
            data: chartData.moving_average,
            color: '#28a745',
            dashStyle: 'dash',
            marker: {
                enabled: false
            }
        });
    }

    Highcharts.chart('weightChart', {
        chart: {
            type: 'line',
            backgroundColor: 'transparent',
            style: {
                fontFamily: 'inherit'
            }
        },
        title: {
            text: 'Evolução do Peso',
            style: {
                color: '#ffffff'
            }
        },
        xAxis: {
            categories: chartData.labels,
            labels: {
                style: {
                    color: '#ffffff'
                }
            },
            lineColor: '#6c757d',
            tickColor: '#6c757d'
        },
        yAxis: {
            title: {
                text: 'Peso (kg)',
                style: {
                    color: '#ffffff'
                }
            },
            labels: {
                style: {
                    color: '#ffffff'
                }
            },
            gridLineColor: '#6c757d'
        },
        legend: {
            itemStyle: {
                color: '#ffffff'
            },
            itemHoverStyle: {
                color: '#cccccc'
            }
        },
        tooltip: {
            backgroundColor: '#343a40',
            style: {
                color: '#ffffff'
            },
            formatter: function() {
                const date = chartData.dates[this.point.index];
                const formattedDate = new Date(date).toLocaleDateString('pt-BR');
                return `<b>${this.series.name}</b><br/>
                        Data: ${formattedDate}<br/>
                        Peso: ${this.y} kg`;
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: false
                },
                enableMouseTracking: true
            }
        },
        series: series,
        credits: {
            enabled: false
        }
    });
}

function editarRegistroPeso(id, peso, data) {
    document.getElementById('editar_registro_id').value = id;
    document.getElementById('editar_peso_kg').value = peso;
    document.getElementById('editar_data').value = data;

    new bootstrap.Modal(document.getElementById('editarRegistroPesoModal')).show();
}

function editarRegistroPesoFromButton(element) {
    const id = element.dataset.registroId;
    const peso = element.dataset.pesoKg;
    const data = element.dataset.data;
    editarRegistroPeso(id, peso, data);
}

function salvarEdicaoRegistro() {
    const id = document.getElementById('editar_registro_id').value;
    const peso = document.getElementById('editar_peso_kg').value;
    const data = document.getElementById('editar_data').value;

    if (!peso || !data) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    const formData = new FormData();
    formData.append('peso_kg', peso);
    formData.append('data', data);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

    fetch(`/weight/${id}/editar/`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            location.reload();
        } else {
            alert('Erro ao editar: ' + (data.erro || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao editar registro');
    });
}

function excluirRegistroPeso(id) {
    if (confirm('Tem certeza que deseja excluir este registro de peso?')) {
        fetch(`/weight/${id}/excluir/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                location.reload();
            } else {
                alert('Erro ao excluir registro: ' + (data.erro || 'Erro desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao excluir registro');
        });
    }
}

function excluirRegistroPesoFromButton(element) {
    const id = element.dataset.registroId;
    excluirRegistroPeso(id);
}

function updateChart(dias) {
    fetch(`/weight/chart-data/?days=${dias}`)
        .then(response => response.json())
        .then(data => {
            const chartDataEl = document.getElementById('chart-data');
            if (chartDataEl) {
                chartDataEl.textContent = JSON.stringify(data);
                initWeightChart();
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar gráfico:', error);
        });
}



document.addEventListener('DOMContentLoaded', function() {
    initWeightChart();

    const periodButtons = document.querySelectorAll('[data-period]');
    periodButtons.forEach(button => {
        button.addEventListener('click', function() {
            const period = this.dataset.period;
            
            periodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            atualizarGrafico(period);
        });
    });

    const editForm = document.getElementById('editarRegistroPesoForm');
    if (editForm) {
        editForm.onsubmit = function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const registroId = formData.get('registro_id');

            fetch(`/weight/${registroId}/editar/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    bootstrap.Modal.getInstance(document.getElementById('editarRegistroPesoModal')).hide();
                    location.reload();
                } else {
                    alert('Erro ao editar registro: ' + (data.erro || 'Erro desconhecido'));
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao editar registro');
            });
        };
    }
});
