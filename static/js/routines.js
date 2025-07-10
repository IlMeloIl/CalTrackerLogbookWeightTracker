function editRoutine(id, name) {
    document.getElementById('edit_routine_id').value = id;
    document.getElementById('edit_routine_name').value = name;
    new bootstrap.Modal(document.getElementById('editRoutineModal')).show();
}

function deleteRoutine(id, name) {
    if (confirm(`Tem certeza que deseja excluir a rotina "${name}"?`)) {
        fetch(`/logbook/rotinas/${id}/delete-ajax/`, {
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
                alert('Erro ao excluir rotina: ' + (data.error || 'Erro desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao excluir rotina');
        });
    }
}

function editRoutineFromButton(element) {
    const id = element.dataset.routineId;
    const name = element.dataset.routineName;
    editRoutine(id, name);
}

function deleteRoutineFromButton(element) {
    const id = element.dataset.routineId;
    const name = element.dataset.routineName;
    deleteRoutine(id, name);
}

document.addEventListener('DOMContentLoaded', function() {
    const editRoutineForm = document.getElementById('editRoutineForm');
    if (editRoutineForm) {
        editRoutineForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const routineId = formData.get('routine_id');
            
            fetch(`/logbook/rotinas/${routineId}/edit-ajax/`, {
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
                    alert('Erro ao editar rotina: ' + (data.error || 'Erro desconhecido'));
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao editar rotina');
            });
        });
    }
});
