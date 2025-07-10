function selectExerciseCard(exerciseId, exerciseName) {
    const currentPeriod = document.getElementById('period-select') ?
                         document.getElementById('period-select').value : '90';

    const url = new URL(window.location);
    url.searchParams.set('exercise', exerciseId);
    url.searchParams.set('period', currentPeriod);

    window.location.href = url.toString();
}

function selectExerciseCardFromCard(element) {
    const exerciseId = element.dataset.exerciseId;
    const exerciseName = element.dataset.exerciseName;
    selectExerciseCard(exerciseId, exerciseName);
}

function changePeriod(period) {
    const url = new URL(window.location);
    const currentExercise = url.searchParams.get('exercise');

    if (currentExercise) {
        url.searchParams.set('exercise', currentExercise);
        url.searchParams.set('period', period || '90');

        window.location.href = url.toString();
    }
}

function initExerciseProgressChart() {
    const chartDataEl = document.getElementById('chart-data');
    if (!chartDataEl) return;

    const chartData = JSON.parse(chartDataEl.textContent);
    
    if (!chartData.datasets || chartData.datasets.length === 0) return;

    const series = chartData.datasets.map(function(dataset) {
        return {
            name: dataset.label,
            data: dataset.data.map(function(point) {
                return [Date.parse(point.x), point.y];
            }),
            color: dataset.borderColor,
            marker: {
                fillColor: dataset.borderColor,
                lineWidth: 2,
                lineColor: '#ffffff',
                radius: dataset.pointRadius || 4
            },
            lineWidth: dataset.borderWidth || 2,
            dashStyle: dataset.borderDash ? 'dash' : 'solid'
        };
    });

    Highcharts.chart('progressChart', {
        chart: {
            type: 'line',
            backgroundColor: 'transparent',
            style: {
                fontFamily: 'inherit'
            },
            zoomType: 'x'
        },
        title: {
            text: 'Progressão do Exercício',
            style: {
                color: '#ffffff'
            }
        },
        xAxis: {
            type: 'datetime',
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
                const date = new Date(this.x).toLocaleDateString('pt-BR');
                return `<b>${this.series.name}</b><br/>
                        Data: ${date}<br/>
                        Peso: ${this.y} kg`;
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: false
                },
                enableMouseTracking: true,
                connectNulls: false
            }
        },
        series: series,
        credits: {
            enabled: false
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initExerciseProgressChart();

    const exerciseCards = document.querySelectorAll('.exercise-card');
    exerciseCards.forEach(card => {
        card.addEventListener('click', function() {
            const exerciseId = this.dataset.exerciseId;
            const exerciseName = this.dataset.exerciseName;
            selectExerciseCard(exerciseId, exerciseName);
        });
    });

    const periodSelect = document.getElementById('period-select');
    if (periodSelect) {
        periodSelect.addEventListener('change', function() {
            changePeriod(this.value);
        });
    }

    const exerciseSelect = document.getElementById('exercise-select');
    if (exerciseSelect) {
        exerciseSelect.addEventListener('change', function() {
            const exerciseId = this.value;
            if (exerciseId) {
                const currentPeriod = document.getElementById('period-select') ?
                                     document.getElementById('period-select').value : '90';
                
                const url = new URL(window.location);
                url.searchParams.set('exercise', exerciseId);
                url.searchParams.set('period', currentPeriod);
                
                window.location.href = url.toString();
            }
        });
    }
});
