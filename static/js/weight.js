function initWeightChart() {
    return AppUtils.graficos.inicializarComProcessamento('weightChart', 'chart-data', {
        processadorDados: function(dadosGrafico) {
            if (!dadosGrafico.data || dadosGrafico.data.length === 0) return null;

            const series = [{
                name: 'Peso',
                data: dadosGrafico.data,
                color: '#007bff',
                marker: { fillColor: '#007bff', lineWidth: 2, lineColor: '#ffffff' }
            }];

            if (dadosGrafico.moving_average && dadosGrafico.moving_average.some(val => val !== null)) {
                series.push({
                    name: 'Média Móvel (7 dias)',
                    data: dadosGrafico.moving_average,
                    color: '#28a745',
                    dashStyle: 'dash',
                    marker: { enabled: false }
                });
            }

            const configuracaoBase = AppUtils.graficos.criarConfiguracaoBase({
                titulo: 'Evolução do Peso',
                tituloY: 'Peso (kg)'
            });

            return {
                ...configuracaoBase,
                xAxis: { ...configuracaoBase.xAxis, categories: dadosGrafico.labels },
                tooltip: {
                    ...configuracaoBase.tooltip,
                    formatter: function() {
                        const date = dadosGrafico.dates[this.point.index];
                        const formattedDate = new Date(date).toLocaleDateString('pt-BR');
                        return `<b>${this.series.name}</b><br/>Data: ${formattedDate}<br/>Peso: ${this.y} kg`;
                    }
                },
                series: series
            };
        }
    });
}

function editarRegistroPeso(id, peso, data) {
    const dadosEntidade = { id, peso, data };
    const mapeamento = {
        id: 'editar_registro_id',
        peso: 'editar_peso_kg',
        data: 'editar_data'
    };
    AppUtils.entidades.abrirModalEdicaoGenerico('editarRegistroPesoModal', dadosEntidade, mapeamento, 'Editar Registro de Peso');
}

const editarRegistroPesoFromButton = AppUtils.entidades.criarFuncaoFromButtonGenerico(
    { id: 'registroId', peso: 'pesoKg', data: 'data' },
    (dados) => editarRegistroPeso(dados.id, dados.peso, dados.data),
    { nomeScript: 'weight.js' },
    'edit'
);

function excluirRegistroPeso(id) {
    AppUtils.entidades.excluirEntidadeComConfirmacao(
        id,
        'este registro de peso',
        `/weight/${id}/excluir/`,
        'o registro',
        { mensagemErroCustomizada: 'Erro ao excluir registro' }
    );
}

const excluirRegistroPesoFromButton = AppUtils.entidades.criarFuncaoFromButtonGenerico(
    { id: 'registroId' },
    (dados) => excluirRegistroPeso(dados.id),
    { nomeScript: 'weight.js' },
    'delete'
);

AppUtils.entidades.inicializarScriptPadrao('weight.js', {
    editarRegistroPesoFromButton,
    excluirRegistroPesoFromButton,
    initWeightChart
}, [
    {
        formId: 'editarRegistroPesoForm',
        config: {
            url: function(formData) {
                const registroId = formData.get('registro_id');
                return `/weight/${registroId}/editar/`;
            },
            modalId: 'editarRegistroPesoModal',
            mensagemErro: 'Erro ao editar registro'
        }
    }
], function() {

    initWeightChart();
});
