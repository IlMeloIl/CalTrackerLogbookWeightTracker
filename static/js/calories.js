function openAddFoodModal(foodId, foodName, servingSize, calories, protein, carbs, fat) {
    const dadosCampos = {
        'selected_food_id': foodId,
        'selected_food_name': foodName,
        'selected_food_info': `${calories} kcal | P: ${protein}g, C: ${carbs}g, F: ${fat}g (por ${servingSize}g)`,
        'quantity_input': servingSize
    };

    AppUtils.modal.abrir('addFoodModal', dadosCampos);
    updateNutritionPreview(servingSize, calories, protein, carbs, fat, servingSize);

    document.getElementById('quantity_input').oninput = function() {
        const quantity = parseFloat(this.value) || 0;
        updateNutritionPreview(quantity, calories, protein, carbs, fat, servingSize);
    };
}

function openAddFoodModalFromCard(card) {
    const mapeamento = {
        foodId: 'foodId',
        foodName: 'foodName',
        servingSize: 'servingSize',
        calories: 'calories',
        protein: 'protein',
        carbs: 'carbs',
        fat: 'fat'
    };

    const dados = AppUtils.dados.extrairDeElemento(card, mapeamento);
    const dadosConvertidos = AppUtils.dados.converterTipos(dados, {
        servingSize: 'float',
        calories: 'int',
        protein: 'float',
        carbs: 'float',
        fat: 'float'
    });

    openAddFoodModal(dadosConvertidos.foodId, dadosConvertidos.foodName, dadosConvertidos.servingSize,
                     dadosConvertidos.calories, dadosConvertidos.protein, dadosConvertidos.carbs, dadosConvertidos.fat);
}

function updateNutritionPreview(quantity, calories, protein, carbs, fat, servingSize) {
    const factor = quantity / servingSize;

    const previewCalories = Math.round(calories * factor);
    const previewProtein = (protein * factor).toFixed(1);
    const previewCarbs = (carbs * factor).toFixed(1);
    const previewFat = (fat * factor).toFixed(1);

    document.getElementById('preview_content').innerHTML =
        `<strong>${previewCalories} kcal</strong> | P: ${previewProtein}g, C: ${previewCarbs}g, F: ${previewFat}g`;
    document.getElementById('nutrition_preview').style.display = 'block';
}

function openFoodModal(foodId = null, name = '', servingSize = '', calories = '', protein = '', carbs = '', fat = '') {
    const dadosCampos = {
        'foodModalTitle': foodId ? 'Editar Alimento' : 'Adicionar Alimento',
        'food_id': foodId || '',
        'food_name': name,
        'serving_size': servingSize,
        'calories': calories,
        'protein': protein,
        'carbs': carbs,
        'fat': fat
    };

    if (!foodId) {
        AppUtils.modal.resetarFormulario('foodForm');
    }

    AppUtils.modal.abrir('foodModal', dadosCampos);
}

function editFood(id, name, servingSize, calories, protein, carbs, fat) {
    const dadosEntidade = { id, name, servingSize, calories, protein, carbs, fat };
    const mapeamento = {
        titulo: 'foodModalTitle',
        id: 'food_id',
        name: 'food_name',
        servingSize: 'serving_size',
        calories: 'calories',
        protein: 'protein',
        carbs: 'carbs',
        fat: 'fat'
    };

    if (!id) {
        AppUtils.modal.resetarFormulario('foodForm');
    }

    AppUtils.entidades.abrirModalEdicaoGenerico('foodModal', dadosEntidade, mapeamento, 'Editar Alimento', 'Adicionar Alimento');
}

function criarFormularioExclusao(action, redirectUrl = null) {
    const opcoes = redirectUrl ? { urlRedirecionamento: redirectUrl } : {};
    AppUtils.formulario.criarDinamico(action, {}, opcoes);
}

function deleteFood(id, name) {
    AppUtils.confirmacao.excluir(name, () => {
        criarFormularioExclusao(`/tracker/foods/${id}/delete/`, '/tracker/log/');
    }, 'o alimento');
}

const deleteFoodFromButton = AppUtils.entidades.criarFuncaoFromButtonGenerico(
    { id: 'foodId', name: 'foodName' },
    (dados) => deleteFood(dados.id, dados.name),
    { nomeScript: 'calories.js' },
    'delete'
);

function editDailyLog(logId, foodName, currentQuantity) {
    const dadosEntidade = { logId, foodName, currentQuantity };
    const mapeamento = {
        logId: 'edit_log_id',
        foodName: 'edit_food_name',
        currentQuantity: 'edit_quantity'
    };
    AppUtils.entidades.abrirModalEdicaoGenerico('editDailyLogModal', dadosEntidade, mapeamento, 'Editar Quantidade');
}

const editDailyLogFromButton = AppUtils.entidades.criarFuncaoFromButtonGenerico(
    { logId: 'logId', foodName: 'foodName', currentQuantity: 'quantity' },
    (dados) => editDailyLog(dados.logId, dados.foodName, dados.currentQuantity),
    {
        tiposConversao: { currentQuantity: 'float' },
        nomeScript: 'calories.js'
    },
    'edit'
);

const editFoodFromButton = AppUtils.entidades.criarFuncaoFromButtonGenerico(
    {
        id: 'foodId', name: 'foodName', servingSize: 'servingSize',
        calories: 'calories', protein: 'protein', carbs: 'carbs', fat: 'fat'
    },
    (dados) => editFood(dados.id, dados.name, dados.servingSize, dados.calories, dados.protein, dados.carbs, dados.fat),
    {
        tiposConversao: {
            servingSize: 'float', calories: 'int', protein: 'float', carbs: 'float', fat: 'float'
        },
        nomeScript: 'calories.js'
    },
    'edit'
);

const deleteDailyLogFromButton = AppUtils.entidades.criarFuncaoFromButtonGenerico(
    { logId: 'logId', foodName: 'foodName', quantity: 'quantity' },
    (dados) => deleteDailyLog(dados.logId, dados.foodName, dados.quantity),
    {
        tiposConversao: { quantity: 'float' },
        nomeScript: 'calories.js'
    },
    'delete'
);

function deleteDailyLog(logId, foodName, quantity) {
    const mensagem = `Tem certeza que deseja remover ${quantity}g de "${foodName}" do seu diário?`;
    AppUtils.confirmacao.acao(mensagem, () => {
        criarFormularioExclusao(`/tracker/log/${logId}/delete/`);
    });
}

AppUtils.entidades.inicializarScriptPadrao('calories.js', {
    deleteFoodFromButton,
    editDailyLogFromButton,
    editFoodFromButton,
    deleteDailyLogFromButton
}, [
    {
        formId: 'foodForm',
        config: {
            url: function(formData) {
                const foodId = formData.get('food_id');
                return foodId ? `/tracker/foods/${foodId}/edit-ajax/` : '/tracker/foods/add-ajax/';
            },
            mensagemErro: 'Erro ao salvar alimento'
        }
    },
    {
        formId: 'addFoodForm',
        config: {
            url: window.location.href,
            mensagemErro: 'Erro ao adicionar alimento ao diário'
        }
    },
    {
        formId: 'editDailyLogForm',
        config: {
            url: function(formData) {
                const logId = formData.get('log_id');
                return `/tracker/log/${logId}/edit/`;
            },
            modalId: 'editDailyLogModal',
            mensagemErro: 'Erro ao editar quantidade'
        }
    }
], function() {

    AppUtils.sortable.configurarReordenacao('food-list', {
        url: '/tracker/daily-log/reorder/',
        atributoId: 'data-food-id',
        nomeParametro: 'food_ids[]'
    });
});
