function editExercise(id, name, description) {
    document.getElementById('edit_exercise_id').value = id;
    document.getElementById('edit_exercise_name').value = name;
    document.getElementById('edit_exercise_description').value = description || '';
    new bootstrap.Modal(document.getElementById('editExerciseModal')).show();
}

function deleteExercise(id, name) {
    if (confirm(`Tem certeza que deseja excluir o exercício "${name}"?`)) {
        fetch(`/logbook/exercicios/${id}/delete-ajax/`, {
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
                alert('Erro ao excluir exercício: ' + (data.error || 'Erro desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao excluir exercício');
        });
    }
}

function editExerciseFromButton(element) {
    const id = element.dataset.exerciseId;
    const name = element.dataset.exerciseName;
    const description = element.dataset.exerciseDescription;
    editExercise(id, name, description);
}

function deleteExerciseFromButton(element) {
    const id = element.dataset.exerciseId;
    const name = element.dataset.exerciseName;
    deleteExercise(id, name);
}

document.addEventListener('DOMContentLoaded', function() {
    const editExerciseForm = document.getElementById('editExerciseForm');
    if (editExerciseForm) {
        editExerciseForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const exerciseId = formData.get('exercise_id');
            
            fetch(`/logbook/exercicios/${exerciseId}/edit-ajax/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Erro ao editar exercício: ' + (data.error || 'Erro desconhecido'));
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao editar exercício');
            });
        });
    }
});
