from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

@dataclass
class ItemComanda:
    comanda_id: str
    produto_id: int
    quantidade: float  # Representa peso em kg ou quantidade unitária
    preco_unitario: float
    preco_total: float = 0.0
    id: Optional[str] = None
    criado_em: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise ValueError("A quantidade do item deve ser maior que zero")
        if self.preco_unitario < 0:
            raise ValueError("O preço unitário não pode ser negativo")
            
        # Calcula o preço total de forma precisa
        qtd_dec = Decimal(str(self.quantidade))
        preco_dec = Decimal(str(self.preco_unitario))
        total_dec = qtd_dec * preco_dec
        self.preco_total = float(total_dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
