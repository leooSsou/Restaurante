from typing import Optional
from sqlalchemy.orm import Session
from src.domain.entities.item_comanda import ItemComanda
from src.domain.repositories.item_comanda_repository import ItemComandaRepositoryInterface
from src.infrastructure.database.mysql_models import ItemComandaModel

class MySQLItemComandaRepository(ItemComandaRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def _mapear_para_dominio(self, model: ItemComandaModel) -> ItemComanda:
        return ItemComanda(
            id=model.id,
            comanda_id=model.comanda_id,
            produto_id=model.produto_id,
            quantidade=float(model.quantidade),
            preco_unitario=float(model.preco_unitario),
            preco_total=float(model.preco_total),
            criado_em=model.criado_em
        )

    def salvar(self, item: ItemComanda) -> ItemComanda:
        model = self.session.query(ItemComandaModel).filter_by(id=item.id).first()
        
        if not model:
            # Criação
            model = ItemComandaModel(
                id=item.id,
                comanda_id=item.comanda_id,
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario,
                preco_total=item.preco_total,
                criado_em=item.criado_em
            )
            self.session.add(model)
        else:
            # Atualização
            model.quantidade = item.quantidade
            model.preco_unitario = item.preco_unitario
            model.preco_total = item.preco_total
            
        self.session.commit()
        self.session.refresh(model)
        
        return self._mapear_para_dominio(model)

    def buscar_por_id(self, item_id: str) -> Optional[ItemComanda]:
        model = self.session.query(ItemComandaModel).filter_by(id=item_id).first()
        return self._mapear_para_dominio(model) if model else None
