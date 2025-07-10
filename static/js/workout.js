let editMode = false;
let sortable = null;
let workoutData = null;

function initWorkoutSession() {
    const workoutDataEl = document.getElementById('workout-data');
    if (workoutDataEl) {
        workoutData = JSON.parse(workoutDataEl.textContent);
    }
}

function toggleEditMode() {
    editMode = !editMode;
    const editButton = document.getElementById('toggleEditMode');
    const dragHandles = document.querySelectorAll('.drag-handle');
    const editControls = document.querySelectorAll('.edit-controls');

    if (editMode) {
        editButton.innerHTML = '<i class="bi bi-check"></i> Finalizar Edição';
        editButton.className = 'btn btn-sm btn-success';
        dragHandles.forEach(handle => handle.style.display = 'inline');
        editControls.forEach(control => control.style.display = 'inline-block');

        const exerciseList = document.getElementById('exercise-list');

        sortable = new Sortable(exerciseList, {
            handle: '.drag-handle',
            animation: 150,
            draggable: '.exercise-section',
            onEnd: function(evt) {
                setTimeout(reorderExercises, 100);
            }
        });
    } else {
        editButton.innerHTML = '<i class="bi bi-pencil"></i> Editar Treino';
        editButton.className = 'btn btn-sm btn-outline-secondary';
        dragHandles.forEach(handle => handle.style.display = 'none');
        editControls.forEach(control => control.style.display = 'none');

        if (sortable) {
            sortable.destroy();
            sortable = null;
        }
    }
}

function reorderExercises() {
    const exerciseList = document.getElementById('exercise-list');
    if (!exerciseList) {
        console.error('Element exercise-list não encontrado');
        return;
    }

    const exerciseSections = exerciseList.querySelectorAll('.exercise-section');
    const exerciseIds = [];

    exerciseSections.forEach((section) => {
        const id = section.getAttribute('data-exercise-id');
        if (id && id.trim() && id !== 'null' && id !== 'undefined') {
            exerciseIds.push(id.trim());
        }
    });

    if (exerciseIds.length === 0) {
        console.error('Nenhum ID de exercício válido encontrado');
        return;
    }

    if (!workoutData) {
        console.error('Dados do treino não carregados');
        return;
    }

    fetch(workoutData.urls.reorderExercises, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: exerciseIds.map(id => `exercise_ids[]=${id}`).join('&')
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            alert('Erro ao reordenar exercícios: ' + data.error);
            location.reload();
        }
    })
    .catch(error => {
        console.error('Erro na requisição:', error);
        alert('Erro ao reordenar exercícios: ' + error.message);
        location.reload();
    });
}

function addExercise() {
    if (!workoutData) {
        console.error('Dados do treino não carregados');
        return;
    }

    const form = document.getElementById('addExerciseForm');
    const formData = new FormData(form);

    fetch(workoutData.urls.addExercise, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erro ao adicionar exercício: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao adicionar exercício');
    });
}

function removeExercise(exerciseId, exerciseName) {
    if (!workoutData) {
        console.error('Dados do treino não carregados');
        return;
    }

    if (!confirm(`Tem certeza que deseja remover "${exerciseName}" do treino? Todos os dados registrados para este exercício serão perdidos.`)) {
        return;
    }

    fetch(workoutData.urls.removeExercise.replace('0', exerciseId), {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erro ao remover exercício: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao remover exercício');
    });
}

function editSets(exerciseId, currentSets) {
    document.getElementById('editExerciseId').value = exerciseId;
    document.getElementById('newSets').value = currentSets;
    new bootstrap.Modal(document.getElementById('editSetsModal')).show();
}

function updateSets() {
    if (!workoutData) {
        console.error('Dados do treino não carregados');
        return;
    }

    const form = document.getElementById('editSetsForm');
    const formData = new FormData(form);
    const exerciseId = formData.get('exercise_id');

    fetch(workoutData.urls.updateSets.replace('0', exerciseId), {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erro ao atualizar séries: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao atualizar séries');
    });
}

function logSet(exerciseId, setNumber, button) {
    const setContainer = button.closest('.set-container');
    const weightInput = setContainer.querySelector('input[name="weight"]');
    const repsInput = setContainer.querySelector('input[name="reps"]');
    const notesInput = setContainer.querySelector('input[name="notes"]');

    const weight = weightInput.value;
    const reps = repsInput.value;
    const notes = notesInput.value;

    if (!weight || !reps) {
        alert('Por favor, preencha peso e repetições.');
        return;
    }

    const formData = new FormData();
    formData.append('weight', weight);
    formData.append('reps', reps);
    formData.append('notes', notes);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

    const url = `/logbook/treino/${workoutData.sessionId}/log/${exerciseId}/${setNumber}/`;

    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.innerHTML = '<i class="bi bi-check"></i>';
            button.className = 'btn btn-success btn-sm';
            button.disabled = true;
            
            weightInput.disabled = true;
            repsInput.disabled = true;
            notesInput.disabled = true;
        } else {
            alert('Erro ao registrar série: ' + (data.error || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao registrar série');
    });
}

function autoSaveSet(form) {
    const sessionId = form.dataset.sessionId;
    const exerciseId = form.dataset.exerciseId;
    const setNumber = form.dataset.setNumber;

    const weightInput = form.querySelector('input[name="weight"]');
    const repsInput = form.querySelector('input[name="reps"]');
    const notesInput = form.querySelector('input[name="notes"]');

    if (!weightInput || !repsInput) {
        return;
    }

    const weight = weightInput.value;
    const reps = repsInput.value;
    const notes = notesInput ? notesInput.value : '';

    if (!weight || !reps) {
        return;
    }

    const savingIndicator = form.closest('.card').querySelector('.saving-indicator');
    const saveFeedback = form.querySelector('.save-feedback');
    const saveError = form.querySelector('.save-error');

    savingIndicator.style.display = 'block';
    saveFeedback.style.display = 'none';
    saveError.style.display = 'none';

    const formData = new FormData();
    formData.append('weight', weight);
    formData.append('reps', reps);
    formData.append('notes', notes);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

    const url = `/logbook/treino/${sessionId}/log/${exerciseId}/${setNumber}/`;

    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        savingIndicator.style.display = 'none';
        if (data.success) {
            saveFeedback.style.display = 'block';
            const card = form.closest('.card');
            card.classList.add('bg-success', 'bg-opacity-10');
            const badge = card.querySelector('.badge');
            if (!badge) {
                const badgeContainer = card.querySelector('.d-flex.align-items-center');
                badgeContainer.insertAdjacentHTML('afterbegin', '<span class="badge bg-success me-2">Registrada</span>');
            }
        } else {
            saveError.style.display = 'block';
        }
    })
    .catch(error => {
        savingIndicator.style.display = 'none';
        saveError.style.display = 'block';
        console.error('Erro:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initWorkoutSession();

    const toggleBtn = document.getElementById('toggleEditMode');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleEditMode);
    }

    const addExerciseModal = document.getElementById('addExerciseModal');
    if (addExerciseModal) {
        addExerciseModal.addEventListener('hidden.bs.modal', function() {
            document.getElementById('addExerciseForm').reset();
        });
    }

    const editSetsModal = document.getElementById('editSetsModal');
    if (editSetsModal) {
        editSetsModal.addEventListener('hidden.bs.modal', function() {
            document.getElementById('editSetsForm').reset();
        });
    }

    const setForms = document.querySelectorAll('.set-form');

    setForms.forEach(form => {
        const weightInput = form.querySelector('input[name="weight"]');
        const repsInput = form.querySelector('input[name="reps"]');
        const notesInput = form.querySelector('input[name="notes"]');

        let saveTimeout;

        function handleInputChange() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                autoSaveSet(form);
            }, 1000);
        }

        if (weightInput) {
            weightInput.addEventListener('input', handleInputChange);
            weightInput.addEventListener('blur', () => {
                clearTimeout(saveTimeout);
                autoSaveSet(form);
            });
        }

        if (repsInput) {
            repsInput.addEventListener('input', handleInputChange);
            repsInput.addEventListener('blur', () => {
                clearTimeout(saveTimeout);
                autoSaveSet(form);
            });
        }

        if (notesInput) {
            notesInput.addEventListener('input', handleInputChange);
            notesInput.addEventListener('blur', () => {
                clearTimeout(saveTimeout);
                autoSaveSet(form);
            });
        }
    });

    document.addEventListener('click', function(e) {
        if (e.target.closest('.edit-sets-btn')) {
            const btn = e.target.closest('.edit-sets-btn');
            const exerciseId = btn.getAttribute('data-exercise-id');
            const currentSets = btn.getAttribute('data-current-sets');
            editSets(exerciseId, currentSets);
        }

        if (e.target.closest('.remove-exercise-btn')) {
            const btn = e.target.closest('.remove-exercise-btn');
            const exerciseId = btn.getAttribute('data-exercise-id');
            const exerciseName = btn.getAttribute('data-exercise-name');
            removeExercise(exerciseId, exerciseName);
        }
    });
});
