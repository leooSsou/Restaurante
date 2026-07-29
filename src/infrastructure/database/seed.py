from src.infrastructure.database.connection import SessionLocal, engine, Base
from src.infrastructure.database.mysql_models import ProdutoModel

def seed():
    # Garante que as tabelas estão criadas no MySQL
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # Verifica se já existem produtos cadastrados
        if session.query(ProdutoModel).count() > 0:
            print("O banco de dados já possui produtos cadastrados. Pulando seed.")
            return

        produtos = [
            ProdutoModel(
                nome="Buffet Livre / Kg",
                tipo="peso",
                preco_por_kg=59.90,
                codigo_barras="7890000000018",
                ncm="21069090",
                cfop="5101",
                icms_csosn="102",
                pis_cst="01",
                cofins_cst="01"
            ),
            ProdutoModel(
                nome="Sobremesa Fina / Kg",
                tipo="peso",
                preco_por_kg=79.90,
                codigo_barras="7890000000025",
                ncm="21069090",
                cfop="5101",
                icms_csosn="102",
                pis_cst="01",
                cofins_cst="01"
            ),
            ProdutoModel(
                nome="Refrigerante Lata 350ml",
                tipo="unitario",
                preco_unitario=6.00,
                codigo_barras="7894900010015",
                ncm="22021000",
                cfop="5102",
                icms_csosn="500",
                pis_cst="04",
                cofins_cst="04"
            ),
            ProdutoModel(
                nome="Água Mineral 500ml",
                tipo="unitario",
                preco_unitario=4.00,
                codigo_barras="7898022271015",
                ncm="22011000",
                cfop="5102",
                icms_csosn="500",
                pis_cst="04",
                cofins_cst="04"
            ),
            ProdutoModel(
                nome="Cerveja Heineken LN 330ml",
                tipo="unitario",
                preco_unitario=10.00,
                codigo_barras="7896045504107",
                ncm="22030000",
                cfop="5102",
                icms_csosn="500",
                pis_cst="04",
                cofins_cst="04"
            ),
            ProdutoModel(
                nome="Suco de Laranja Natural Caneca",
                tipo="unitario",
                preco_unitario=9.00,
                codigo_barras=None,
                ncm="22029900",
                cfop="5101",
                icms_csosn="102",
                pis_cst="01",
                cofins_cst="01"
            ),
        ]

        session.bulk_save_objects(produtos)
        session.commit()
        print("Banco de dados populado com 6 produtos de exemplo com sucesso!")
        
    except Exception as e:
        session.rollback()
        print(f"Erro ao popular banco de dados: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed()
