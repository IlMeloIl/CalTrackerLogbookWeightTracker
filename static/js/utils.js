const AppUtils = {
    modal: {
        abrir(modalId, dadosCampos = {}) {
            if (!modalId || typeof modalId !== 'string') {
                console.error('modalId deve ser uma string válida');
                return null;
            }

            const modal = document.getElementById(modalId);
            if (!modal) {
                console.error(`Modal ${modalId} não encontrado`);
                return null;
            }

            Object.entries(dadosCampos).forEach(([campoId, valor]) => {
                const elemento = document.getElementById(campoId);
                if (elemento) {
                    if (elemento.tagName === 'INPUT' || elemento.tagName === 'TEXTAREA' || elemento.tagName === 'SELECT') {
                        elemento.value = valor || '';
                    } else {
                        elemento.textContent = valor || '';
                    }
                }
            });

            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            return bootstrapModal;
        },

        fechar(modalId) {
            if (!modalId || typeof modalId !== 'string') {
                console.error('modalId deve ser uma string válida');
                return;
            }

            const modal = document.getElementById(modalId);
            if (modal) {
                const bootstrapModal = bootstrap.Modal.getInstance(modal);
                if (bootstrapModal) {
                    bootstrapModal.hide();
                }
            }
        },

        resetarFormulario(formularioId) {
            if (!formularioId || typeof formularioId !== 'string') {
                console.error('formularioId deve ser uma string válida');
                return;
            }

            const formulario = document.getElementById(formularioId);
            if (formulario) {
                formulario.reset();
                const camposHidden = formulario.querySelectorAll('input[type="hidden"]:not([name="csrfmiddlewaretoken"])');
                camposHidden.forEach(campo => campo.value = '');
            }
        }
    },

    fetch: {

        obterCsrfToken() {
            const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
            return tokenElement ? tokenElement.value : '';
        },

        async requisicaoPost(url, dados = {}, opcoes = {}) {
            if (!url || typeof url !== 'string') {
                throw new Error('URL deve ser uma string válida');
            }

            const timeoutMs = opcoes.timeout || 30000;
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

            const configuracaoPadrao = {
                method: 'POST',
                signal: controller.signal,
                headers: {
                    'X-CSRFToken': this.obterCsrfToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                    ...opcoes.headers
                }
            };

            if (dados instanceof FormData) {
                delete configuracaoPadrao.headers['Content-Type'];
                configuracaoPadrao.body = dados;
            } else if (typeof dados === 'object') {
                configuracaoPadrao.body = new URLSearchParams(dados).toString();
            } else {
                configuracaoPadrao.body = dados;
            }

            try {
                const response = await fetch(url, { ...configuracaoPadrao, ...opcoes });
                clearTimeout(timeoutId);

                if (opcoes.retornarResponse) {
                    return response;
                }

                if (response.redirected || (response.status >= 300 && response.status < 400)) {
                    if (opcoes.onSucesso) {
                        opcoes.onSucesso({ success: true });
                    } else if (opcoes.recarregarPagina !== false) {
                        location.reload();
                    }
                    return { success: true };
                }

                let data;
                try {
                    data = await response.json();
                } catch (jsonError) {
                    if (response.ok) {
                        if (opcoes.onSucesso) {
                            opcoes.onSucesso({ success: true });
                        } else if (opcoes.recarregarPagina !== false) {
                            location.reload();
                        }
                        return { success: true };
                    }
                    throw jsonError;
                }

                if (data.success || data.sucesso) {
                    if (opcoes.onSucesso) {
                        opcoes.onSucesso(data);
                    } else if (opcoes.recarregarPagina !== false) {
                        location.reload();
                    }
                } else {
                    const mensagemErro = data.error || data.erro || 'Erro desconhecido';
                    if (opcoes.onErro) {
                        opcoes.onErro(mensagemErro);
                    } else {
                        alert(`Erro: ${mensagemErro}`);
                    }
                }

                return data;
            } catch (error) {
                clearTimeout(timeoutId);
                console.error('Erro na requisição:', error);

                let mensagemErro = opcoes.mensagemErroCustomizada || 'Erro na requisição';
                if (error.name === 'AbortError') {
                    mensagemErro = 'Requisição cancelada por timeout';
                }

                if (opcoes.onErro) {
                    opcoes.onErro(mensagemErro);
                } else {
                    alert(mensagemErro);
                }
                throw error;
            }
        }
    },

    confirmacao: {

        excluir(nomeItem, callback, tipoItem = 'item') {
            if (typeof callback !== 'function') {
                console.error('Callback deve ser uma função');
                return;
            }
            const mensagem = `Tem certeza que deseja excluir ${tipoItem} "${nomeItem}"?`;
            if (confirm(mensagem)) {
                callback();
            }
        },

        acao(mensagem, callback) {
            if (typeof callback !== 'function') {
                console.error('Callback deve ser uma função');
                return;
            }
            if (confirm(mensagem)) {
                callback();
            }
        }
    },

    dados: {

        extrairDeElemento(elemento, mapeamentoCampos = {}) {
            if (!elemento || !elemento.dataset) {
                console.error('Elemento inválido ou sem dataset');
                return {};
            }

            const dados = {};

            Object.entries(mapeamentoCampos).forEach(([chave, atributoData]) => {
                const valor = elemento.dataset[atributoData];
                dados[chave] = valor !== undefined ? valor : null;
            });

            return dados;
        },

        converterTipos(dados, tiposEsperados = {}) {
            if (!dados || typeof dados !== 'object') {
                console.error('Dados devem ser um objeto válido');
                return {};
            }

            const dadosConvertidos = { ...dados };

            Object.entries(tiposEsperados).forEach(([chave, tipo]) => {
                if (dadosConvertidos[chave] !== undefined && dadosConvertidos[chave] !== null) {
                    try {
                        switch (tipo) {
                            case 'number':
                            case 'float':
                                dadosConvertidos[chave] = parseFloat(dadosConvertidos[chave]);
                                break;
                            case 'int':
                            case 'integer':
                                dadosConvertidos[chave] = parseInt(dadosConvertidos[chave]);
                                break;
                            case 'boolean':
                                dadosConvertidos[chave] = dadosConvertidos[chave] === 'true' || dadosConvertidos[chave] === true;
                                break;
                        }
                    } catch (error) {
                        console.warn(`Erro ao converter ${chave} para ${tipo}:`, error);
                    }
                }
            });

            return dadosConvertidos;
        }
    },

    formulario: {
        criarDinamico(action, campos = {}, opcoes = {}) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = action;

            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = AppUtils.fetch.obterCsrfToken();
            form.appendChild(csrfInput);

            Object.entries(campos).forEach(([nome, valor]) => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = nome;
                input.value = valor;
                form.appendChild(input);
            });

            if (opcoes.urlRedirecionamento) {
                const redirectInput = document.createElement('input');
                redirectInput.type = 'hidden';
                redirectInput.name = 'next';
                redirectInput.value = opcoes.urlRedirecionamento;
                form.appendChild(redirectInput);
            }

            document.body.appendChild(form);

            if (opcoes.submeterAutomaticamente !== false) {
                form.submit();
            }

            return form;
        },

        configurarSubmitAjax(formId, opcoes = {}) {
            const form = document.getElementById(formId);
            if (!form) {
                console.warn(`Formulário ${formId} não encontrado`);
                return null;
            }

            form.addEventListener('submit', function(e) {
                e.preventDefault();

                const formData = new FormData(this);
                let url = opcoes.url;

                if (opcoes.urlComId) {
                    const idField = opcoes.campoId || `${opcoes.entidade}_id`;
                    const id = formData.get(idField);
                    url = opcoes.urlComId.replace('{id}', id);
                }

                const configRequisicao = {
                    mensagemErroCustomizada: opcoes.mensagemErro || 'Erro ao processar formulário',
                    ...opcoes.configRequisicao
                };

                AppUtils.fetch.requisicaoPost(url, formData, configRequisicao);
            });

            return form;
        },

        configurarFormulariosEdicao(configuracoes) {
            configuracoes.forEach(config => {
                AppUtils.formulario.configurarSubmitAjax(config.formId, {
                    urlComId: config.urlTemplate,
                    campoId: config.campoId,
                    entidade: config.entidade,
                    mensagemErro: config.mensagemErro
                });
            });
        },

        configurarAjaxPadrao(formId, configuracao = {}) {
            const form = document.getElementById(formId);
            if (!form) {
                console.warn(`Formulário ${formId} não encontrado para configuração AJAX`);
                return null;
            }

            const config = {
                url: form.action || window.location.href,
                modalId: null,
                onSucesso: null,
                onErro: null,
                recarregarPagina: true,
                mensagemErro: 'Erro ao processar formulário',
                ...configuracao
            };

            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);

                let urlFinal = config.url;
                if (typeof config.url === 'function') {
                    urlFinal = config.url(formData);
                }

                const opcoesFetch = {
                    mensagemErroCustomizada: config.mensagemErro,
                    onSucesso: (data) => {
                        if (config.onSucesso) {
                            config.onSucesso(data);
                        } else {
                            if (config.modalId) {
                                AppUtils.modal.fechar(config.modalId);
                            }
                            if (config.recarregarPagina) {
                                location.reload();
                            }
                        }
                    },
                    onErro: (erro) => {
                        if (config.onErro) {
                            config.onErro(erro);
                        } else {
                            alert(`${config.mensagemErro}: ${erro}`);
                        }
                    }
                };

                AppUtils.fetch.requisicaoPost(urlFinal, formData, opcoesFetch);
            });

            return form;
        },

        configurarMultiplosFormularios(configuracoes) {
            configuracoes.forEach(({ formId, config }) => {
                this.configurarAjaxPadrao(formId, config);
            });
        }

    },

    url: {
        atualizarParametros(parametros) {
            const url = new URL(window.location);
            Object.entries(parametros).forEach(([chave, valor]) => {
                if (valor !== null && valor !== undefined) {
                    url.searchParams.set(chave, valor);
                } else {
                    url.searchParams.delete(chave);
                }
            });
            window.location.href = url.toString();
        },

        obterParametro(nome) {
            const url = new URL(window.location);
            return url.searchParams.get(nome);
        }
    },

    ui: {
        mostrarIndicadorCarregamento(elemento, mostrar = true) {
            if (mostrar) {
                elemento.style.display = 'block';
            } else {
                elemento.style.display = 'none';
            }
        },

    },

    dependencias: {
        verificarAppUtils(nomeScript) {
            if (typeof AppUtils === 'undefined') {
                console.error(`❌ ${nomeScript}: AppUtils não está disponível. Certifique-se de que utils.js foi carregado.`);
                if (typeof DependencyChecker !== 'undefined') {
                    DependencyChecker.executarAposDependencias(['AppUtils'], function() {
                        console.log(`✅ ${nomeScript}: Dependências carregadas, reinicializando...`);
                        location.reload();
                    }, nomeScript);
                }
                return false;
            }
            return true;
        },

        verificarAppUtilsNoDOMContentLoaded(nomeScript) {
            if (typeof AppUtils === 'undefined') {
                console.error(`❌ ${nomeScript}: AppUtils não disponível no DOMContentLoaded`);
                return false;
            }
            return true;
        },

        verificacaoInicialCompleta(nomeScript, opcoes = {}) {
            const config = {
                usarDependencyChecker: true,
                mostrarWarning: true,
                ...opcoes
            };

            if (typeof AppUtils === 'undefined') {
                if (config.mostrarWarning) {
                    console.warn(`⚠️ ${nomeScript}: AppUtils não disponível, mas funções serão expostas globalmente`);
                }

                if (config.usarDependencyChecker && typeof DependencyChecker !== 'undefined') {
                    DependencyChecker.executarAposDependencias(['AppUtils'], function() {
                        console.log(`✅ ${nomeScript}: Dependências carregadas, reinicializando...`);
                        location.reload();
                    }, nomeScript);
                }
                return false;
            } else {
                console.log(`✅ ${nomeScript}: AppUtils disponível`);
                return true;
            }
        }
    },

    acoes: {
        criarFuncaoEditarDeElemento(mapeamentoCampos, funcaoEdicao) {
            return function(element) {
                const dados = AppUtils.dados.extrairDeElemento(element, mapeamentoCampos);
                funcaoEdicao(dados);
            };
        },

        criarFuncaoExcluirDeElemento(mapeamentoCampos, funcaoExclusao) {
            return function(element) {
                const dados = AppUtils.dados.extrairDeElemento(element, mapeamentoCampos);
                funcaoExclusao(dados);
            };
        },

        criarFuncaoEditarComParametros(mapeamentoCampos, funcaoEdicao) {
            return function(element) {
                const dados = AppUtils.dados.extrairDeElemento(element, mapeamentoCampos);
                const parametros = Object.values(dados);
                funcaoEdicao(...parametros);
            };
        },

        criarFuncaoExcluirComParametros(mapeamentoCampos, funcaoExclusao) {
            return function(element) {
                const dados = AppUtils.dados.extrairDeElemento(element, mapeamentoCampos);
                const parametros = Object.values(dados);
                funcaoExclusao(...parametros);
            };
        },

        criarFuncaoFromButton(mapeamentoCampos, funcaoAcao, opcoes = {}) {
            const config = {
                tiposConversao: {},
                usarParametros: false,
                nomeScript: 'script',
                ...opcoes
            };

            return function(element) {
                if (typeof AppUtils === 'undefined') {
                    console.error(`AppUtils não disponível para função FromButton em ${config.nomeScript}`);
                    return;
                }

                const dados = AppUtils.dados.extrairDeElemento(element, mapeamentoCampos);

                let dadosProcessados = dados;
                if (Object.keys(config.tiposConversao).length > 0) {
                    dadosProcessados = AppUtils.dados.converterTipos(dados, config.tiposConversao);
                }

                if (config.usarParametros) {
                    const parametros = Object.values(dadosProcessados);
                    funcaoAcao(...parametros);
                } else {
                    funcaoAcao(dadosProcessados);
                }
            };
        }
    },

    autoSave: {
        configurarCamposComTimeout(seletor, funcaoSalvar, delay = 1000) {
            const elementos = document.querySelectorAll(seletor);
            const timeouts = new Map();

            elementos.forEach(elemento => {
                const form = elemento.closest('form') || elemento;

                function handleInputChange() {
                    const timeoutId = timeouts.get(elemento);
                    if (timeoutId) {
                        clearTimeout(timeoutId);
                    }

                    const novoTimeout = setTimeout(() => {
                        funcaoSalvar(form, elemento);
                    }, delay);

                    timeouts.set(elemento, novoTimeout);
                }

                function handleBlur() {
                    const timeoutId = timeouts.get(elemento);
                    if (timeoutId) {
                        clearTimeout(timeoutId);
                    }
                    funcaoSalvar(form, elemento);
                }

                elemento.addEventListener('input', handleInputChange);
                elemento.addEventListener('blur', handleBlur);
            });

            return timeouts;
        },

        configurarFormularioComTimeout(form, funcaoSalvar, camposSelector = 'input, textarea, select', delay = 1000) {
            if (typeof form === 'string') {
                form = document.getElementById(form);
            }

            if (!form) {
                console.warn('Formulário não encontrado para auto-save');
                return null;
            }

            const campos = form.querySelectorAll(camposSelector);
            let saveTimeout;

            function handleInputChange() {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    funcaoSalvar(form);
                }, delay);
            }

            function handleBlur() {
                clearTimeout(saveTimeout);
                funcaoSalvar(form);
            }

            campos.forEach(campo => {
                campo.addEventListener('input', handleInputChange);
                campo.addEventListener('blur', handleBlur);
            });

            return { form, campos, clearTimeout: () => clearTimeout(saveTimeout) };
        }
    },

    sortable: {
        configurarReordenacao(elementoId, opcoes = {}) {
            const elemento = document.getElementById(elementoId);
            if (!elemento) {
                console.warn(`Elemento ${elementoId} não encontrado para sortable`);
                return null;
            }

            const configuracaoPadrao = {
                handle: '.bi-grip-vertical',
                animation: 150,
                onEnd: function() {
                    const ids = Array.from(elemento.children).map(item => {
                        const atributoId = opcoes.atributoId || 'data-id';
                        return item.getAttribute(atributoId);
                    });

                    const nomeParametro = opcoes.nomeParametro || 'ids[]';
                    const dados = ids.map(id => `${nomeParametro}=${id}`).join('&');

                    const configRequisicao = {
                        recarregarPagina: false,
                        onErro: (erro) => {
                            console.error('Erro ao reordenar:', erro);
                            if (opcoes.recarregarEmErro !== false) {
                                location.reload();
                            }
                        },
                        ...opcoes.configRequisicao
                    };

                    AppUtils.fetch.requisicaoPost(opcoes.url, dados, configRequisicao);
                }
            };

            const configuracaoFinal = { ...configuracaoPadrao, ...opcoes.sortableConfig };

            if (typeof Sortable !== 'undefined') {
                return new Sortable(elemento, configuracaoFinal);
            } else {
                console.error('Biblioteca Sortable não está disponível');
                return null;
            }
        }
    },

    exposicaoGlobal: {
        exponerFuncoes(funcoes, nomeScript, debug = true) {
            if (!funcoes || typeof funcoes !== 'object') {
                console.error(`${nomeScript}: Objeto de funções inválido para exposição global`);
                return;
            }

            const funcoesExpostas = [];

            Object.entries(funcoes).forEach(([nome, funcao]) => {
                if (typeof funcao === 'function') {
                    window[nome] = funcao;
                    funcoesExpostas.push(nome);
                } else {
                    console.warn(`${nomeScript}: ${nome} não é uma função válida para exposição`);
                }
            });

            if (debug && funcoesExpostas.length > 0) {
                console.log(`🔧 ${nomeScript}: Funções expostas globalmente`);
                funcoesExpostas.forEach(nome => {
                    console.log(`${nome}:`, typeof window[nome]);
                });
            }

            return funcoesExpostas;
        }
    },

    graficos: {
        criarConfiguracaoBase(opcoes = {}) {
            const config = {
                titulo: 'Gráfico',
                tituloY: 'Valores',
                tipoGrafico: 'line',
                habilitarZoom: false,
                tipoEixoX: 'category',
                ...opcoes
            };

            const configuracaoBase = {
                chart: {
                    type: config.tipoGrafico,
                    backgroundColor: 'transparent',
                    style: {
                        fontFamily: 'inherit'
                    }
                },
                title: {
                    text: config.titulo,
                    style: {
                        color: '#ffffff'
                    }
                },
                xAxis: {
                    labels: {
                        style: {
                            color: '#ffffff'
                        }
                    },
                    lineColor: '#6c757d',
                    tickColor: '#6c757d'
                },
                yAxis: {
                    title: {
                        text: config.tituloY,
                        style: {
                            color: '#ffffff'
                        }
                    },
                    labels: {
                        style: {
                            color: '#ffffff'
                        }
                    },
                    gridLineColor: '#6c757d'
                },
                legend: {
                    itemStyle: {
                        color: '#ffffff'
                    },
                    itemHoverStyle: {
                        color: '#cccccc'
                    }
                },
                tooltip: {
                    backgroundColor: '#343a40',
                    style: {
                        color: '#ffffff'
                    }
                },
                plotOptions: {
                    line: {
                        dataLabels: {
                            enabled: false
                        },
                        enableMouseTracking: true
                    }
                },
                credits: {
                    enabled: false
                }
            };

            if (config.habilitarZoom) {
                configuracaoBase.chart.zoomType = 'x';
            }

            if (config.tipoEixoX === 'datetime') {
                configuracaoBase.xAxis.type = 'datetime';
            }

            return configuracaoBase;
        },

        inicializarGrafico(elementoGraficoId, elementoDadosId, opcoes = {}) {
            if (typeof Highcharts === 'undefined') {
                console.warn('Highcharts não está disponível para inicializar gráfico');
                return null;
            }

            const elementoDados = document.getElementById(elementoDadosId);
            if (!elementoDados) {
                console.warn(`Elemento de dados ${elementoDadosId} não encontrado`);
                return null;
            }

            let dadosGrafico;
            try {
                dadosGrafico = JSON.parse(elementoDados.textContent);
            } catch (error) {
                console.error('Erro ao fazer parse dos dados do gráfico:', error);
                return null;
            }

            if (opcoes.processarDados && typeof opcoes.processarDados === 'function') {
                dadosGrafico = opcoes.processarDados(dadosGrafico);
            }

            if (!dadosGrafico || (dadosGrafico.data && dadosGrafico.data.length === 0)) {
                console.warn('Dados do gráfico estão vazios');
                return null;
            }

            const configuracaoFinal = dadosGrafico || opcoes.configuracaoGrafico;

            return Highcharts.chart(elementoGraficoId, configuracaoFinal);
        },

        inicializarComProcessamento(elementoGraficoId, elementoDadosId, configuracao = {}) {
            if (typeof Highcharts === 'undefined') {
                console.warn('Highcharts não está disponível para inicializar gráfico');
                return null;
            }

            const elementoDados = document.getElementById(elementoDadosId);
            if (!elementoDados) {
                console.warn(`Elemento de dados ${elementoDadosId} não encontrado`);
                return null;
            }

            let dadosGrafico;
            try {
                dadosGrafico = JSON.parse(elementoDados.textContent);
            } catch (error) {
                console.error('Erro ao fazer parse dos dados do gráfico:', error);
                return null;
            }

            if (configuracao.processadorDados && typeof configuracao.processadorDados === 'function') {
                dadosGrafico = configuracao.processadorDados(dadosGrafico);
            }

            if (!dadosGrafico) {
                console.warn('Dados do gráfico estão vazios após processamento');
                return null;
            }

            const configuracaoFinal = configuracao.configuracaoBase || dadosGrafico;

            return Highcharts.chart(elementoGraficoId, configuracaoFinal);
        }
    },

    scripts: {

        inicializar(nomeScript, funcoes = {}, callbackDOMReady = null, opcoes = {}) {
            const config = {
                verificarDependencias: true,
                exponerGlobalmente: true,
                configurarDOMReady: true,
                ...opcoes
            };

            let appUtilsDisponivel = typeof AppUtils !== 'undefined';

            if (config.verificarDependencias) {
                if (appUtilsDisponivel) {
                    AppUtils.dependencias.verificacaoInicialCompleta(nomeScript);
                } else {
                    console.warn(`⚠️ ${nomeScript}: AppUtils não disponível, mas funções serão expostas globalmente`);
                    if (typeof DependencyChecker !== 'undefined') {
                        DependencyChecker.executarAposDependencias(['AppUtils'], function() {
                            console.log(`✅ ${nomeScript}: Dependências carregadas, reinicializando...`);
                            location.reload();
                        }, nomeScript);
                    }
                }
            }

            if (config.exponerGlobalmente && Object.keys(funcoes).length > 0) {
                if (appUtilsDisponivel) {
                    AppUtils.exposicaoGlobal.exponerFuncoes(funcoes, nomeScript);
                } else {

                    Object.entries(funcoes).forEach(([nome, funcao]) => {
                        if (typeof funcao === 'function') {
                            window[nome] = funcao;
                        }
                    });
                    console.log(`🔧 ${nomeScript}: Funções expostas globalmente (fallback)`);
                }
            }

            if (config.configurarDOMReady && callbackDOMReady) {
                document.addEventListener('DOMContentLoaded', function() {
                    console.log(`🔧 ${nomeScript}: DOMContentLoaded executado`);

                    if (typeof AppUtils === 'undefined') {
                        console.error(`❌ ${nomeScript}: AppUtils não disponível no DOMContentLoaded`);
                        return;
                    }

                    callbackDOMReady();
                });
            }

            return appUtilsDisponivel;
        }
    },

    entidades: {

        abrirModalEdicaoGenerico(modalId, dadosEntidade, mapeamentoCampos, tituloEdicao, tituloAdicao = null) {
            if (typeof AppUtils === 'undefined') {
                console.error('AppUtils não disponível para abrirModalEdicaoGenerico');
                return;
            }

            const dadosCampos = {};

            Object.entries(mapeamentoCampos).forEach(([propriedadeEntidade, campoModal]) => {
                dadosCampos[campoModal] = dadosEntidade[propriedadeEntidade] || '';
            });

            if (mapeamentoCampos.titulo) {
                const isEdicao = dadosEntidade.id !== null && dadosEntidade.id !== undefined;
                dadosCampos[mapeamentoCampos.titulo] = isEdicao ? tituloEdicao : (tituloAdicao || tituloEdicao);
            }

            AppUtils.modal.abrir(modalId, dadosCampos);
        },

        excluirEntidadeComConfirmacao(id, nome, urlExclusao, tipoEntidade, opcoesRequisicao = {}) {
            if (typeof AppUtils === 'undefined') {
                console.error('AppUtils não disponível para excluirEntidadeComConfirmacao');
                return;
            }

            const configuracaoPadrao = {
                mensagemErroCustomizada: `Erro ao excluir ${tipoEntidade}`,
                ...opcoesRequisicao
            };

            AppUtils.confirmacao.excluir(nome, () => {
                AppUtils.fetch.requisicaoPost(urlExclusao, {}, configuracaoPadrao);
            }, tipoEntidade);
        },

        criarFuncaoFromButtonGenerico(mapeamentoCampos, funcaoAcao, opcoes = {}, tipoAcao = 'action') {
            return typeof AppUtils !== 'undefined' ?
                AppUtils.acoes.criarFuncaoFromButton(mapeamentoCampos, funcaoAcao, opcoes) :
                function(element) {
                    console.error(`AppUtils não disponível para ${tipoAcao}FromButton em ${opcoes.nomeScript || 'script'}`);
                };
        },

        configurarFormulariosAjaxPadrao(configuracoes, opcoesPadroes = {}) {
            if (typeof AppUtils === 'undefined') {
                console.error('AppUtils não disponível para configurarFormulariosAjaxPadrao');
                return;
            }

            configuracoes.forEach(config => {
                const configCompleta = {
                    recarregarPagina: true,
                    ...opcoesPadroes,
                    ...config.config
                };

 
                if (configCompleta.urlComId) {
                    AppUtils.formulario.configurarSubmitAjax(config.formId, configCompleta);
                } else {

                    AppUtils.formulario.configurarAjaxPadrao(config.formId, configCompleta);
                }
            });
        },

        inicializarScriptPadrao(nomeScript, funcoesExpostas = {}, configuracaoFormularios = [], callbackInicializacao = null) {
            if (typeof AppUtils === 'undefined') {
                console.error('AppUtils não disponível para inicializarScriptPadrao');
                return;
            }

            AppUtils.scripts.inicializar(nomeScript, funcoesExpostas, function() {

                if (configuracaoFormularios.length > 0) {
                    AppUtils.entidades.configurarFormulariosAjaxPadrao(configuracaoFormularios);
                }


                if (callbackInicializacao && typeof callbackInicializacao === 'function') {
                    callbackInicializacao();
                }

                console.log(`✅ ${nomeScript}: Inicialização completa`);
            });
        }
    },

    templates: {

        criarModal(configuracao) {
            const config = {
                id: 'modal',
                titulo: 'Modal',
                conteudoBody: '',
                botoes: [
                    { texto: 'Cancelar', classe: 'btn-secondary', acao: 'data-bs-dismiss="modal"' },
                    { texto: 'Salvar', classe: 'btn-primary', tipo: 'submit' }
                ],
                formId: null,
                tamanho: '',
                ...configuracao
            };

            const classesTamanho = config.tamanho ? ` modal-${config.tamanho}` : '';
            const tagForm = config.formId ? 'form' : 'div';
            const atributosForm = config.formId ? `id="${config.formId}" method="post"` : '';

            const botoesHtml = config.botoes.map(botao => {
                const tipo = botao.tipo ? `type="${botao.tipo}"` : 'type="button"';
                const acao = botao.acao || '';
                return `<button ${tipo} class="btn ${botao.classe}" ${acao}>${botao.texto}</button>`;
            }).join('\n          ');

            return `
<div class="modal fade" id="${config.id}" tabindex="-1">
  <div class="modal-dialog${classesTamanho}">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">${config.titulo}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <${tagForm} ${atributosForm}>
        <div class="modal-body">
          ${config.conteudoBody}
        </div>
        <div class="modal-footer">
          ${botoesHtml}
        </div>
      </${tagForm}>
    </div>
  </div>
</div>`.trim();
        },

        criarBotoesAcao(configuracao) {
            const config = {
                dados: {},
                acoes: ['edit', 'delete'],
                tamanho: 'sm',
                grupo: true,
                ...configuracao
            };

            const classeTamanho = config.tamanho !== 'md' ? ` btn-${config.tamanho}` : '';

            const tiposAcao = {
                edit: {
                    classe: 'btn-outline-primary',
                    icone: 'bi-pencil',
                    funcao: 'editFromButton'
                },
                delete: {
                    classe: 'btn-outline-danger',
                    icone: 'bi-trash',
                    funcao: 'deleteFromButton'
                },
                view: {
                    classe: 'btn-outline-info',
                    icone: 'bi-eye',
                    funcao: 'viewFromButton'
                }
            };

            const dataAttributes = Object.entries(config.dados)
                .map(([chave, valor]) => `data-${chave}="${valor}"`)
                .join(' ');

            const botoesHtml = config.acoes.map(acao => {
                const tipoAcao = tiposAcao[acao];
                if (!tipoAcao) return '';

                return `<button type="button" class="btn ${tipoAcao.classe}${classeTamanho}" ${dataAttributes} onclick="${tipoAcao.funcao}(this)">
    <i class="bi ${tipoAcao.icone}"></i>
  </button>`;
            }).join('\n  ');

            if (config.grupo) {
                return `<div class="btn-group${classeTamanho}" role="group">
  ${botoesHtml}
</div>`;
            }

            return botoesHtml;
        }
    }
};

if (typeof window !== 'undefined') {
    window.AppUtils = AppUtils;

    window.dispatchEvent(new CustomEvent('AppUtilsLoaded', { detail: AppUtils }));

    if (window.location.search.includes('debug=true')) {
        console.log('AppUtils carregado com sucesso:', Object.keys(AppUtils));
    }
} else {
    console.error('Ambiente window não disponível - AppUtils não pode ser inicializado');
}
