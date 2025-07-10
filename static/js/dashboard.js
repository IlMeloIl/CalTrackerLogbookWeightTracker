function deleteWorkoutSession(sessionId, routineName, sessionDate) {
    if (confirm(`Tem certeza que deseja excluir o treino "${routineName}" de ${sessionDate}? Esta ação não pode ser desfeita.`)) {
        fetch(`/logbook/treino/${sessionId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Erro ao excluir treino: ' + (data.error || 'Erro desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao excluir treino');
        });
    }
}
