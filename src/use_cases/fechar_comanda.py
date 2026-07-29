from pydantic import BaseModel, Field
from src.domain.entities.comanda import Comanda
from src.domain.repositories.comanda_repository import ComandaRepositoryInterface

class FecharComandaInput(BaseModel):
    comanda_id: str = Field(..., description="ID único da comanda a ser fechada")

class FecharComandaUseCase:
    def __init__(self, comanda_repo: ComandaRepositoryInterface):
        self.comanda_repo = comanda_repo

    def executar(self, dados: FecharComandaInput) -> Comanda:
        # 1. Buscar comanda
        comanda = self.comanda_repo.buscar_por_id(dados.comanda_id)
        if not comanda:
            raise ValueError(f"Comanda com ID '{dados.comanda_id}' não encontrada")

        # 2. Executar a regra de negócio do fechamento (lança ValueError se houver saldo devedor)
        comanda.fechar_comanda()

        # 3. Salvar no repositório
        return self.comanda_repo.salvar(comanda)
