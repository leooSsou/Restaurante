import pytest
from typing import Optional, List
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.entities.comanda import Comanda
from src.domain.repositories.comanda_repository import ComandaRepositoryInterface
from src.use_cases.abrir_comanda import AbrirComandaUseCase, AbrirComandaInput
from src.adapters.repositories.mysql_comanda_repository import MySQLComandaRepository
from src.infrastructure.database.connection import Base

# --- Fake Repository para Testes Unitários ---
class FakeComandaRepository(ComandaRepositoryInterface):
    def __init__(self):
        self.comandas = []

    def salvar(self, comanda: Comanda) -> Comanda:
        # Tenta atualizar se já existir
        for idx, c in enumerate(self.comandas):
            if c.id == comanda.id:
                self.comandas[idx] = comanda
                return comanda
        self.comandas.append(comanda)
        return comanda

    def buscar_por_id(self, comanda_id: str) -> Optional[Comanda]:
        for c in self.comandas:
            if c.id == comanda_id:
                return c
        return None

    def buscar_ativa_por_cartao(self, numero_cartao: str) -> Optional[Comanda]:
        for c in self.comandas:
            if c.numero_cartao == numero_cartao and c.esta_aberta:
                return c
        return None


# --- Testes Unitários do Caso de Uso ---
def test_abrir_comanda_sucesso():
    repo = FakeComandaRepository()
    use_case = AbrirComandaUseCase(repo)
    dados = AbrirComandaInput(numero_cartao="00100")
    
    # Act
    comanda = use_case.executar(dados)
    
    # Assert
    assert comanda.id is not None
    assert comanda.numero_cartao == "00100"
    assert comanda.esta_aberta is True
    assert comanda.criado_em is not None


def test_abrir_comanda_erro_duplicidade_ativa():
    repo = FakeComandaRepository()
    use_case = AbrirComandaUseCase(repo)
    dados = AbrirComandaInput(numero_cartao="00100")
    
    # Abrir primeira vez
    use_case.executar(dados)
    
    # Act & Assert - Tentar abrir novamente com o mesmo cartão ativo deve lançar erro
    with pytest.raises(ValueError, match="já possui uma comanda ativa"):
        use_case.executar(dados)


def test_abrir_comanda_sucesso_apos_fechamento():
    repo = FakeComandaRepository()
    use_case = AbrirComandaUseCase(repo)
    dados = AbrirComandaInput(numero_cartao="00100")
    
    # 1. Abrir a primeira
    comanda1 = use_case.executar(dados)
    
    # 2. Fechar a primeira
    comanda1.esta_aberta = False
    repo.salvar(comanda1)
    
    # 3. Act - Abrir a segunda com o mesmo cartão (agora livre)
    comanda2 = use_case.executar(dados)
    
    # Assert
    assert comanda1.id != comanda2.id
    assert comanda2.esta_aberta is True


# --- Testes de Integração da Persistência (SQLite) ---
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(name="db_session")
def fixture_db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_mysql_repositorio_comanda_integracao(db_session):
    repo = MySQLComandaRepository(db_session)
    
    c = Comanda(
        id="comanda-uuid-123",
        numero_cartao="00200",
        esta_aberta=True,
        criado_em=datetime.now()
    )
    
    # Act - Salvar
    repo.salvar(c)
    
    # Assert - Buscar ativa
    c_ativa = repo.buscar_ativa_por_cartao("00200")
    assert c_ativa is not None
    assert c_ativa.id == "comanda-uuid-123"
    assert c_ativa.esta_aberta is True
    
    # Act - Fechar e salvar
    c_ativa.esta_aberta = False
    c_ativa.fechado_em = datetime.now()
    repo.salvar(c_ativa)
    
    # Assert - Buscar ativa novamente (deve retornar None)
    c_ativa_depois = repo.buscar_ativa_por_cartao("00200")
    assert c_ativa_depois is None
    
    # Assert - Mas buscar por ID ainda deve encontrá-la no banco
    c_historico = repo.buscar_por_id("comanda-uuid-123")
    assert c_historico is not None
    assert c_historico.esta_aberta is False
