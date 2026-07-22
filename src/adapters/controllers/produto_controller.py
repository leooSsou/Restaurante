from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.infrastructure.database.connection import obter_sessao_mysql
from src.adapters.repositories.mysql_produto_repository import MySQLProdutoRepository
from src.use_cases.cadastrar_produto import CadastrarProdutoUseCase, CadastrarProdutoInput
from src.use_cases.listar_produtos import ListarProdutosUseCase

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def cadastrar_produto(dados: CadastrarProdutoInput, db: Session = Depends(obter_sessao_mysql)):
    """Rota para cadastrar um novo produto no restaurante."""
    repo = MySQLProdutoRepository(db)
    use_case = CadastrarProdutoUseCase(repo)
    try:
        produto_salvo = use_case.executar(dados)
        return {
            "mensagem": "Produto cadastrado com sucesso!",
            "produto": {
                "id": produto_salvo.id,
                "nome": produto_salvo.nome,
                "tipo": produto_salvo.tipo,
                "codigo_barras": produto_salvo.codigo_barras,
                "preco_por_kg": produto_salvo.preco_por_kg,
                "preco_unitario": produto_salvo.preco_unitario,
                "ncm": produto_salvo.ncm,
                "cest": produto_salvo.cest,
                "cfop": produto_salvo.cfop,
                "icms_csosn": produto_salvo.icms_csosn,
                "pis_cst": produto_salvo.pis_cst,
                "cofins_cst": produto_salvo.cofins_cst
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=None)
def listar_produtos(db: Session = Depends(obter_sessao_mysql)):
    """Rota para listar todos os produtos cadastrados."""
    repo = MySQLProdutoRepository(db)
    use_case = ListarProdutosUseCase(repo)
    produtos = use_case.executar()
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "tipo": p.tipo,
            "codigo_barras": p.codigo_barras,
            "preco_por_kg": p.preco_por_kg,
            "preco_unitario": p.preco_unitario,
            "ncm": p.ncm,
            "cest": p.cest,
            "cfop": p.cfop,
            "icms_csosn": p.icms_csosn,
            "pis_cst": p.pis_cst,
            "cofins_cst": p.cofins_cst
        }
        for p in produtos
    ]
