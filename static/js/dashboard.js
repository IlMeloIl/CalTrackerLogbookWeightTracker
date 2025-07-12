function deleteWorkoutSession(sessionId, routineName, sessionDate) {
    if (typeof AppUtils === 'undefined') {
        console.error('AppUtils não disponível para deleteWorkoutSession');
        return;
    }
    const mensagem = `Tem certeza que deseja excluir o treino "${routineName}" de ${sessionDate}? Esta ação não pode ser desfeita.`;
    AppUtils.confirmacao.acao(mensagem, () => {
        AppUtils.fetch.requisicaoPost(`/logbook/treino/${sessionId}/delete/`, {}, {
            mensagemErroCustomizada: 'Erro ao excluir treino'
        });
    });
}

AppUtils.scripts.inicializar('dashboard.js', {
    deleteWorkoutSession
});
