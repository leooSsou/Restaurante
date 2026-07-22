from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Pagamento:
    comanda_id: str
    valor: float
    metodo_pagamento: str  # 'dinheiro', 'debito', 'credito', 'pix'
    id: Optional[str] = None
    criado_em: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.valor <= 0:
            raise ValueError("O valor do pagamento deve ser maior que zero")
            
        metodos_validos = ('dinheiro', 'debito', 'credito', 'pix')
        if self.metodo_pagamento not in metodos_validos:
            raise ValueError(f"Método de pagamento inválido. Deve ser um de: {metodos_validos}")
