/**
 * Abre modal de edição de exercício com dados pré-preenchidos
 * @param {string|number} id - ID do exercício
 * @param {string} name - Nome do exercício
 * @param {string} description - Descrição do exercício
 */
function editExercise(id, name, description) {
    const dadosEntidade = { id, name, description: description || '' };
    const mapeamento = {
        id: 'edit_exercise_id',
        name: 'edit_exercise_name',
        description: 'edit_exercise_description'
    };
    AppUtils.entidades.abrirModalEdicaoGenerico('editExerciseModal', dadosEntidade, mapeamento, 'Editar Exercício');
}

/**
 * Exclui exercício com confirmação do usuário
 * @param {string|number} id - ID do exercício
 * @param {string} name - Nome do exercício
 */
function deleteExercise(id, name) {
    AppUtils.entidades.excluirEntidadeComConfirmacao(
        id,
        name,
        `/logbook/exercicios/${id}/delete-ajax/`,
        'o exercício',
        { mensagemErroCustomizada: 'Erro ao excluir exercício' }
    );
}

/**
 * Função FromButton para edição de exercício
 * Extrai dados do elemento e chama editExercise
 */
const editExerciseFromButton = AppUtils.entidades.criarFuncaoFromButtonGenerico(
    { id: 'exerciseId', name: 'exerciseName', description: 'exerciseDescription' },
    (dados) => editExercise(dados.id, dados.name, dados.description),
    { nomeScript: 'exercises.js' },
    'edit'
);

/**
 * Função FromButton para exclusão de exercício
 * Extrai dados do elemento e chama deleteExercise
 */
const deleteExerciseFromButton = AppUtils.entidades.criarFuncaoFromButtonGenerico(
    { id: 'exerciseId', name: 'exerciseName' },
    (dados) => deleteExercise(dados.id, dados.name),
    { nomeScript: 'exercises.js' },
    'delete'
);

/**
 * Inicialização do módulo exercises.js
 * Utiliza o padrão de inicialização padronizado com configuração de formulários
 */
AppUtils.entidades.inicializarScriptPadrao('exercises.js', {
    editExerciseFromButton,
    deleteExerciseFromButton
}, [
    {
        formId: 'editExerciseForm',
        config: {
            urlComId: '/logbook/exercicios/{id}/edit-ajax/',
            campoId: 'exercise_id',
            mensagemErro: 'Erro ao editar exercício'
        }
    }
]);
