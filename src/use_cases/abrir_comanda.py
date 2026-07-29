import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from src.domain.entities.comanda import Comanda
from src.domain.repositories.comanda_repository import ComandaRepositoryInterface

class AbrirComandaInput(BaseModel):
    numero_cartao: str = Field(..., min_length=1, max_length=50, description="Número físico da comanda/cartão")

class AbrirComandaUseCase:
    def __init__(self, comanda_repo: ComandaRepositoryInterface):
        self.comanda_repo = comanda_repo

    def executar(self, dados: AbrirComandaInput) -> Comanda:
        numero_cartao = dados.numero_cartao.strip()
        if not numero_cartao:
            raise ValueError("O número do cartão não pode ser vazio")

        # 1. Verificar se já existe uma comanda ativa para este cartão
        comanda_ativa = self.comanda_repo.buscar_ativa_por_cartao(numero_cartao)
        if comanda_ativa:
            raise ValueError(f"Não é possível abrir: o cartão '{numero_cartao}' já possui uma comanda ativa")

        # 2. Instanciar a entidade de domínio Comanda
        nova_comanda = Comanda(
            id=str(uuid.uuid4()),
            numero_cartao=numero_cartao,
            esta_aberta=True,
            criado_em=datetime.now()
        )

        # 3. Salvar na persistência
        return self.comanda_repo.salvar(nova_comanda)
