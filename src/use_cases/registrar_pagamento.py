import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from src.domain.entities.pagamento import Pagamento
from src.domain.repositories.comanda_repository import ComandaRepositoryInterface
from src.domain.repositories.pagamento_repository import PagamentoRepositoryInterface

class RegistrarPagamentoInput(BaseModel):
    comanda_id: str = Field(..., description="ID único da comanda")
    valor: float = Field(..., description="Valor pago")
    metodo_pagamento: str = Field(..., description="Método de pagamento (dinheiro, debito, credito, pix)")

class RegistrarPagamentoUseCase:
    def __init__(
        self,
        comanda_repo: ComandaRepositoryInterface,
        pagamento_repo: PagamentoRepositoryInterface
    ):
        self.comanda_repo = comanda_repo
        self.pagamento_repo = pagamento_repo

    def executar(self, dados: RegistrarPagamentoInput) -> Pagamento:
        # 1. Buscar comanda
        comanda = self.comanda_repo.buscar_por_id(dados.comanda_id)
        if not comanda:
            raise ValueError(f"Comanda com ID '{dados.comanda_id}' não encontrada")
        if not comanda.esta_aberta:
            raise ValueError("Não é possível registrar pagamentos em uma comanda fechada")

        # 2. Instanciar entidade de domínio Pagamento (executa validação de valor > 0 e métodos válidos)
        pagamento = Pagamento(
            id=str(uuid.uuid4()),
            comanda_id=comanda.id,
            valor=dados.valor,
            metodo_pagamento=dados.metodo_pagamento,
            criado_em=datetime.now()
        )

        # 3. Salvar na persistência
        return self.pagamento_repo.salvar(pagamento)
