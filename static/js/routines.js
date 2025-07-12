/**
 * Abre modal de edição de rotina com dados pré-preenchidos
 * @param {string|number} id - ID da rotina
 * @param {string} name - Nome da rotina
 */
function editRoutine(id, name) {
    const dadosEntidade = { id, name };
    const mapeamento = {
        id: 'edit_routine_id',
        name: 'edit_routine_name'
    };
    AppUtils.entidades.abrirModalEdicaoGenerico('editRoutineModal', dadosEntidade, mapeamento, 'Editar Rotina');
}

/**
 * Exclui rotina com confirmação do usuário
 * @param {string|number} id - ID da rotina
 * @param {string} name - Nome da rotina
 */
function deleteRoutine(id, name) {
    AppUtils.entidades.excluirEntidadeComConfirmacao(
        id,
        name,
        `/logbook/rotinas/${id}/delete-ajax/`,
        'a rotina',
        { mensagemErroCustomizada: 'Erro ao excluir rotina' }
    );
}

/**
 * Função FromButton para edição de rotina
 * Extrai dados do elemento e chama editRoutine
 */
const editRoutineFromButton = AppUtils.entidades.criarFuncaoFromButtonGenerico(
    { id: 'routineId', name: 'routineName' },
    (dados) => editRoutine(dados.id, dados.name),
    { nomeScript: 'routines.js' },
    'edit'
);

/**
 * Função FromButton para exclusão de rotina
 * Extrai dados do elemento e chama deleteRoutine
 */
const deleteRoutineFromButton = AppUtils.entidades.criarFuncaoFromButtonGenerico(
    { id: 'routineId', name: 'routineName' },
    (dados) => deleteRoutine(dados.id, dados.name),
    { nomeScript: 'routines.js' },
    'delete'
);

/**
 * Inicialização do módulo routines.js
 * Utiliza o padrão de inicialização padronizado com configuração de formulários
 */
AppUtils.entidades.inicializarScriptPadrao('routines.js', {
    editRoutineFromButton,
    deleteRoutineFromButton
}, [
    {
        formId: 'editRoutineForm',
        config: {
            urlComId: '/logbook/rotinas/{id}/edit-ajax/',
            campoId: 'routine_id',
            mensagemErro: 'Erro ao editar rotina'
        }
    }
]);
