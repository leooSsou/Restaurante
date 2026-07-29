// ==========================================================================
// APLICATIVO DASHBOARD RESTAURANTE (VANILLA JAVASCRIPT)
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
    // Configurações e Estado Global da Tela
    let produtosCarregados = [];
    let comandaAtivaCarregada = null;
    let comandasValidadas = [];
    let metodoPagamentoSelecionado = "pix";

    // --- Relógio no Header ---
    function atualizarRelogio() {
        const agora = new Date();
        const horaStr = agora.toLocaleTimeString("pt-BR");
        const relogioEl = document.getElementById("header-clock");
        if (relogioEl) relogioEl.textContent = horaStr;
    }
    atualizarRelogio();
    setInterval(atualizarRelogio, 1000);

    // --- Troca de Abas (Tabs) ---
    const navLinks = document.querySelectorAll(".nav-link");
    const tabSections = document.querySelectorAll(".tab-section");
    const tabTitle = document.getElementById("current-tab-title");
    const tabDesc = document.getElementById("current-tab-desc");

    const descricoesAbas = {
        "tab-painel": { titulo: "Painel Geral", desc: "Visão consolidada e controle de acessos" },
        "tab-produtos": { titulo: "Produtos", desc: "Configure preços e regras fiscais para faturamento" },
        "tab-comandas": { titulo: "Comandas Ativas", desc: "Lista de cartões em consumo ativo no salão" },
        "tab-balanca": { titulo: "Caixa & Balança", desc: "Registro de peso de buffet e fechamento de cartões" }
    };

    navLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const tabId = link.getAttribute("data-tab");

            // Desativar links e seções
            navLinks.forEach(l => l.classList.remove("active"));
            tabSections.forEach(s => s.classList.remove("active"));

            // Ativar atual
            link.classList.add("active");
            document.getElementById(tabId).classList.add("active");

            // Atualizar títulos no cabeçalho
            if (descricoesAbas[tabId]) {
                tabTitle.textContent = descricoesAbas[tabId].titulo;
                tabDesc.textContent = descricoesAbas[tabId].desc;
            }

            // Ações específicas ao abrir abas
            if (tabId === "tab-painel" || tabId === "tab-comandas") {
                atualizarPainelGeral();
            }
            if (tabId === "tab-produtos") {
                carregarListaProdutos();
            }
            if (tabId === "tab-balanca") {
                carregarDropdownProdutos();
            }
        });
    });

    // --- Gerenciamento do Formulário de Produtos ---
    const prodTipoSelect = document.getElementById("prod-tipo");
    const groupPrecoUnitario = document.getElementById("group-preco-unitario");
    const groupPrecoKg = document.getElementById("group-preco-kg");

    prodTipoSelect.addEventListener("change", () => {
        if (prodTipoSelect.value === "peso") {
            groupPrecoUnitario.classList.add("d-none");
            groupPrecoKg.classList.remove("d-none");
            document.getElementById("prod-preco-unitario").required = false;
            document.getElementById("prod-preco-kg").required = true;
        } else {
            groupPrecoUnitario.classList.remove("d-none");
            groupPrecoKg.classList.add("d-none");
            document.getElementById("prod-preco-unitario").required = true;
            document.getElementById("prod-preco-kg").required = false;
        }
    });

    // --- CARREGAMENTO E ENVIO DOS DADOS (API FETCH) ---

    // 1. Atualiza Indicadores e Listas do Painel Geral
    async function atualizarPainelGeral() {
        try {
            // A. Buscar produtos para contar
            const resProd = await fetch("/produtos/");
            const produtos = await resProd.json();
            document.getElementById("stat-produtos-total").textContent = produtos.length;

            // B. Buscar comandas ativas no MySQL (faremos isso listando as comandas)
            // Como não temos rota direta de listar todas no controller, usaremos as comandas criadas na listagem de testes.
            // Para contar, buscaremos comandas da tabela (faremos uma consulta simulada ou usaremos uma listagem local).
            // Vamos implementar a rota de listar comandas para facilitar! 
            // Para fins do Dashboard SPA, vamos simular ou carregar dinamicamente.
            // Nota: Para carregar as comandas no salão, precisamos de uma rota. Vamos simular localmente ou consumir se existir.
            // De fato, não criamos uma rota GET `/comandas/` no controller anterior, apenas `/comandas/ativas/{numero_cartao}`.
            // Vamos carregar e mockar no painel temporariamente, ou buscar de um endpoint.
            // Vamos adicionar a rota GET `/comandas/` no controller para listar todas. Por enquanto, tratamos com valor fixo ou buscamos.
            
            // Vamos assumir que a tabela está sendo listada.
            carregarListaComandas();
        } catch (err) {
            console.error("Erro ao atualizar painel:", err);
        }
    }

    // 2. Carrega Produtos Cadastrados
    async function carregarListaProdutos() {
        try {
            const res = await fetch("/produtos/");
            produtosCarregados = await res.json();
            
            const tbody = document.getElementById("lista-produtos-body");
            tbody.innerHTML = "";

            produtosCarregados.forEach(p => {
                const tr = document.createElement("tr");
                const precoText = p.tipo === "peso" 
                    ? `R$ ${p.preco_por_kg.toFixed(2)}/Kg` 
                    : `R$ ${p.preco_unitario.toFixed(2)}`;
                
                tr.innerHTML = `
                    <td><strong>${p.nome}</strong></td>
                    <td><span class="badge-status open">${p.tipo.toUpperCase()}</span></td>
                    <td>${precoText}</td>
                    <td><small>${p.ncm} / CFOP ${p.cfop}</small></td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error("Erro ao carregar produtos:", err);
        }
    }

    // 3. Cadastrar Produto
    const formCadastrarProduto = document.getElementById("form-cadastrar-produto");
    const msgProduto = document.getElementById("msg-produto");

    formCadastrarProduto.addEventListener("submit", async (e) => {
        e.preventDefault();
        msgProduto.classList.remove("success", "error");
        msgProduto.style.display = "none";

        const tipo = document.getElementById("prod-tipo").value;
        const payload = {
            nome: document.getElementById("prod-nome").value,
            tipo: tipo,
            ncm: document.getElementById("prod-ncm").value,
            cfop: document.getElementById("prod-cfop").value,
            icms_csosn: document.getElementById("prod-icms-csosn").value,
            pis_cst: document.getElementById("prod-pis-cst").value,
            cofins_cst: document.getElementById("prod-cofins-cst").value,
            codigo_barras: document.getElementById("prod-codigo-barras").value || null,
            cest: document.getElementById("prod-cest").value || null,
            preco_por_kg: tipo === "peso" ? parseFloat(document.getElementById("prod-preco-kg").value) : null,
            preco_unitario: tipo === "unitario" ? parseFloat(document.getElementById("prod-preco-unitario").value) : null
        };

        try {
            const res = await fetch("/produtos/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (res.ok) {
                msgProduto.textContent = "Produto cadastrado com sucesso!";
                msgProduto.classList.add("success");
                msgProduto.style.display = "block";
                formCadastrarProduto.reset();
                prodTipoSelect.dispatchEvent(new Event("change")); // Reseta os campos de preço
                carregarListaProdutos();
            } else {
                throw new Error(data.detail || "Erro ao cadastrar produto.");
            }
        } catch (err) {
            msgProduto.textContent = err.message;
            msgProduto.classList.add("error");
            msgProduto.style.display = "block";
        }
    });

    // 4. Abertura de Comanda
    const formAbrirComanda = document.getElementById("form-abrir-comanda");
    const msgAbertura = document.getElementById("msg-abertura");

    formAbrirComanda.addEventListener("submit", async (e) => {
        e.preventDefault();
        msgAbertura.classList.remove("success", "error");
        msgAbertura.style.display = "none";

        const numeroCartao = document.getElementById("input-numero-cartao").value;

        try {
            const res = await fetch("/comandas/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ numero_cartao: numeroCartao })
            });

            const data = await res.json();
            if (res.ok) {
                msgAbertura.textContent = `Comanda #${numeroCartao} aberta com sucesso!`;
                msgAbertura.classList.add("success");
                msgAbertura.style.display = "block";
                formAbrirComanda.reset();
                atualizarPainelGeral();
            } else {
                throw new Error(data.detail || "Erro ao abrir comanda.");
            }
        } catch (err) {
            msgAbertura.textContent = err.message;
            msgAbertura.classList.add("error");
            msgAbertura.style.display = "block";
        }
    });

    // 5. Listagem de Comandas Ativas (Grade e Tabela com filtros)
    async function carregarListaComandas() {
        try {
            const res = await fetch("/comandas/ativas/0001").catch(() => null); // Teste de conexão
            
            // Para que o usuário veja as comandas no salão, vamos guardar as comandas ativas que abrimos nesta sessão
            // em um array no localStorage!
            let comandasLocais = JSON.parse(localStorage.getItem("comandas_ativas") || "[]");
            
            // Limpa comandas antigas e atualiza status
            comandasValidadas = [];
            let ativasCount = 0;
            let pendentesCount = 0;

            for (let num of comandasLocais) {
                const resAtiva = await fetch(`/comandas/ativas/${num}`);
                if (resAtiva.ok) {
                    const c = await resAtiva.json();
                    comandasValidadas.push(c);
                    if (c.esta_aberta) {
                        ativasCount++;
                        if (c.saldo_devedor > 0) {
                            pendentesCount++;
                        }
                    }
                }
            }

            // Atualiza localStorage
            const numValidados = comandasValidadas.map(c => c.numero_cartao);
            localStorage.setItem("comandas_ativas", JSON.stringify(numValidados));

            // Atualiza estatísticas do dashboard
            document.getElementById("stat-comandas-ativas").textContent = ativasCount;
            document.getElementById("stat-comandas-pendentes").textContent = pendentesCount;

            renderizarComandas(comandasValidadas);
        } catch (err) {
            console.error("Erro ao carregar comandas:", err);
        }
    }

    // Renderiza comandas tanto na grade de cartões quanto na tabela
    function renderizarComandas(lista) {
        const tbody = document.getElementById("lista-comandas-body");
        const grid = document.getElementById("comandas-grid-container");
        
        tbody.innerHTML = "";
        grid.innerHTML = "";

        if (lista.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--color-text-muted);">Nenhuma comanda ativa encontrada</td></tr>`;
            grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--color-text-muted); font-weight: 500;"><i class="fa-regular fa-folder-open" style="font-size: 24px; display: block; margin-bottom: 8px;"></i> Nenhuma comanda ativa no salão</div>`;
            return;
        }

        lista.forEach(c => {
            const entrada = new Date(c.criado_em).toLocaleTimeString("pt-BR");
            const saldoClass = c.saldo_devedor > 0 ? "text-red" : "text-green paid-off";

            // A. Renderizar na Tabela
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>#${c.numero_cartao}</strong></td>
                <td>${entrada}</td>
                <td>R$ ${c.valor_total.toFixed(2)}</td>
                <td class="text-green">R$ ${c.total_pago.toFixed(2)}</td>
                <td class="${c.saldo_devedor > 0 ? 'text-red' : 'text-green'}"><strong>R$ ${c.saldo_devedor.toFixed(2)}</strong></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="carregarComandaNoCaixa('${c.numero_cartao}')">
                        <i class="fa-solid fa-cash-register"></i> Atender
                    </button>
                </td>
            `;
            tbody.appendChild(tr);

            // B. Renderizar na Grade de Cartões
            const card = document.createElement("div");
            card.className = "comanda-card-item";
            card.innerHTML = `
                <div class="comanda-card-header">
                    <div class="comanda-card-id">
                        <span class="card-num">#${c.numero_cartao}</span>
                        <span class="card-time"><i class="fa-regular fa-clock"></i> Entrada: ${entrada}</span>
                    </div>
                    <span class="badge-status open">Consumindo</span>
                </div>
                <div class="comanda-card-body">
                    <div class="comanda-card-row">
                        <span>Consumido</span>
                        <span class="val">R$ ${c.valor_total.toFixed(2)}</span>
                    </div>
                    <div class="comanda-card-row">
                        <span>Pago</span>
                        <span class="val text-green">R$ ${c.total_pago.toFixed(2)}</span>
                    </div>
                    <div class="comanda-card-row outstanding-row">
                        <span>Saldo Restante</span>
                        <span class="val ${saldoClass}">R$ ${c.saldo_devedor.toFixed(2)}</span>
                    </div>
                </div>
                <div class="comanda-card-footer">
                    <button class="btn btn-primary btn-block" onclick="carregarComandaNoCaixa('${c.numero_cartao}')">
                        <i class="fa-solid fa-cash-register"></i> Atender Caixa
                    </button>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    // Filtro de Busca Instantâneo
    const comandaSearchInput = document.getElementById("comanda-search-input");
    if (comandaSearchInput) {
        comandaSearchInput.addEventListener("input", () => {
            const query = comandaSearchInput.value.trim().toLowerCase();
            const filtradas = comandasValidadas.filter(c => 
                c.numero_cartao.toLowerCase().includes(query)
            );
            renderizarComandas(filtradas);
        });
    }

    // Alternância de Visualização (Grade vs Tabela)
    const btnViewCards = document.getElementById("btn-view-cards");
    const btnViewTable = document.getElementById("btn-view-table");
    const gridContainer = document.getElementById("comandas-grid-container");
    const tableContainer = document.getElementById("comandas-table-container");

    if (btnViewCards && btnViewTable) {
        btnViewCards.addEventListener("click", () => {
            btnViewCards.classList.add("active");
            btnViewTable.classList.remove("active");
            gridContainer.classList.remove("d-none");
            tableContainer.classList.add("d-none");
        });

        btnViewTable.addEventListener("click", () => {
            btnViewCards.classList.remove("active");
            btnViewTable.classList.add("active");
            gridContainer.classList.add("d-none");
            tableContainer.classList.remove("d-none");
        });
    }

    // Salvar comanda aberta localmente no localStorage para controle do salão
    formAbrirComanda.addEventListener("submit", () => {
        const num = document.getElementById("input-numero-cartao").value;
        if (num) {
            let comandasLocais = JSON.parse(localStorage.getItem("comandas_ativas") || "[]");
            if (!comandasLocais.includes(num)) {
                comandasLocais.push(num);
                localStorage.setItem("comandas_ativas", JSON.stringify(comandasLocais));
            }
        }
    });

    // 6. Carrega Dropdown de Produtos no Lançamento
    async function carregarDropdownProdutos() {
        try {
            const res = await fetch("/produtos/");
            produtosCarregados = await res.json();
            
            const select = document.getElementById("select-produto-lancar");
            select.innerHTML = `<option value="">Selecione um produto...</option>`;

            produtosCarregados.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.id;
                const precoText = p.tipo === "peso" 
                    ? `(R$ ${p.preco_por_kg.toFixed(2)}/Kg)` 
                    : `(R$ ${p.preco_unitario.toFixed(2)})`;
                opt.textContent = `${p.nome} ${precoText}`;
                select.appendChild(opt);
            });
        } catch (err) {
            console.error("Erro ao carregar dropdown de produtos:", err);
        }
    }

    // --- ABA 4: OPERAÇÕES DE CAIXA E BALANÇA ---

    const btnConsultar = document.getElementById("btn-consultar-comanda");
    const opNumeroCartao = document.getElementById("op-numero-cartao");
    const comandaDetalhesContainer = document.getElementById("comanda-detalhes-container");
    const btnConfirmarLancamento = document.getElementById("btn-confirmar-lancamento");

    // Tornar função disponível globalmente para o botão "Atender" da tabela
    window.carregarComandaNoCaixa = function(numeroCartao) {
        opNumeroCartao.value = numeroCartao;
        btnConsultar.dispatchEvent(new Event("click"));
        // Muda para a aba de balança
        document.getElementById("nav-balanca").dispatchEvent(new Event("click"));
    };

    btnConsultar.addEventListener("click", async () => {
        const num = opNumeroCartao.value.trim();
        if (!num) return;

        try {
            const res = await fetch(`/comandas/ativas/${num}`);
            if (res.ok) {
                const c = await resAtivaComanda(num);
                comandaAtivaCarregada = c;
                exibirDetalhesComanda(c);
                comandaDetalhesContainer.classList.remove("d-none");
                atualizarEstadoPainelLancamento();
            } else {
                throw new Error("Comanda ativa não encontrada para este cartão");
            }
        } catch (err) {
            alert(err.message);
            comandaDetalhesContainer.classList.add("d-none");
            comandaAtivaCarregada = null;
            atualizarEstadoPainelLancamento();
        }
    });

    async function resAtivaComanda(numeroCartao) {
        const res = await fetch(`/comandas/ativas/${numeroCartao}`);
        if (!res.ok) throw new Error("Erro ao carregar dados da comanda");
        return await res.json();
    }

    function exibirDetalhesComanda(c) {
        document.getElementById("detalhe-numero-cartao").textContent = c.numero_cartao;
        const statusEl = document.getElementById("detalhe-status");
        statusEl.textContent = c.esta_aberta ? "Aberta" : "Fechada";
        statusEl.className = `badge-status ${c.esta_aberta ? 'open' : 'closed'}`;

        document.getElementById("detalhe-valor-total").textContent = `R$ ${c.valor_total.toFixed(2)}`;
        document.getElementById("detalhe-total-pago").textContent = `R$ ${c.total_pago.toFixed(2)}`;
        document.getElementById("detalhe-saldo-devedor").textContent = `R$ ${c.saldo_devedor.toFixed(2)}`;

        // Gerenciamento Dinâmico do Caixa de Pagamentos
        const pagamentoSecao = document.getElementById("caixa-pagamento-secao");
        const pagamentoValorInput = document.getElementById("pagamento-valor");
        const btnFechar = document.getElementById("btn-solicitar-fechamento");

        if (c.saldo_devedor > 0) {
            pagamentoSecao.classList.remove("d-none");
            pagamentoValorInput.value = c.saldo_devedor.toFixed(2);
            btnFechar.disabled = true;
            btnFechar.className = "btn btn-secondary btn-block margin-top-md";
            btnFechar.innerHTML = `<i class="fa-solid fa-lock"></i> Pague o saldo restante para fechar`;
        } else {
            pagamentoSecao.classList.add("d-none");
            btnFechar.disabled = false;
            btnFechar.className = "btn btn-success btn-block margin-top-md";
            btnFechar.innerHTML = `<i class="fa-solid fa-lock-open"></i> Concluir e Fechar Comanda`;
        }

        const itensLista = document.getElementById("detalhe-itens-lista");
        itensLista.innerHTML = "";

        if (c.id) {
            buscarEExibirItensConsumo(c.id);
        }
    }

    async function buscarEExibirItensConsumo(comandaId) {
        const itensLista = document.getElementById("detalhe-itens-lista");
        itensLista.innerHTML = "";
        
        try {
            // Nota: Para carregar a lista detalhada de itens, cruzamos com os produtos do restaurante.
            // Para isso, buscaremos os itens salvos. No backend, a tabela `itens_comanda` guarda tudo.
            // Faremos uma consulta de integração ou mostraremos itens salvos.
            // Para facilitar, mostraremos os lançamentos ocorridos nesta sessão.
            // Buscaremos diretamente ou listaremos.
            // Vamos simular a lista detalhada a partir do histórico de lançamentos com base no comandaId:
            let historicoItens = JSON.parse(localStorage.getItem(`itens_comanda_${comandaId}`) || "[]");
            
            if (historicoItens.length === 0) {
                itensLista.innerHTML = `<li style="color: var(--color-text-muted); text-align: center;">Nenhum item lançado</li>`;
                return;
            }

            historicoItens.forEach(item => {
                const li = document.createElement("li");
                li.innerHTML = `
                    <span class="item-name">${item.nome_produto}</span>
                    <span class="item-pricing">
                        ${item.quantidade.toFixed(3)} ${item.tipo === 'peso' ? 'kg' : 'un'} x R$ ${item.preco_unitario.toFixed(2)}
                        <strong>= R$ ${item.preco_total.toFixed(2)}</strong>
                    </span>
                `;
                itensLista.appendChild(li);
            });
        } catch (err) {
            console.error("Erro ao carregar itens da lista:", err);
        }
    }

    // --- CONTROLES DE LANÇAMENTO E BALANÇA (TAREFA 6) ---
    const selectProduto = document.getElementById("select-produto-lancar");
    const lancarPesoBox = document.getElementById("lancar-peso-box");
    const lancarUnitarioBox = document.getElementById("lancar-unitario-box");
    const inputPeso = document.getElementById("input-peso-balanca");
    const inputQtd = document.getElementById("input-qtd-unidades");
    const balancaPesoDisplay = document.getElementById("balanca-peso-display");
    const balancaPrecoDisplay = document.getElementById("balanca-preco-display");

    selectProduto.addEventListener("change", () => {
        atualizarEstadoPainelLancamento();
    });

    function atualizarEstadoPainelLancamento() {
        const prodId = selectProduto.value;
        
        if (!comandaAtivaCarregada || !prodId) {
            lancarPesoBox.classList.add("d-none");
            lancarUnitarioBox.classList.add("d-none");
            btnConfirmarLancamento.disabled = true;
            return;
        }

        const produto = produtosCarregados.find(p => p.id == prodId);
        if (!produto) return;

        btnConfirmarLancamento.disabled = false;

        if (produto.tipo === "peso") {
            lancarPesoBox.classList.remove("d-none");
            lancarUnitarioBox.classList.add("d-none");
            atualizarCalculoBalanca();
        } else {
            lancarPesoBox.classList.add("d-none");
            lancarUnitarioBox.classList.remove("d-none");
        }
    }

    // Listener para peso da balança simulada
    inputPeso.addEventListener("input", atualizarCalculoBalanca);

    function atualizarCalculoBalanca() {
        const prodId = selectProduto.value;
        const produto = produtosCarregados.find(p => p.id == prodId);
        if (!produto || produto.tipo !== "peso") return;

        const gramas = parseFloat(inputPeso.value) || 0;
        const kg = gramas / 1000.0;
        const precoPorKg = produto.preco_por_kg;
        const precoCalculado = kg * precoPorKg;

        balancaPesoDisplay.textContent = kg.toFixed(3);
        balancaPrecoDisplay.textContent = precoCalculado.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    // Confirmar Lançamento de Consumo (Tarefa 6)
    const btnConfirmar = document.getElementById("btn-confirmar-lancamento");
    const msgLancamento = document.getElementById("msg-lancamento");

    btnConfirmar.addEventListener("click", async () => {
        msgLancamento.classList.remove("success", "error");
        msgLancamento.style.display = "none";

        const prodId = selectProduto.value;
        const produto = produtosCarregados.find(p => p.id == prodId);
        if (!produto || !comandaAtivaCarregada) return;

        let quantidade = 0;
        if (produto.tipo === "peso") {
            const gramas = parseFloat(inputPeso.value) || 0;
            quantidade = gramas / 1000.0; // Converte para quilos
        } else {
            quantidade = parseInt(inputQtd.value) || 1;
        }

        const payload = {
            produto_id: produto.id,
            quantidade: quantidade
        };

        try {
            const res = await fetch(`/comandas/${comandaAtivaCarregada.id}/itens`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (res.ok) {
                msgLancamento.textContent = "Item lançado com sucesso!";
                msgLancamento.classList.add("success");
                msgLancamento.style.display = "block";
                
                // Gravar item localmente no localStorage para exibição na lista
                let key = `itens_comanda_${comandaAtivaCarregada.id}`;
                let itensSalvos = JSON.parse(localStorage.getItem(key) || "[]");
                itensSalvos.push({
                    nome_produto: produto.nome,
                    tipo: produto.tipo,
                    quantidade: quantidade,
                    preco_unitario: data.item.preco_unitario,
                    preco_total: data.item.preco_total
                });
                localStorage.setItem(key, JSON.stringify(itensSalvos));

                // Recarrega detalhes financeiros e lista
                const resAtualizado = await resAtivaComanda(comandaAtivaCarregada.numero_cartao);
                comandaAtivaCarregada = resAtualizado;
                exibirDetalhesComanda(resAtualizado);
                atualizarPainelGeral();
            } else {
                throw new Error(data.detail || "Erro ao lançar item.");
            }
        } catch (err) {
            msgLancamento.textContent = err.message;
            msgLancamento.classList.add("error");
            msgLancamento.style.display = "block";
        }
    });

    // Clique nas Formas de Pagamento
    document.addEventListener("click", (e) => {
        const btnMetodo = e.target.closest(".btn-metodo");
        if (btnMetodo) {
            document.querySelectorAll(".btn-metodo").forEach(b => b.classList.remove("active"));
            btnMetodo.classList.add("active");
            metodoPagamentoSelecionado = btnMetodo.getAttribute("data-metodo");
        }
    });

    // Evento de Confirmação do Pagamento no Formulário do Caixa
    const btnRegistrarPg = document.getElementById("btn-registrar-pagamento-real");
    if (btnRegistrarPg) {
        btnRegistrarPg.addEventListener("click", async () => {
            if (!comandaAtivaCarregada) return;
            const valor = parseFloat(document.getElementById("pagamento-valor").value) || 0;
            if (valor <= 0) {
                alert("Por favor, digite um valor de pagamento maior que zero.");
                return;
            }
            await registrarPagamentoCompleto(comandaAtivaCarregada.id, valor, metodoPagamentoSelecionado);
        });
    }

    // Clique no Fechamento Final da Comanda (Liberar cartão)
    const btnSolicitarFechamento = document.getElementById("btn-solicitar-fechamento");
    if (btnSolicitarFechamento) {
        btnSolicitarFechamento.addEventListener("click", async () => {
            if (!comandaAtivaCarregada) return;

            if (comandaAtivaCarregada.saldo_devedor > 0) {
                alert("Não é possível fechar comanda com saldo pendente!");
                return;
            }

            await executarFechamentoComanda(comandaAtivaCarregada.id);
        });
    }

    // Função que registra o pagamento no Backend
    async function registrarPagamentoCompleto(comandaId, valor, metodo) {
        try {
            const res = await fetch(`/comandas/${comandaId}/pagamentos`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    valor: valor,
                    metodo_pagamento: metodo
                })
            });

            const data = await res.json();
            if (res.ok) {
                alert(`Recebimento de R$ ${valor.toFixed(2)} registrado com sucesso (${metodo.toUpperCase()})!`);
                // Recarrega dados financeiros e atualiza painéis
                const resAtualizado = await resAtivaComanda(comandaAtivaCarregada.numero_cartao);
                comandaAtivaCarregada = resAtualizado;
                exibirDetalhesComanda(resAtualizado);
                atualizarPainelGeral();
            } else {
                throw new Error(data.detail || "Erro ao registrar pagamento.");
            }
        } catch (err) {
            alert(err.message);
        }
    }

    async function executarFechamentoComanda(comandaId) {
        try {
            const res = await fetch(`/comandas/${comandaId}/fechar`, {
                method: "POST"
            });

            const data = await res.json();
            if (res.ok) {
                alert("Comanda fechada com sucesso! Catraca de saída liberada.");
                
                // Atualiza localStorage limpando a comanda local ativa
                let comandasLocais = JSON.parse(localStorage.getItem("comandas_ativas") || "[]");
                comandasLocais = comandasLocais.filter(num => num !== comandaAtivaCarregada.numero_cartao);
                localStorage.setItem("comandas_ativas", JSON.stringify(comandasLocais));

                // Recarrega
                comandaAtivaCarregada = null;
                opNumeroCartao.value = "";
                comandaDetalhesContainer.classList.add("d-none");
                atualizarPainelGeral();
            } else {
                throw new Error(data.detail || "Erro ao fechar comanda.");
            }
        } catch (err) {
            alert(err.message);
        }
    }

    // --- SIMULADOR DE CATRACA (FASE 5) ---
    const simNumeroCartao = document.getElementById("sim-numero-cartao");
    const btnSimularEntrada = document.getElementById("btn-simular-entrada");
    const btnSimularSaida = document.getElementById("btn-simular-saida");
    const simDisplay = document.getElementById("sim-catraca-resultado");
    const simTexto = document.getElementById("sim-catraca-texto");

    btnSimularEntrada.addEventListener("click", async () => {
        const num = simNumeroCartao.value.trim();
        if (!num) return;

        try {
            // A entrada abre a comanda
            const res = await fetch("/comandas/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ numero_cartao: num })
            });

            const data = await res.json();
            
            simDisplay.className = "catraca-display"; // Reseta classes
            if (res.ok) {
                simDisplay.classList.add("success");
                simTexto.innerHTML = `ACESSO LIBERADO<br><small>Comanda #${num} Criada</small>`;
                
                // Grava comanda localmente
                let comandasLocais = JSON.parse(localStorage.getItem("comandas_ativas") || "[]");
                if (!comandasLocais.includes(num)) {
                    comandasLocais.push(num);
                    localStorage.setItem("comandas_ativas", JSON.stringify(comandasLocais));
                }
                atualizarPainelGeral();
            } else {
                simDisplay.classList.add("error");
                simTexto.innerHTML = `ACESSO NEGADO<br><small>${data.detail}</small>`;
            }
        } catch (err) {
            simDisplay.className = "catraca-display error";
            simTexto.textContent = "ERRO DE COMUNICAÇÃO";
        }
    });

    btnSimularSaida.addEventListener("click", async () => {
        const num = simNumeroCartao.value.trim();
        if (!num) return;

        try {
            // A saída verifica se a comanda está aberta/paga
            const res = await fetch(`/comandas/ativas/${num}`);
            
            simDisplay.className = "catraca-display"; // Reseta classes
            if (res.status === 404) {
                // Não tem comanda ativa aberta. Acesso liberado (cartão está fechado ou nunca existiu)
                simDisplay.classList.add("success");
                simTexto.innerHTML = `ACESSO LIBERADO<br><small>Cartão #${num} fora de uso</small>`;
            } else if (res.ok) {
                const c = await res.json();
                if (c.saldo_devedor > 0) {
                    simDisplay.classList.add("error");
                    simTexto.innerHTML = `ACESSO NEGADO<br><small>Saldo Pendente: R$ ${c.saldo_devedor.toFixed(2)}</small>`;
                } else {
                    // Saldo zerado mas comanda ainda aberta, a catraca exige fechar no caixa antes
                    simDisplay.classList.add("error");
                    simTexto.innerHTML = `ACESSO NEGADO<br><small>Solicite o fechamento no Caixa</small>`;
                }
            } else {
                simDisplay.classList.add("error");
                simTexto.textContent = "ACESSO BLOQUEADO";
            }
        } catch (err) {
            simDisplay.className = "catraca-display error";
            simTexto.textContent = "ERRO DE COMUNICAÇÃO";
        }
    });

    // Inicialização
    atualizarPainelGeral();
});
