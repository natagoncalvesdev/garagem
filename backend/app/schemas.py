from pydantic import BaseModel, ConfigDict, Field

class EstacinamentoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cidade: str = Field(min_length=1, max_length=100)
    estado: str = Field(min_length=1, max_length=100)


class EstacinamentoCreate(EstacinamentoBase):
    """Dados que  cliente envia para criar um estacionamento"""


class EstacionamentoUpdate(BaseModel):
    """Todos os campos opcionais: o cliente manda só o que quer alterar"""
    nome: Optional[str] = Field(min_length=1, max_length=100)
    cidade: Optional[str] = Field(min_length=1, max_length=100)
    estado: Optional[str] = Field(min_length=1, max_length=100)


class EstacionamentoOut(EstacionamentoBase):
    """Dados que a API devolve(inclui o id gerado pelo banco)"""
    id: int

    model_config = ConfigDict(from_attributes=True)