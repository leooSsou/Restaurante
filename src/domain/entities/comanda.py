from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from src.domain.entities.item_comanda import ItemComanda
from src.domain.entities.pagamento import Pagamento

@dataclass
class Comanda:
    id: str
    numero_cartao: str
    esta_aberta: bool = True
    criado_em: Optional[datetime] = None
    fechado_em: Optional[datetime] = None
    itens: List[ItemComanda] = field(default_factory=list)
    pagamentos: List[Pagamento] = field(default_factory=list)

    def adicionar_item(self, item: ItemComanda) -> None:
        if not self.esta_aberta:
            raise ValueError("Não é possível adicionar itens a uma comanda fechada")
        self.itens.append(item)

    def registrar_pagamento(self, pagamento: Pagamento) -> None:
        if not self.esta_aberta:
            raise ValueError("Não é possível registrar pagamentos em uma comanda fechada")
        self.pagamentos.append(pagamento)

    def obter_valor_total(self) -> float:
        """Calcula o valor total somando todos os itens da comanda."""
        total = sum(Decimal(str(item.preco_total)) for item in self.itens)
        return float(total)

    def obter_total_pago(self) -> float:
        """Calcula o valor total pago somando todos os pagamentos da comanda."""
        total = sum(Decimal(str(p.valor)) for p in self.pagamentos)
        return float(total)

    def obter_saldo_devedor(self) -> float:
        """Calcula o valor que resta pagar (Total - Pago)."""
        saldo = Decimal(str(self.obter_valor_total())) - Decimal(str(self.obter_total_pago()))
        return float(saldo)

    def fechar_comanda(self) -> None:
        """Fecha a comanda se o saldo devedor for igual a zero."""
        if not self.esta_aberta:
            return
            
        if self.obter_saldo_devedor() > 0:
            raise ValueError(f"Não é possível fechar a comanda. Saldo devedor restante: R$ {self.obter_saldo_devedor():.2f}")
            
        self.esta_aberta = False
        self.fechado_em = datetime.now()
