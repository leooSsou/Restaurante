from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.entities.produto import Produto
from src.domain.repositories.produto_repository import ProdutoRepositoryInterface
from src.infrastructure.database.mysql_models import ProdutoModel

class MySQLProdutoRepository(ProdutoRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def _mapear_para_dominio(self, model: ProdutoModel) -> Produto:
        return Produto(
            id=model.id,
            nome=model.nome,
            tipo=model.tipo,
            codigo_barras=model.codigo_barras,
            preco_por_kg=float(model.preco_por_kg) if model.preco_por_kg is not None else None,
            preco_unitario=float(model.preco_unitario) if model.preco_unitario is not None else None,
            ncm=model.ncm,
            cest=model.cest,
            cfop=model.cfop,
            icms_csosn=model.icms_csosn,
            pis_cst=model.pis_cst,
            cofins_cst=model.cofins_cst
        )

    def salvar(self, produto: Produto) -> Produto:
        if produto.id:
            # Atualização
            model = self.session.query(ProdutoModel).filter_by(id=produto.id).first()
            if not model:
                raise ValueError(f"Produto com ID {produto.id} não encontrado para atualização")
            model.nome = produto.nome
            model.tipo = produto.tipo
            model.codigo_barras = produto.codigo_barras
            model.preco_por_kg = produto.preco_por_kg
            model.preco_unitario = produto.preco_unitario
            model.ncm = produto.ncm
            model.cest = produto.cest
            model.cfop = produto.cfop
            model.icms_csosn = produto.icms_csosn
            model.pis_cst = produto.pis_cst
            model.cofins_cst = produto.cofins_cst
        else:
            # Criação
            model = ProdutoModel(
                nome=produto.nome,
                tipo=produto.tipo,
                codigo_barras=produto.codigo_barras,
                preco_por_kg=produto.preco_por_kg,
                preco_unitario=produto.preco_unitario,
                ncm=produto.ncm,
                cest=produto.cest,
                cfop=produto.cfop,
                icms_csosn=produto.icms_csosn,
                pis_cst=produto.pis_cst,
                cofins_cst=produto.cofins_cst
            )
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        
        # Sincroniza o ID gerado pelo banco com a entidade de domínio
        produto.id = model.id
        return produto

    def buscar_por_id(self, produto_id: int) -> Optional[Produto]:
        model = self.session.query(ProdutoModel).filter_by(id=produto_id).first()
        return self._mapear_para_dominio(model) if model else None

    def buscar_por_codigo_barras(self, codigo_barras: str) -> Optional[Produto]:
        model = self.session.query(ProdutoModel).filter_by(codigo_barras=codigo_barras).first()
        return self._mapear_para_dominio(model) if model else None

    def listar_todos(self) -> List[Produto]:
        models = self.session.query(ProdutoModel).all()
        return [self._mapear_para_dominio(m) for m in models]
