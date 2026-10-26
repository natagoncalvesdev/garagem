from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from sqlalchemy import intersect

from backend.app.models import tipo_vaga


# ------------------------Estacionamentos------------------------

class EstacionamentoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cidade: str = Field(min_length=1, max_length=100)
    estado: str = Field(min_length=1, max_length=100)


class EstacionamentoCreate(EstacionamentoBase):
    """Dados que  cliente envia para criar um estacionamento"""


class EstacionamentoUpdate(BaseModel):
    """Todos os campos opcionais: o cliente manda só o que quer alterar"""
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    cidade: str | None = Field(default=None, min_length=1, max_length=100)
    estado: str | None = Field(default=None, min_length=1, max_length=100)


class EstacionamentoOut(EstacionamentoBase):
    """Dados que a API devolve(inclui o id gerado pelo banco)"""
    id: int

    model_config = ConfigDict(from_attributes=True)


# ------------------------Vagas------------------------

class PosicaoVaga(BaseModel):
    """Um quadrado marcado no mapa. x = coluna, y = linha (começam em 0)"""
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    tipo : tipo_vaga = tipo_vaga.CARRO


class VagaLote(BaseModel):
    """Lista de quadrados marcados pelo usuario; a API define o número"""
    posicoes: list[PosicaoVaga] = Field(min_length=1)


class VagaUpdate(BaseModel):
    tipo: tipo_vaga | None = None
    ativa: bool | None = None


class VagaOut(BaseModel):
    id: int
    estacionamento_id: int
    numero: int
    x: int
    y: int
    tipo: tipo_vaga
    ativa: bool

    model_config = ConfigDict(from_attributes=True)