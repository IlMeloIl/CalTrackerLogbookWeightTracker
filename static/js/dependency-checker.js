(function() {
    'use strict';

    const DEPENDENCIAS_OBRIGATORIAS = {
        'AppUtils': {
            objeto: 'window.AppUtils',
            descricao: 'Utilitários centralizados da aplicação',
            arquivo: 'utils.js'
        },
        'bootstrap': {
            objeto: 'window.bootstrap',
            descricao: 'Framework Bootstrap',
            arquivo: 'bootstrap.bundle.min.js'
        }
    };

    const TIMEOUT_VERIFICACAO = 10000; // 10 segundos
    const INTERVALO_VERIFICACAO = 100; // 100ms

    function verificarDependencia(caminho) {
        try {
            const partes = caminho.split('.');
            let objeto = window;
            
            for (const parte of partes) {
                if (parte === 'window') continue;
                if (!objeto || typeof objeto[parte] === 'undefined') {
                    return false;
                }
                objeto = objeto[parte];
            }
            
            return true;
        } catch (error) {
            return false;
        }
    }

    function aguardarDependencia(nome, config) {
        return new Promise((resolve, reject) => {
            const inicioTempo = Date.now();
            
            function verificar() {
                if (verificarDependencia(config.objeto)) {
                    resolve();
                    return;
                }
                
                if (Date.now() - inicioTempo > TIMEOUT_VERIFICACAO) {
                    reject(new Error(
                        `Timeout: Dependência '${nome}' (${config.descricao}) não foi carregada. ` +
                        `Verifique se o arquivo '${config.arquivo}' está sendo carregado corretamente.`
                    ));
                    return;
                }
                
                setTimeout(verificar, INTERVALO_VERIFICACAO);
            }
            
            verificar();
        });
    }

    async function verificarTodasDependencias() {
        const promessas = Object.entries(DEPENDENCIAS_OBRIGATORIAS).map(([nome, config]) => 
            aguardarDependencia(nome, config)
        );
        
        try {
            await Promise.all(promessas);
            console.log('✅ Todas as dependências foram carregadas com sucesso');
            return true;
        } catch (error) {
            console.error('❌ Erro ao carregar dependências:', error.message);
            
            if (typeof alert !== 'undefined') {
                alert(
                    'Erro ao carregar recursos da aplicação. ' +
                    'Por favor, recarregue a página. Se o problema persistir, ' +
                    'entre em contato com o suporte.'
                );
            }
            
            throw error;
        }
    }

    function criarVerificadorParaScript(dependenciasNecessarias, nomeScript) {
        return async function() {
            const dependenciasFaltando = dependenciasNecessarias.filter(nome => 
                !verificarDependencia(DEPENDENCIAS_OBRIGATORIAS[nome]?.objeto)
            );
            
            if (dependenciasFaltando.length > 0) {
                console.warn(
                    `⚠️ Script '${nomeScript}' aguardando dependências:`, 
                    dependenciasFaltando
                );
                
                const promessas = dependenciasFaltando.map(nome => 
                    aguardarDependencia(nome, DEPENDENCIAS_OBRIGATORIAS[nome])
                );
                
                await Promise.all(promessas);
                console.log(`✅ Dependências carregadas para '${nomeScript}'`);
            }
            
            return true;
        };
    }

    function executarAposDependencias(dependencias, callback, nomeScript = 'script') {
        if (typeof callback !== 'function') {
            console.error('Callback deve ser uma função');
            return;
        }
        
        const verificador = criarVerificadorParaScript(dependencias, nomeScript);
        
        verificador()
            .then(() => callback())
            .catch(error => {
                console.error(`Erro ao executar '${nomeScript}':`, error);
            });
    }

    window.DependencyChecker = {
        verificarDependencia,
        aguardarDependencia,
        verificarTodasDependencias,
        criarVerificadorParaScript,
        executarAposDependencias,
        DEPENDENCIAS_OBRIGATORIAS
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', verificarTodasDependencias);
    } else {
        setTimeout(verificarTodasDependencias, 0);
    }

    console.log('🔍 Sistema de verificação de dependências inicializado');
})();
