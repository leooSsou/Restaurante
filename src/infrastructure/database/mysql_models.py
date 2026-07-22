from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.infrastructure.database.connection import Base

class ProdutoModel(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    tipo = Column(Enum("peso", "unitario"), nullable=False)
    codigo_barras = Column(String(50), nullable=True)
    preco_por_kg = Column(Numeric(10, 2), nullable=True)
    preco_unitario = Column(Numeric(10, 2), nullable=True)
    
    # Dados Tributários / Fiscais
    ncm = Column(String(8), nullable=False)
    cest = Column(String(7), nullable=True)
    cfop = Column(String(4), nullable=False)
    icms_csosn = Column(String(4), nullable=False)
    pis_cst = Column(String(2), nullable=False)
    cofins_cst = Column(String(2), nullable=False)

    # Relacionamento de volta para itens registrados
    itens = relationship("ItemComandaModel", back_populates="produto")


class ComandaModel(Base):
    __tablename__ = "comandas"

    id = Column(String(36), primary_key=True)  # UUID
    numero_cartao = Column(String(50), nullable=False, unique=True, index=True)
    esta_aberta = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    fechado_em = Column(DateTime, nullable=True)

    # Relacionamentos
    itens = relationship(
        "ItemComandaModel", 
        back_populates="comanda", 
        cascade="all, delete-orphan"
    )
    pagamentos = relationship(
        "PagamentoModel", 
        back_populates="comanda", 
        cascade="all, delete-orphan"
    )


class ItemComandaModel(Base):
    __tablename__ = "itens_comanda"

    id = Column(String(36), primary_key=True)  # UUID
    comanda_id = Column(String(36), ForeignKey("comandas.id", ondelete="CASCADE"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Numeric(10, 3), nullable=False)  # 3 casas para suportar gramas precisas (ex: 0.750)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    preco_total = Column(Numeric(10, 2), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    comanda = relationship("ComandaModel", back_populates="itens")
    produto = relationship("ProdutoModel", back_populates="itens")


class PagamentoModel(Base):
    __tablename__ = "pagamentos"

    id = Column(String(36), primary_key=True)  # UUID
    comanda_id = Column(String(36), ForeignKey("comandas.id", ondelete="CASCADE"), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    metodo_pagamento = Column(Enum("dinheiro", "debito", "credito", "pix"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    comanda = relationship("ComandaModel", back_populates="pagamentos")
