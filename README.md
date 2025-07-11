# Sistema de Controle de Calorias, Peso e Treinos

Sistema web desenvolvido em Django para controle completo de alimentação, peso corporal e rotinas de exercícios.

## Funcionalidades

### Controle de Calorias
- Cadastro personalizado de alimentos com informações nutricionais
- Registro diário de consumo alimentar
- Cálculo automático de macronutrientes (proteínas, carboidratos, gorduras)

### Controle de Peso
- Registro de pesagens com data
- Gráficos de evolução do peso
- Cálculo de média móvel (7 dias)
- Estatísticas de peso atual, máximo e mínimo
- Taxa de variação semanal

### Logbook de Treinos
- Criação e gerenciamento de rotinas de exercícios
- Registro detalhado de séries (peso, repetições, notas)
- Progressão de exercícios com gráficos

### Sistema de Usuários
- Autenticação completa (login/logout)

## Tecnologias Utilizadas

- **Backend**: Django 5.2.4
- **Frontend**: Bootstrap 5.3.3, JavaScript
- **Banco de Dados**: SQLite (desenvolvimento)
- **Gráficos**: Highcharts
- **Gerenciamento de Dependências**: uv

## Estrutura do Projeto

```
CalTrackerLogbookWeightTracker/
├── CalTrackerLogbookWeightTracker/    # Configurações do projeto
├── users/                             # App de usuários
├── calories/                          # App de controle de calorias
├── weight/                            # App de controle de peso
├── logbook/                           # App de logbook de treinos
├── templates/                         # Templates HTML
├── static/js/                         # Arquivos JavaScript
├── db.sqlite3                         # Banco de dados
└── manage.py                          # Script de gerenciamento Django
```

## Instalação e Configuração

### Pré-requisitos
- Python 3.13+
- uv (gerenciador de pacotes)

### Passos de Instalação

1. Clone o repositório:
```bash
git clone https://github.com/IlMeloIl/calorie-weight-logbook
cd calorie-weight-logbook
```

2. Instale as dependências:
```bash
uv sync
```

3. Execute as migrações:
```bash
python manage.py migrate
```

4. Crie um superusuário:
```bash
python manage.py createsuperuser
```

5. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

6. Acesse a aplicação em `http://localhost:8000`

## Uso da Aplicação

### Primeiro Acesso
1. Faça login com as credenciais do superuser criado
2. Acesse "Meu Dia" para começar o controle de calorias
3. Vá em "Controle de Peso" para registrar seu peso
4. Use o "Logbook" para criar rotinas e iniciar treinos

### Controle de Calorias
1. Cadastre alimentos com informações nutricionais
2. Adicione alimentos consumidos no dia atual
3. Visualize o resumo nutricional diário
4. Reordene alimentos conforme necessário

### Controle de Peso
1. Registre pesagens regulares
2. Acompanhe a evolução através dos gráficos
3. Monitore estatísticas de peso
4. Edite registros históricos quando necessário

### Logbook de Treinos
1. Crie exercícios personalizados
2. Monte rotinas com exercícios e número de séries
3. Inicie sessões de treino
4. Registre séries executadas
5. Acompanhe progressão nos exercícios
