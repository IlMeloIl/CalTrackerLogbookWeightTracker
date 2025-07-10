function openAddFoodModal(foodId, foodName, servingSize, calories, protein, carbs, fat) {
    document.getElementById('selected_food_id').value = foodId;
    document.getElementById('selected_food_name').textContent = foodName;
    document.getElementById('selected_food_info').innerHTML =
        `${calories} kcal | P: ${protein}g, C: ${carbs}g, F: ${fat}g (por ${servingSize}g)`;
    document.getElementById('quantity_input').value = servingSize;

    updateNutritionPreview(servingSize, calories, protein, carbs, fat, servingSize);

    document.getElementById('quantity_input').oninput = function() {
        const quantity = parseFloat(this.value) || 0;
        updateNutritionPreview(quantity, calories, protein, carbs, fat, servingSize);
    };

    new bootstrap.Modal(document.getElementById('addFoodModal')).show();
}

function openAddFoodModalFromCard(card) {
    const foodId = card.dataset.foodId;
    const foodName = card.dataset.foodName;
    const servingSize = parseFloat(card.dataset.servingSize);
    const calories = parseInt(card.dataset.calories);
    const protein = parseFloat(card.dataset.protein);
    const carbs = parseFloat(card.dataset.carbs);
    const fat = parseFloat(card.dataset.fat);

    openAddFoodModal(foodId, foodName, servingSize, calories, protein, carbs, fat);
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

function submitAddFoodForm() {
    const foodId = document.getElementById('selected_food_id').value;
    const quantity = document.getElementById('quantity_input').value;

    if (!foodId || !quantity) {
        alert('Por favor, selecione um alimento e informe a quantidade.');
        return;
    }

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = window.location.href;

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);

    const foodInput = document.createElement('input');
    foodInput.type = 'hidden';
    foodInput.name = 'food';
    foodInput.value = foodId;
    form.appendChild(foodInput);

    const quantityInput = document.createElement('input');
    quantityInput.type = 'hidden';
    quantityInput.name = 'quantity_grams';
    quantityInput.value = quantity;
    form.appendChild(quantityInput);

    document.body.appendChild(form);
    form.submit();
}

function openFoodModal(foodId = null, name = '', servingSize = '', calories = '', protein = '', carbs = '', fat = '') {
    document.getElementById('foodModalTitle').textContent = foodId ? 'Editar Alimento' : 'Adicionar Alimento';
    document.getElementById('food_id').value = foodId || '';
    document.getElementById('food_name').value = name;
    document.getElementById('serving_size').value = servingSize;
    document.getElementById('calories').value = calories;
    document.getElementById('protein').value = protein;
    document.getElementById('carbs').value = carbs;
    document.getElementById('fat').value = fat;

    if (!foodId) {
        document.getElementById('foodForm').reset();
        document.getElementById('food_id').value = '';
    }

    new bootstrap.Modal(document.getElementById('foodModal')).show();
}

function editFood(id, name, servingSize, calories, protein, carbs, fat) {
    openFoodModal(id, name, servingSize, calories, protein, carbs, fat);
}

function criarFormularioExclusao(action, redirectUrl = null) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = action;

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);

    if (redirectUrl) {
        const redirectInput = document.createElement('input');
        redirectInput.type = 'hidden';
        redirectInput.name = 'next';
        redirectInput.value = redirectUrl;
        form.appendChild(redirectInput);
    }

    document.body.appendChild(form);
    form.submit();
}

function deleteFood(id, name) {
    if (confirm(`Tem certeza que deseja excluir o alimento "${name}"?`)) {
        criarFormularioExclusao(`/tracker/foods/${id}/delete/`, '/tracker/log/');
    }
}

function deleteFoodFromButton(element) {
    const id = element.dataset.foodId;
    const name = element.dataset.foodName;
    deleteFood(id, name);
}

function editDailyLog(logId, foodName, currentQuantity) {
    document.getElementById('edit_log_id').value = logId;
    document.getElementById('edit_food_name').textContent = foodName;
    document.getElementById('edit_quantity').value = currentQuantity;
    new bootstrap.Modal(document.getElementById('editDailyLogModal')).show();
}

function editDailyLogFromButton(element) {
    const logId = element.dataset.logId;
    const foodName = element.dataset.foodName;
    const currentQuantity = parseFloat(element.dataset.quantity);
    editDailyLog(logId, foodName, currentQuantity);
}

function editFoodFromButton(element) {
    const id = element.dataset.foodId;
    const name = element.dataset.foodName;
    const servingSize = parseFloat(element.dataset.servingSize);
    const calories = parseInt(element.dataset.calories);
    const protein = parseFloat(element.dataset.protein);
    const carbs = parseFloat(element.dataset.carbs);
    const fat = parseFloat(element.dataset.fat);
    editFood(id, name, servingSize, calories, protein, carbs, fat);
}

function deleteDailyLogFromButton(element) {
    const logId = element.dataset.logId;
    const foodName = element.dataset.foodName;
    const quantity = parseFloat(element.dataset.quantity);
    deleteDailyLog(logId, foodName, quantity);
}

function deleteDailyLog(logId, foodName, quantity) {
    if (confirm(`Tem certeza que deseja remover ${quantity}g de "${foodName}" do seu diário?`)) {
        criarFormularioExclusao(`/tracker/log/${logId}/delete/`);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const foodList = document.getElementById('food-list');
    if (foodList) {
        new Sortable(foodList, {
            handle: '.bi-grip-vertical',
            animation: 150,
            onEnd: function() {
                const foodIds = Array.from(foodList.children).map(li =>
                    li.getAttribute('data-food-id')
                );

                fetch('/tracker/daily-log/reorder/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: foodIds.map(id => `food_ids[]=${id}`).join('&')
                })
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        console.error('Erro ao reordenar:', data.error);
                        location.reload();
                    }
                });
            }
        });
    }

    const foodForm = document.getElementById('foodForm');
    if (foodForm) {
        foodForm.onsubmit = function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const foodId = formData.get('food_id');
            const url = foodId ? `/tracker/foods/${foodId}/edit-ajax/` : '/tracker/foods/add-ajax/';

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            }).then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Erro ao salvar alimento');
                }
            });
        };
    }

    const addFoodForm = document.getElementById('addFoodForm');
    if (addFoodForm) {
        addFoodForm.onsubmit = function(e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            }).then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Erro ao adicionar alimento ao diário');
                }
            });
        };
    }

    const editDailyLogForm = document.getElementById('editDailyLogForm');
    if (editDailyLogForm) {
        editDailyLogForm.onsubmit = function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const logId = formData.get('log_id');

            fetch(`/tracker/log/${logId}/edit/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            }).then(response => response.json())
            .then(data => {
                if (data.success) {
                    bootstrap.Modal.getInstance(document.getElementById('editDailyLogModal')).hide();
                    location.reload();
                } else {
                    alert('Erro ao editar quantidade: ' + (data.error || 'Erro desconhecido'));
                }
            }).catch(error => {
                console.error('Erro:', error);
                alert('Erro ao editar quantidade');
            });
        };
    }
});
