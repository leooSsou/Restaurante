from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.infrastructure.database.connection import obter_sessao_mysql
from src.adapters.repositories.mysql_comanda_repository import MySQLComandaRepository
from src.use_cases.abrir_comanda import AbrirComandaUseCase, AbrirComandaInput

router = APIRouter(prefix="/comandas", tags=["Comandas"])

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
