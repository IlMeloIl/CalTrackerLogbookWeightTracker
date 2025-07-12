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

    const dados = exerciseIds.map(id => `exercise_ids[]=${id}`).join('&');
    AppUtils.fetch.requisicaoPost(workoutData.urls.reorderExercises, dados, {
        recarregarPagina: false,
        onErro: (erro) => {
            alert('Erro ao reordenar exercícios: ' + erro);
            location.reload();
        }
    });
}

function addExercise() {
    if (typeof AppUtils === 'undefined') {
        console.error('AppUtils não disponível para addExercise');
        return;
    }
    if (!workoutData) {
        console.error('Dados do treino não carregados');
        return;
    }

    const form = document.getElementById('addExerciseForm');
    const formData = new FormData(form);

    AppUtils.fetch.requisicaoPost(workoutData.urls.addExercise, formData, {
        mensagemErroCustomizada: 'Erro ao adicionar exercício'
    });
}

function removeExercise(exerciseId, exerciseName) {
    if (!workoutData) {
        console.error('Dados do treino não carregados');
        return;
    }

    const mensagem = `Tem certeza que deseja remover "${exerciseName}" do treino? Todos os dados registrados para este exercício serão perdidos.`;
    AppUtils.confirmacao.acao(mensagem, () => {
        AppUtils.fetch.requisicaoPost(workoutData.urls.removeExercise.replace('0', exerciseId), {}, {
            mensagemErroCustomizada: 'Erro ao remover exercício'
        });
    });
}

function editSets(exerciseId, currentSets) {
    const dadosCampos = {
        'editExerciseId': exerciseId,
        'newSets': currentSets
    };
    AppUtils.modal.abrir('editSetsModal', dadosCampos);
}

function updateSets() {
    if (!workoutData) {
        console.error('Dados do treino não carregados');
        return;
    }

    const form = document.getElementById('editSetsForm');
    const formData = new FormData(form);
    const exerciseId = formData.get('exercise_id');

    AppUtils.fetch.requisicaoPost(workoutData.urls.updateSets.replace('0', exerciseId), formData, {
        mensagemErroCustomizada: 'Erro ao atualizar séries'
    });
}

AppUtils.scripts.inicializar('workout.js', {
    initWorkoutSession,
    addExercise
}, function() {
    
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

    if (AppUtils.autoSave && AppUtils.autoSave.configurarCamposComTimeout) {
        AppUtils.autoSave.configurarCamposComTimeout(
            '.set-form input[name="weight"], .set-form input[name="reps"], .set-form input[name="notes"]',
            (form, elemento) => autoSaveSet(form),
            1000
        );
        console.log('✅ Auto-save configurado com sucesso');
    } else {
        console.error('❌ AppUtils.autoSave.configurarCamposComTimeout não disponível');
    }

    document.addEventListener('click', function(e) {
        if (e.target.closest('.edit-sets-btn')) {
            const btn = e.target.closest('.edit-sets-btn');
            const dados = AppUtils.dados.extrairDeElemento(btn, {
                exerciseId: 'exerciseId',
                currentSets: 'currentSets'
            });
            editSets(dados.exerciseId, dados.currentSets);
        }

        if (e.target.closest('.remove-exercise-btn')) {
            const btn = e.target.closest('.remove-exercise-btn');
            const dados = AppUtils.dados.extrairDeElemento(btn, {
                exerciseId: 'exerciseId',
                exerciseName: 'exerciseName'
            });
            removeExercise(dados.exerciseId, dados.exerciseName);
        }
    });
});

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

    AppUtils.fetch.requisicaoPost(url, formData, {
        onSucesso: () => {
            AppUtils.ui.mostrarIndicadorCarregamento(savingIndicator, false);
            saveFeedback.style.display = 'block';
            const card = form.closest('.card');
            card.classList.add('bg-success', 'bg-opacity-10');
            const badge = card.querySelector('.badge');
            if (!badge) {
                const badgeContainer = card.querySelector('.d-flex.align-items-center');
                badgeContainer.insertAdjacentHTML('afterbegin', '<span class="badge bg-success me-2">Registrada</span>');
            }
        },
        onErro: () => {
            AppUtils.ui.mostrarIndicadorCarregamento(savingIndicator, false);
            saveError.style.display = 'block';
        }
    });
}


