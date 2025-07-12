function selectExerciseCard(exerciseId, exerciseName) {
    if (typeof AppUtils === 'undefined') {
        console.error('AppUtils não disponível para selectExerciseCard');
        return;
    }
    const currentPeriod = document.getElementById('period-select') ?
                         document.getElementById('period-select').value : '90';

    AppUtils.url.atualizarParametros({
        'exercise': exerciseId,
        'period': currentPeriod
    });
}

const selectExerciseCardFromCard = typeof AppUtils !== 'undefined' ?
    AppUtils.acoes.criarFuncaoFromButton(
        { exerciseId: 'exerciseId', exerciseName: 'exerciseName' },
        (dados) => selectExerciseCard(dados.exerciseId, dados.exerciseName),
        { nomeScript: 'exercise-progress.js' }
    ) : function(element) {
        console.error('AppUtils não disponível para selectExerciseCardFromCard');
    };

function processarDadosProgresso(dadosGrafico) {
    if (!dadosGrafico.datasets || dadosGrafico.datasets.length === 0) return null;

    const series = dadosGrafico.datasets.map(function(dataset) {
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

    const configuracaoBase = AppUtils.graficos.criarConfiguracaoBase({
        titulo: 'Progressão do Exercício',
        tituloY: 'Peso (kg)',
        habilitarZoom: true,
        tipoEixoX: 'datetime'
    });

    return {
        ...configuracaoBase,
        tooltip: {
            ...configuracaoBase.tooltip,
            formatter: function() {
                const date = new Date(this.x).toLocaleDateString('pt-BR');
                return `<b>${this.series.name}</b><br/>Data: ${date}<br/>Peso: ${this.y} kg`;
            }
        },
        plotOptions: {
            ...configuracaoBase.plotOptions,
            line: {
                ...configuracaoBase.plotOptions.line,
                connectNulls: false
            }
        },
        series: series
    };
}

function changePeriod(period) {
    const currentExercise = AppUtils.url.obterParametro('exercise');

    if (currentExercise) {
        AppUtils.url.atualizarParametros({
            'exercise': currentExercise,
            'period': period || '90'
        });
    }
}

function initExerciseProgressChart() {
    return AppUtils.graficos.inicializarComProcessamento('progressChart', 'chart-data', {
        processadorDados: processarDadosProgresso
    });
}

AppUtils.scripts.inicializar('exercise-progress.js', {
    selectExerciseCardFromCard,
    selectExerciseCard
}, function() {

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

                AppUtils.url.atualizarParametros({
                    'exercise': exerciseId,
                    'period': currentPeriod
                });
            }
        });
    }
});
