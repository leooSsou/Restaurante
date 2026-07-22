# Diretrizes de Desenvolvimento: Sistema Restaurante (Kg + Balança/Catraca)

Este documento define as regras, padrões arquiteturais e metodologias de desenvolvimento a serem seguidos obrigatoriamente por todos os desenvolvedores (humanos e agentes de IA) no projeto.

---

## 1. Stack Tecnológica
* **Linguagem**: Python (v3.10+)
* **Backend Framework**: FastAPI (desempenho assíncrono e documentação automática)
* **Bancos de Dados**:
  * **Relacional**: MySQL (para dados estruturados, transacionais: comandas, vendas, pagamentos, produtos)
  * **NoSQL**: MongoDB (para auditoria de acessos de catraca, logs de hardware e eventos)
* **Testes**: Pytest

---

## 2. Padrões de Nomenclatura e Estilo de Código
* **Estilo Geral**: PEP 8 para Python.
  * **Classes**: `PascalCase` (ex: `CriarComandaUseCase`, `BalancaAdapter`)
  * **Funções / Métodos / Variáveis**: `snake_case` (ex: `ler_peso_em_gramas()`, `comanda_id`)
  * **Constantes**: `UPPER_CASE` (ex: `LIMITE_PESO_MAXIMO`)
* **Idioma do Código**: **Português** (obrigatoriamente) para termos de domínio, banco de dados, variáveis e classes.
* **Termos de Domínio Padrão**:
  * Comanda / Cartão -> `Comanda` / `Cartao`
  * Balança -> `Balanca`
  * Catraca -> `Catraca`
  * Produto / Preço por Kg -> `Produto` / `PrecoPorKg`
  * Pagamento -> `Pagamento`
  * Cupom Fiscal -> `CupomFiscal`

---

## 3. Arquitetura do Sistema
Adotaremos **Clean Architecture / Hexagonal (Ports & Adapters)** para garantir que o núcleo do negócio seja independente de banco de dados, frameworks web e, principalmente, de hardware físico.

### Camadas do Projeto:
1. **Domínio (Domain)**:
   * Contém entidades puras e regras de negócio essenciais.
   * Não pode importar nada de frameworks, ORMs ou bibliotecas externas.
   * Exemplo: `src/domain/entities/comanda.py`, `src/domain/value_objects/peso.py`.
2. **Casos de Uso (Use Cases)**:
   * Contém as regras de aplicação (ex: ler peso da balança e salvar na comanda).
   * Orquestra as entidades. Importa apenas interfaces (portas).
3. **Adaptadores (Adapters)**:
   * **Entrada**: Controllers FastAPI, routers, payloads de requisição.
   * **Saída**: Implementações de repositórios (SQLAlchemy, Motor/MongoDB), Gateways de hardware (Balança, Catraca).
4. **Infraestrutura (Infrastructure)**:
   * Configurações de conexão de banco de dados, inicialização do servidor web, drivers de comunicação serial ou sockets TCP/IP.

---

## 4. Integração com Hardware (Simuladores)
Como balanças e catracas dependem de conexão física, **é obrigatório** seguir o padrão de Porta/Adaptador com suporte a Simulação local:

* Para cada hardware (Balança, Catraca, Impressora), definiremos uma **Porta** (Interface Abstrata):
  ```python
  class BalancaInterface(ABC):
      @abstractmethod
      async def ler_peso_em_gramas(self) -> int:
          pass
  ```
* Criaremos sempre **duas** implementações:
  1. `PhysicalBalancaAdapter` (ou similar): Para produção, comunicando-se via serial/USB ou rede com a balança real.
  2. `SimuladorBalancaAdapter`: Para desenvolvimento e testes, que simula leituras (lendo valores de um arquivo mock, de uma variável de ambiente ou gerando peso randômico configurável).
* Uma variável de ambiente (`ENVIRONMENT=development` vs `ENVIRONMENT=production`) definirá qual adaptador injetar.

---

## 5. Política de Testes (TDD / Testes Antes)
* **Regra de Ouro**: **Nenhuma feature ou Caso de Uso deve ser implementada sem testes de unidade correspondentes.**
* **TDD (Test-Driven Development)**: Preferencialmente, escreva a assinatura do caso de uso e os testes para ela (testando sucesso e falhas esperadas) antes de desenvolver a lógica.
* **Isolamento**:
  * Bancos de dados devem ser mockados ou usar instâncias em memória (`sqlite` ou banco de testes temporário).
  * Comunicações externas e hardwares devem sempre utilizar implementações fictícias (`Mocks` / `Fakes`).
* **Execução**:
  ```bash
  docker compose exec app pytest
  ```

---

## 6. Fluxo de Git e Commits
* Commits devem ser claros e seguir o padrão de **Conventional Commits**:
  * `feat: ...` para novos recursos.
  * `fix: ...` para correção de bugs.
  * `test: ...` para escrita de testes.
  * `docs: ...` para documentações.
  * `refactor: ...` para melhorias no código sem alteração de comportamento.
