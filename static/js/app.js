//1. Função para alternar a exibição das seções
function mudarAba(abaSelecionada){
    const listaDeAbas = ['entregas', 'frequencia', 'funcionarios', 'competencias'];

    listaDeAbas.forEach(aba => {
        const elementoSecao = document.getElementById(`sec-${aba}`);
        const elementoBotao = document.getElementById(`tab-${aba}`);

        if (aba === abaSelecionada) {
            //Exibe a seção clicada
            elementoSecao.classList.remove('hidden');
            //Destaque visual no botão ativo
            elementoBotao.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
            elementoBotao.classList.remove('text-gray-500');
        } else {
            //Esconde as outras seções
            elementoSecao.classList.add('hidden');
            //Remove destaque dos outros botões
            elementoBotao.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
            elementoBotao.classList.add('text-gray-500');
        }
    });
}
//2. Módulo de competências
async function carregarCompetencias() {
    const resposta = await fetch('/competencias');
    const competencias = await resposta.json();
    console.log("Competência cadastrada com sucesso:", competencias);    
}
async function salvarCompetencia(event) {
    event.preventDefault();

    const mesDigitado = parseInt(document.getElementById('comp-mes').value);
    const anoDigitado = parseInt(document.getElementById('comp-ano').value);

    const dados = {
        mes: mesDigitado,
        ano: anoDigitado
    };
    const resposta = await fetch ('/competencias', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados)
    });
    if (resposta.ok) {
        alert("Competência cadastrada com sucesso!");
        document.getElementById('form-competencia').request();
    } else {
        const erro = await resposta.json();
        alert(`Erro: ${erro.detail}`);
    }
}
//Carrega selects de competencias e funcionarios
async function carregarOpcoesSelects() {
    try {
        //1. Busca as competências cadastradas
        const resComp = await fetch('/competencias');
        const competencias = await resComp.json();

        const selectComp = document.getElementById('freq-competencia');
        if (selectComp) {
            selectComp.innerHTML = '<option value="">Selecione a Competência</option>';
            competencias.forEach(c => {
                selectComp.innerHTML += `<option value = "${f.id}">${f.nome} (Matrícula: ${f.matricula})</option>`;
            });
        }
    } catch (erro) {
        console.error("Erro ao carregar opções para os selects:", erro);
    }
}

//Cadastrar Funcionário
async function salvarFuncionario(event) {
    event.preventDefault();

    const nome = document.getElementById('func-nome').value;
    const matricula = document.getElementById('func-matricula').value;
    const setor = document.getElementById('func.setor').value;

    try {
        const res = await fetch('/funcionarios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({ nome, matricula, setor})
        });

        if (res.ok) {
            alert("Funcionário cadastrado com sucesso!");
            document.getElementById('form-funcionario').rest();
            carregarTabelaFuncionarios(); //atualiza a tabela
            carregarOpcoesSelects(); //atualiza select da frequencia
        } else {
            const erro = await res.json();
            alert(`Erro: ${erro.detail}`);
        }
    } catch (e) {
        alert("Erro ao conectar com o servidor.");
    }
}

//Listar funcionarios na tabela
async function carregarTabelaFuncionarios() {
    try {
        const res = await fetch ('/funcionarios');
        const funcionarios = await res.json();

        const tabela = document.getElementById('tabela-funcionarios');
        if (!tabela) return;

        tabela.innerHTML = ''; //limpa a tabela antes de preencher

        funcionarios.forEach(f =>{
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

//Deletar Funcionario
async function deletarFuncionario(id) {
    if (!confirm("Tem certeza que deseja remover este funcionário?")) return;

    try {
        const res = await fetch(`/funcionarios/${id}`, { method: 'DELETE' });
        if (res.ok) {
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

//executa o carregamento inicial quando o HTML for totalmente lido
document.addEventListener('DOMContentLoaded', () => {
    carregarTabelaFuncionarios();
    carregarOpcoesSelects();
});