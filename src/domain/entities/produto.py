from dataclasses import dataclass
from typing import Optional

@dataclass
class Produto:
    nome: str
    tipo: str  # 'peso' ou 'unitario'
    ncm: str  # 8 dígitos
    cfop: str  # 4 dígitos
    icms_csosn: str  # Código de Situação Tributária do ICMS (ou CST)
    pis_cst: str  # CST do PIS
    cofins_cst: str  # CST do COFINS
    id: Optional[int] = None
    codigo_barras: Optional[str] = None
    preco_por_kg: Optional[float] = None
    preco_unitario: Optional[float] = None
    cest: Optional[str] = None

    def __post_init__(self) -> None:
        if self.tipo not in ('peso', 'unitario'):
            raise ValueError("O tipo do produto deve ser 'peso' ou 'unitario'")
        
        if self.tipo == 'peso' and self.preco_por_kg is None:
            raise ValueError("Produtos do tipo 'peso' devem possuir preco_por_kg definido")
            
        if self.tipo == 'unitario' and self.preco_unitario is None:
            raise ValueError("Produtos do tipo 'unitario' devem possuir preco_unitario definido")

        if len(self.ncm) != 8 or not self.ncm.isdigit():
            raise ValueError("O NCM deve possuir exatamente 8 dígitos numéricos")

        if len(self.cfop) != 4 or not self.cfop.isdigit():
            raise ValueError("O CFOP deve possuir exatamente 4 dígitos numéricos")
