from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.infrastructure.database.connection import obter_sessao_mysql
from src.adapters.repositories.mysql_comanda_repository import MySQLComandaRepository
from src.adapters.repositories.mysql_produto_repository import MySQLProdutoRepository
from src.adapters.repositories.mysql_item_comanda_repository import MySQLItemComandaRepository

from src.use_cases.abrir_comanda import AbrirComandaUseCase, AbrirComandaInput
from src.use_cases.lancar_item_comanda import LancarItemComandaUseCase, LancarItemComandaInput
from src.use_cases.fechar_comanda import FecharComandaUseCase, FecharComandaInput

router = APIRouter(prefix="/comandas", tags=["Comandas"])

class RegistrarItemRequest(BaseModel):
    produto_id: int = Field(..., description="ID único do produto")
    quantidade: float = Field(..., description="Quantidade (peso em kg ou unidades)")

@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def abrir_comanda(dados: AbrirComandaInput, db: Session = Depends(obter_sessao_mysql)):
    """Abre uma nova comanda para um cartão físico."""
    repo = MySQLComandaRepository(db)
    use_case = AbrirComandaUseCase(repo)
    try:
        comanda = use_case.executar(dados)
        return {
            "mensagem": "Comanda aberta com sucesso!",
            "comanda": {
                "id": comanda.id,
                "numero_cartao": comanda.numero_cartao,
                "esta_aberta": comanda.esta_aberta,
                "criado_em": comanda.criado_em.isoformat() if comanda.criado_em else None,
                "fechado_em": comanda.fechado_em.isoformat() if comanda.fechado_em else None,
                "total_itens": len(comanda.itens),
                "total_pagamentos": len(comanda.pagamentos)
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/ativas/{numero_cartao}", response_model=None)
def obter_comanda_ativa(numero_cartao: str, db: Session = Depends(obter_sessao_mysql)):
    """Busca a comanda aberta ativa para um número de cartão."""
    repo = MySQLComandaRepository(db)
    comanda = repo.buscar_ativa_por_cartao(numero_cartao)
    
    if not comanda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi encontrada nenhuma comanda ativa para o cartão '{numero_cartao}'"
        )
        
    return {
        "id": comanda.id,
        "numero_cartao": comanda.numero_cartao,
        "esta_aberta": comanda.esta_aberta,
        "criado_em": comanda.criado_em.isoformat() if comanda.criado_em else None,
        "fechado_em": comanda.fechado_em.isoformat() if comanda.fechado_em else None,
        "valor_total": comanda.obter_valor_total(),
        "total_pago": comanda.obter_total_pago(),
        "saldo_devedor": comanda.obter_saldo_devedor()
    }

@router.post("/{comanda_id}/itens", response_model=None, status_code=status.HTTP_201_CREATED)
def lancar_item_comanda(comanda_id: str, dados: RegistrarItemRequest, db: Session = Depends(obter_sessao_mysql)):
    """Lança um item de consumo (peso ou unitário) na comanda ativa."""
    comanda_repo = MySQLComandaRepository(db)
    produto_repo = MySQLProdutoRepository(db)
    item_repo = MySQLItemComandaRepository(db)
    
    use_case = LancarItemComandaUseCase(comanda_repo, produto_repo, item_repo)
    try:
        input_dto = LancarItemComandaInput(
            comanda_id=comanda_id,
            produto_id=dados.produto_id,
            quantidade=dados.quantidade
        )
        item_lancado = use_case.executar(input_dto)
        return {
            "mensagem": "Item registrado com sucesso na comanda!",
            "item": {
                "id": item_lancado.id,
                "comanda_id": item_lancado.comanda_id,
                "produto_id": item_lancado.produto_id,
                "quantidade": item_lancado.quantidade,
                "preco_unitario": item_lancado.preco_unitario,
                "preco_total": item_lancado.preco_total,
                "criado_em": item_lancado.criado_em.isoformat() if item_lancado.criado_em else None
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{comanda_id}/fechar", response_model=None)
def fechar_comanda(comanda_id: str, db: Session = Depends(obter_sessao_mysql)):
    """Solicita o fechamento da comanda. O fechamento só é permitido se o saldo devedor for R$ 0,00."""
    comanda_repo = MySQLComandaRepository(db)
    use_case = FecharComandaUseCase(comanda_repo)
    try:
        input_dto = FecharComandaInput(comanda_id=comanda_id)
        comanda = use_case.executar(input_dto)
        return {
            "mensagem": "Comanda fechada com sucesso!",
            "comanda": {
                "id": comanda.id,
                "numero_cartao": comanda.numero_cartao,
                "esta_aberta": comanda.esta_aberta,
                "criado_em": comanda.criado_em.isoformat() if comanda.criado_em else None,
                "fechado_em": comanda.fechado_em.isoformat() if comanda.fechado_em else None
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
