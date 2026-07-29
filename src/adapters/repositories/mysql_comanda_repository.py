from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.entities.comanda import Comanda
from src.domain.entities.item_comanda import ItemComanda
from src.domain.entities.pagamento import Pagamento
from src.domain.repositories.comanda_repository import ComandaRepositoryInterface
from src.infrastructure.database.mysql_models import ComandaModel, ItemComandaModel, PagamentoModel

class MySQLComandaRepository(ComandaRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def _mapear_para_dominio(self, model: ComandaModel) -> Comanda:
        # Mapear itens da comanda do modelo para o domínio
        itens_dominio = [
            ItemComanda(
                id=i.id,
                comanda_id=i.comanda_id,
                produto_id=i.produto_id,
                quantidade=float(i.quantidade),
                preco_unitario=float(i.preco_unitario),
                preco_total=float(i.preco_total),
                criado_em=i.criado_em
            )
            for i in model.itens
        ]

        # Mapear pagamentos do modelo para o domínio
        pagamentos_dominio = [
            Pagamento(
                id=p.id,
                comanda_id=p.comanda_id,
                valor=float(p.valor),
                metodo_pagamento=p.metodo_pagamento,
                criado_em=p.criado_em
            )
            for p in model.pagamentos
        ]

        return Comanda(
            id=model.id,
            numero_cartao=model.numero_cartao,
            esta_aberta=model.esta_aberta,
            criado_em=model.criado_em,
            fechado_em=model.fechado_em,
            itens=itens_dominio,
            pagamentos=pagamentos_dominio
        )

    def salvar(self, comanda: Comanda) -> Comanda:
        model = self.session.query(ComandaModel).filter_by(id=comanda.id).first()
        
        if not model:
            # Criação
            model = ComandaModel(
                id=comanda.id,
                numero_cartao=comanda.numero_cartao,
                esta_aberta=comanda.esta_aberta,
                criado_em=comanda.criado_em,
                fechado_em=comanda.fechado_em
            )
            self.session.add(model)
        else:
            # Atualização dos atributos principais
            model.numero_cartao = comanda.numero_cartao
            model.esta_aberta = comanda.esta_aberta
            model.fechado_em = comanda.fechado_em
            
            # Sincronização básica de coleções se necessário
            # (Geralmente itens/pagamentos são adicionados via seus próprios repositórios
            # ou salvos em cascata, mas mantemos o mapeamento alinhado).

        self.session.commit()
        self.session.refresh(model)
        
        return self._mapear_para_dominio(model)

    def buscar_por_id(self, comanda_id: str) -> Optional[Comanda]:
        model = self.session.query(ComandaModel).filter_by(id=comanda_id).first()
        return self._mapear_para_dominio(model) if model else None

    def buscar_ativa_por_cartao(self, numero_cartao: str) -> Optional[Comanda]:
        model = (
            self.session.query(ComandaModel)
            .filter_by(numero_cartao=numero_cartao, esta_aberta=True)
            .first()
        )
        return self._mapear_para_dominio(model) if model else None
