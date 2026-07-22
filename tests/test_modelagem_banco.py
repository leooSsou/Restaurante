import uuid
from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.connection import Base
from src.infrastructure.database.mysql_models import (
    ProdutoModel,
    ComandaModel,
    ItemComandaModel,
    PagamentoModel
)

# Configuração de um banco SQLite em memória para testes de persistência
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="db_session")
def fixture_db_session():
    # Usamos o SQLite em memória para simular o banco relacionando chaves estrangeiras
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_persistencias_e_relacionamentos(db_session):
    # 1. Inserir Produtos com dados fiscais
    bebida = ProdutoModel(
        nome="Coca-Cola 350ml",
        tipo="unitario",
        codigo_barras="7891234567890",
        preco_unitario=Decimal("6.00"),
        ncm="22021000",
        cfop="5102",
        icms_csosn="500",
        pis_cst="04",
        cofins_cst="04"
    )
    
    comida_kg = ProdutoModel(
        nome="Buffet Livre/Kg",
        tipo="peso",
        preco_por_kg=Decimal("69.90"),
        ncm="21069090",
        cfop="5101",
        icms_csosn="102",
        pis_cst="01",
        cofins_cst="01"
    )
    
    db_session.add_all([bebida, comida_kg])
    db_session.commit()
    
    assert bebida.id is not None
    assert comida_kg.id is not None

    # 2. Criar uma Comanda
    comanda_id = str(uuid.uuid4())
    comanda = ComandaModel(
        id=comanda_id,
        numero_cartao="00123",
        esta_aberta=True
    )
    db_session.add(comanda)
    db_session.commit()

    # 3. Registrar Itens na Comanda (com cálculo de preços)
    item_peso = ItemComandaModel(
        id=str(uuid.uuid4()),
        comanda_id=comanda_id,
        produto_id=comida_kg.id,
        quantidade=Decimal("0.450"),  # 450 gramas
        preco_unitario=comida_kg.preco_por_kg,
        preco_total=Decimal("0.450") * comida_kg.preco_por_kg  # 31.455 -> 31.46
    )
    
    item_unitario = ItemComandaModel(
        id=str(uuid.uuid4()),
        comanda_id=comanda_id,
        produto_id=bebida.id,
        quantidade=Decimal("2.000"),  # 2 Coca-Colas
        preco_unitario=bebida.preco_unitario,
        preco_total=Decimal("2.000") * bebida.preco_unitario  # 12.00
    )
    
    db_session.add_all([item_peso, item_unitario])
    db_session.commit()

    # 4. Registrar Pagamento
    pagamento = PagamentoModel(
        id=str(uuid.uuid4()),
        comanda_id=comanda_id,
        valor=Decimal("43.46"),  # R$ 31.46 + R$ 12.00
        metodo_pagamento="pix"
    )
    db_session.add(pagamento)
    db_session.commit()

    # 5. Validar Relacionamentos (Carregamento da Comanda)
    comanda_carregada = db_session.query(ComandaModel).filter_by(id=comanda_id).first()
    assert comanda_carregada is not None
    assert len(comanda_carregada.itens) == 2
    assert len(comanda_carregada.pagamentos) == 1
    assert comanda_carregada.pagamentos[0].metodo_pagamento == "pix"
    assert comanda_carregada.pagamentos[0].valor == Decimal("43.46")

    # 6. Validar Deleção em Cascata (Cascade Delete)
    db_session.delete(comanda_carregada)
    db_session.commit()

    # Itens e pagamentos correspondentes devem ter sido removidos automaticamente do banco
    itens_restantes = db_session.query(ItemComandaModel).filter_by(comanda_id=comanda_id).all()
    pagamentos_restantes = db_session.query(PagamentoModel).filter_by(comanda_id=comanda_id).all()
    
    assert len(itens_restantes) == 0
    assert len(pagamentos_restantes) == 0
