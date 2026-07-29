from sqlalchemy.orm import Session
from src.domain.entities.pagamento import Pagamento
from src.domain.repositories.pagamento_repository import PagamentoRepositoryInterface
from src.infrastructure.database.mysql_models import PagamentoModel

class MySQLPagamentoRepository(PagamentoRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def _mapear_para_dominio(self, model: PagamentoModel) -> Pagamento:
        return Pagamento(
            id=model.id,
            comanda_id=model.comanda_id,
            valor=float(model.valor),
            metodo_pagamento=model.metodo_pagamento,
            criado_em=model.criado_em
        )

    def salvar(self, pagamento: Pagamento) -> Pagamento:
        model = self.session.query(PagamentoModel).filter_by(id=pagamento.id).first()
        
        if not model:
            # Criação
            model = PagamentoModel(
                id=pagamento.id,
                comanda_id=pagamento.comanda_id,
                valor=pagamento.valor,
                metodo_pagamento=pagamento.metodo_pagamento,
                criado_em=pagamento.criado_em
            )
            self.session.add(model)
        else:
            # Atualização
            model.valor = pagamento.valor
            model.metodo_pagamento = pagamento.metodo_pagamento

        self.session.commit()
        self.session.refresh(model)
        
        return self._mapear_para_dominio(model)
