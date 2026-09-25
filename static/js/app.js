// 1. Função para alternar a exibição das seções
function mudarAba(abaSelecionada) {
    const listaDeAbas = ['entregas', 'frequencia', 'funcionarios', 'competencias'];

    listaDeAbas.forEach(aba => {
        const elementoSecao = document.getElementById(`sec-${aba}`);
        const elementoBotao = document.getElementById(`tab-${aba}`);

        if (aba === abaSelecionada) {
            // Exibe a seção clicada
            elementoSecao.classList.remove('hidden');
            // Destaque visual no botão ativo
            elementoBotao.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
            elementoBotao.classList.remove('text-gray-500');
        } else {
            // Esconde as outras seções
            elementoSecao.classList.add('hidden');
            // Remove destaque dos outros botões
            elementoBotao.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
            elementoBotao.classList.add('text-gray-500');
        }
    });
}
//==================================================================
//2. Módulo de Competências
//==================================================================
let competenciaSelecionadaId = null;
async function carregarCompetencias() {
    try {
        const resposta = await fetch('/competencias');
        const competencias = await resposta.json();
        console.log("Competências carregadas:", competencias);

        const selectCompetencia = document.getElementById('select-competencia');
        if (!selectCompetencia) return;

        selectCompetencia.innerHTML = '<option value="">Selecione uma competência...</option>';

        competencias.forEach(comp => {
            const option = document.createElement('option');
            option.value = comp.id;
            //formata o mes com 0 a esquerda ex: 05/2026
            const mesFormatado = String(comp.mes).padStart(2, '0');
            option.textContent = `${mesFormatado}/${comp.ano}`;
            selectCompetencia.appendChild(option);
        });

        //Seleciona automaticamente a última competência cadastrada, se houver
        if (competencias.length > 0) {
            const ultimaCompetencia = competencias[competencias.length - 1];
            selectCompetencia.value = ultimaCompetencia.id;
            competenciaSelecionadaId = ultimaCompetencia.id;

            //atualiza a tabela de status de entregas com a competencia padrao
            if (typeof carregarStatusEntregas === 'function') {
                carregarStatusEntregas(competenciaSelecionadaId);
            }
        }
    } catch (erro) {
        console.error("Erro ao carregar competências:", erro);
    }    
}

//listenet para disparar busca quando o usuário mudar a competencia no <select>
document.addEventListener('DOMContentLoaded', () => {
    const selectCompetencia = document.getElementById('select-competencia');
    if (selectCompetencia) {
        selectCompetencia.addEventListener('change', (e) => {
            competenciaSelecionadaId = e.target.value;
            if (competenciaSelecionadaId && typeof carregarStatusEntregas === 'function') {
                carregarStatusEntregas(competenciaSelecionadaId);
            }
        });
    }
});

async function salvarCompetencia(event) {
    event.preventDefault();

    const mesDigitado = parseInt(document.getElementById('comp-mes').value);
    const anoDigitado = parseInt(document.getElementById('comp-ano').value);

    const dados = {
        mes: mesDigitado,
        ano: anoDigitado
    };

    try {
        const resposta = await fetch('/competencias', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify(dados)
        });

        if (resposta.ok) {
            alert("Competência cadastrada com sucesso!");
            document.getElementById('form-competencia').reset();
            //recarrega o combo de competencias para exibir a recem-criada
            await carregarCompetencias();
        } else {
            const erro = await resposta.json();
            alert(`Erro: ${erro.detail}`);
        }
    } catch (e) {
        alert("Erro de conexão ao salvar competência.");
    }
}
//==================================================================
//3. Carregar Opções dos Selects (Frequência)
//==================================================================
// Carrega selects de competencias e funcionarios
async function carregarOpcoesSelects() {
    try {
        // 1. Busca as competências cadastradas
        const resComp = await fetch('/competencias');
        const competencias = await resComp.json();

        const selectComp = document.getElementById('freq-competencia');
        if (selectComp) {
            selectComp.innerHTML = '<option value="">Selecione a Competência</option>';
            competencias.forEach(c => {
                selectComp.innerHTML += `<option value="${c.id}">${String(c.mes).padStart(2, '0')}/${c.ano}</option>`;
            });
        }

        // 2. Busca os funcionários cadastrados
        const resFunc = await fetch('/funcionarios');
        const funcionarios = await resFunc.json();

        const selectFunc = document.getElementById('freq-funcionario');
        if (selectFunc) {
            selectFunc.innerHTML = '<option value="">Selecione o Funcionário</option>';
            funcionarios.forEach(f => {
                selectFunc.innerHTML += `<option value="${f.id}">${f.nome} (Matrícula: ${f.matricula})</option>`;
            });
        }
    } catch (erro) {
        console.error("Erro ao carregar opções para os selects:", erro);
    }
}
//==================================================================
//4. Módulo de Funcionários
//==================================================================
// Cadastrar Funcionário
async function salvarFuncionario(event) {
    event.preventDefault();

    const nome = document.getElementById('func-nome').value;
    const matricula = document.getElementById('func-matricula').value;    
    const setor = document.getElementById('func-setor').value;

    try {
        const res = await fetch('/funcionarios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, matricula, setor })
        });

        if (res.ok) {
            alert("Funcionário cadastrado com sucesso!");            
            document.getElementById('form-funcionario').reset();
            carregarTabelaFuncionarios(); // atualiza a tabela
            carregarOpcoesSelects();      // atualiza select da frequencia
        } else {
            const erro = await res.json();
            alert(`Erro: ${erro.detail}`);
        }
    } catch (e) {
        alert("Erro ao conectar com o servidor.");
    }
}

// Listar funcionarios na tabela
async function carregarTabelaFuncionarios() {
    try {
        const res = await fetch('/funcionarios');
        const funcionarios = await res.json();

        const tabela = document.getElementById('tabela-funcionarios');
        if (!tabela) return;

        tabela.innerHTML = ''; // limpa a tabela antes de preencher

        funcionarios.forEach(f => {
            tabela.innerHTML += `
            <tr class="hover:bg-gray-50 border-b">
                <td class="p-3">${f.id}</td>
                <td class="p-3 font-medium">${f.nome}</td>
                <td class="p-3">${f.matricula}</td>
                <td class="p-3">${f.setor}</td>
                <td class="p-3 text-center">
                    <button onclick="deletarFuncionario(${f.id})" class="text-red-600 hover:text-red-800 font-semibold text-xs bg-red-100 px-2 py-1 rounded">
                    Excluir
                    </button>
                </td>
            </tr>
            `;
        });
    } catch (e) {
        console.error("Erro ao listar funcionários:", e);
    }
}

// Deletar Funcionario
async function deletarFuncionario(id) {
    if (!confirm("Tem certeza que deseja remover este funcionário?")) return;

    try {
        const res = await fetch(`/funcionarios/${id}`, { method: 'DELETE' });
        if (res.ok) {
            alert("Funcionário excluído com sucesso!");
            carregarTabelaFuncionarios();
            carregarOpcoesSelects();
        } else {
            const erro = await res.json();
            alert(`Erro: ${erro.detail}`);
        }
    } catch (e) {
        alert("Erro ao excluir funcionário.");
    }
}
//==================================================================
//5. Módulo de Frequência
//==================================================================
//Salvar registro de frequência
async function salvarFrequencia(event) {
    event.preventDefault();

    const funcionarioId = document.getElementById('freq-funcionario').value;
    const competenciaId = document.getElementById('freq-competencia').value;
    const diasTrabalhados = document.getElementById('freq-dias-trabalhados').value;
    const faltasJustificadas = document.getElementById('freq-faltas-justificadas')?.value || 0;
    const faltasInjustificadas = document.getElementById('freq-faltas-injustificadas')?.value || 0;

    if (!funcionarioId || !competenciaId || diasTrabalhados === '') {
        alert("Por favor, preencha todos os campos obrigatórios.");
        return;
    }
    try {
        const resposta = await fetch ('/frequencia', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                funcionario_id: parseInt(funcionarioId),
                competenciaId: parseInt(competenciaId),
                dias_trabalhados: parseInt(diasTrabalhados),
                faltas_justificadas: parseInt(faltasJustificadas),
                faltas_injustificadas: parseInt(faltasInjustificadas)
            })
        });
        const dados = await resposta.json();

        if (resposta.ok) {
            alert(dados.mensagem);
            document.getElementById('form-frequencia').reset();
            carregarFrequencias();
        } else {
            alert(`Erro: ${dados.detail}`);
        }
    } catch (erro) {
        console.error("Erro ao registrar frequência:", erro);
        alert("Erro de conexão ao salvar frequência.");
    }
}
// Carregar tabela de frequências
async function carregarFrequencias() {
    try {
        const resposta = await fetch ('/frequencia');
        const lista = await resposta.json();

        const tabela = document.getElementById('tabela-frequencia');
        if (!tabela) return;

        tabela.innerHTML = '';
        lista.forEach(f => {
            tabela.innerHTML += `
            <tr class="hover:bg-gray-50 border-b">
                <td class="p-3 font-medium">${f.funcionario_nome || f.funcionario_id} (${f.matricula || '-'})</td>
                <td class="p-3 text-center">${f.dias_trabalhados}</td>
                <td class="p-3 text-center">${f.faltas_justificadas}</td>
                <td class="p-3 text-center">${f.faltas_injustificadas}</td>
                <td class="p-3 text-center">
                    <button onclick="deletarFrequencia(${f.id})" class="text-red-600 hover:text-red-800 font-semibold text-xs bg-red-100 px-2 py-1 rounded">
                    Excluir
                    </button>
                </td>
            </tr>
            `;
        });
    } catch (erro) {
        console.error("Erro ao carregar frequências:", erro);
    }
}
//Deletar frequencia
async function deletarFrequencia(id) {
    if (!confirm("Tem certeza que deseja remover este registro de frequência?")) return;
    try {
        const res = await fetch(`/frequencia/${id}`, { method: 'DELETE' });
        const dados = await res.json();
        if (res.ok) {
            alert(dados.mensagem);
            carregarFrequencias();
        } else {
            alert(`Erro: ${dados.detail}`);
        }
    } catch (e) {
        alert("Erro ao excluir frequência.")
    }
}
//==================================================================
//6. Módulo de Entregas
//==================================================================

//Carregar seletor de competências da aba de entregas
async function carregarFiltroCompetenciasEntregas() {
    try {
        const res = await fetch('/competencias');
        if(!res.ok) return;

        const competencias = await res.json();
        const select = document.getElementById('filtro-entrega-competencia');
        if (!select) return;

        select.innerHTML = '<option value= "">Selecione uma Competência...</option>';

        competencias.forEach(c => {
            const mesZero = String(c.mes).padStart(2, '0');
            select.innerHTML += `<option value="${c.id}">${mesZero}/${c.ano}</option>`;
        });

        //Seleciona automaticamente a última competência cadastrada
        if (competencias.length > 0) {
            const ultimaComp = competencias[competencias.length - 1];
            select.value = ultimaComp.id;

            //Carrega os dados da tabela para essa competencia automaticamente
            carregarTabelaEntregas();
        }
    } catch (erro) {
        console.error("Erro ao carregar filtro de competências:", erro);
    }
}

//Evento para atualizar a tabela sempre que o utilizador alterar a competencia no menu suspenso
document.addEventListener('DOMContentLoaded', () => {
    carregarFiltroCompetenciasEntregas();

    const select = document.getElementById('filtro-entrega-competencia');
    if (select) {
        select.addEventListener('change', carregarTabelaEntregas);
    }
});

//Busca e exibe a lista de entregas / elegibilidade
async function carregarTabelaEntregas() {
    const selectComp = document.getElementById('filtro-entrega-competencia');
    const compId = selectComp?.value || '';
    const tabela = document.getElementById('tabela-entregas');
    if (!tabela) return;

    //1.Impede a chamada se nenhuma competência estiver selecionada
    if (!compId) {
        tabela.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-gray-500">Selecione uma competência acima para visualizar o status das entregas.</td></tr>`;
        return;
    }

    try {
        const res = await fetch(`/entregas/status?competencia_id=${compId}`);

        //2.valida se a resposta HTTP é OK antes de processar
        if (!res.ok) {
            const erroApi = await res.text();
            console.error("Erro da API:", erroApi);
            tabela.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500 font-medium">Erro ao carregar os dados das entregas.</td></tr>`;
            return;
        }

        const lista = await res.json();
        tabela.innerHTML = '';

        //3.Garante que seja um Array
        if (!Array.isArray(lista) || lista.length === 0) {
            tabela.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-gray-500">Nenhum registro de frequência/entrega encontrado.</td></tr>`;
            return;
        }

        lista.forEach(item => {
            const badgeElegivel = item.elegivel
                ? `<span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded font-semibold">Elegível</span>`
                : `<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded font-semibold" title="${item.motivo_elegibilidade}">${item.motivo_elegibilidade}</span>`;

            const bagdeStatus = item.entregue
                ? `<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded font-semibold">Entregue</span>`
                : `<span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded font-semibold">Pendentes</span>`;

            //envia o funcionario_id e o compId selecionado
            const botaoAcao = item.elegivel && !item.entregue
                ? `<button onclick="confirmarEntrega(${item.funcionario_id}, ${compId})" class="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1 rounded shadow">Baixar Entrega</button>`
                : (item.entregue ? `<span class="text-xs text-gray-400">Concluído</span>` : `<span class="text-xs text-gray-400">Inapto</span>`);
            
            tabela.innerHTML += `
            <tr class="hover:bg-gray-50 border-b">
                <td class="p-3 font-medium">${item.nome} (${item.matricula})</td>
                <td class="p-3 text-center">${item.competencia}</td>
                <td class="p-3 text-center">${badgeElegivel}</td>
                <td class="p-3 text-center">${bagdeStatus}</td>
                <td class="p-3 text-center text-xs text-gray-500">${item.data_entrega || '-'}</td>
                <td class="p-3 text-center">${botaoAcao}</td>
            </tr>
            `;
        });
    } catch (erro) {
        console.error("Erro ao carregar entregas:", erro);
        tabela.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500 font-medium">Erro na comunicação com o servidor.</td></tr>`;
    }
}

//Registrar a entrega individual
async function confirmarEntrega(funcionarioId, competenciaId) {
    if (!confirm("Confirmar a entrega da cesta básica para este funcionário?")) return;

    try {
        const res = await fetch('/entregas/registrar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                funcionario_id: funcionarioId,
                competencia_id: competenciaId,
                entregue: true
            })
        });

        const dados = await res.json();
        if (res.ok) {
            alert(dados.mensagem || "Entrega registrada com sucesso!");
            carregarTabelaEntregas();
        } else {
            alert(`Erro: ${dados.detail}`);
        }
    } catch (e) {
        alert("Erro ao registrar entrega.");
    }
}

//==================================================================
//Inicialização
//==================================================================
// Executa o carregamento inicial quando o HTML for totalmente lido
document.addEventListener('DOMContentLoaded', () => {
    carregarTabelaFuncionarios();
    carregarOpcoesSelects();
    carregarFrequencias();
    carregarFiltroCompetenciasEntregas();
    carregarTabelaEntregas();
});