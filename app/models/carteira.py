from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class CarteiraBase(BaseModel):
    nome: str = Field(..., description="Nome da carteira")
    descricao: Optional[str] = Field(None, description="Descrição da carteira")

class CarteiraCriar(CarteiraBase):
    pass

class Carteira(CarteiraBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True 