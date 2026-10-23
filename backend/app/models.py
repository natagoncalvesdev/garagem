import enum

from sqlalchemy import (
    Column, BigInteger, String, Boolean, DateTime,
    ForeignKey, Enum, UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class tipo_vaga(enum.Enum):
    CARRO = 'carro'
    MOTO = 'moto'
    VAN = 'van'


class pessoa(Base):
    __tablename__ = 'pessoa'
    id = Column(BigInteger, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    telefone = Column(String(100), nullable=False)
    cpf = Column(String(100), nullable=False, unique=True)

    usuario = relationship('usuario', back_populates='pessoa', uselist=False)
    veiculos = relationship('pessoa_veiculo', back_populates='pessoa')


class usuario(Base):
    __tablename__ = 'usuario'
    id = Column(BigInteger, primary_key=True)
    email = Column(String(100), nullable=False, unique=True)
    senha = Column(String(100), nullable=False)  # guardar o HASH, nunca a senha pura
    pessoa_id = Column(BigInteger, ForeignKey('pessoa.id'), nullable=False)

    pessoa = relationship('pessoa', back_populates='usuario')
    estacionamentos = relationship('usuario_estacionamento', back_populates='usuario')
    reservas = relationship('reserva', back_populates='usuario')


class estacionamento(Base):
    __tablename__ = 'estacionamento'
    id = Column(BigInteger, primary_key=True)
    nome = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)

    usuarios = relationship('usuario_estacionamento', back_populates='estacionamento')
    vagas = relationship('vaga', back_populates='estacionamento')


class usuario_estacionamento(Base):
    __tablename__ = 'usuario_estacionamento'
    id = Column(BigInteger, primary_key=True)
    usuario_id = Column(BigInteger, ForeignKey('usuario.id'), nullable=False)
    estacionamento_id = Column(BigInteger, ForeignKey('estacionamento.id'), nullable=False)
    data_inicio = Column(DateTime, nullable=False)

    usuario = relationship('usuario', back_populates='estacionamentos')
    estacionamento = relationship('estacionamento', back_populates='usuarios')

    __table_args__ = (
        UniqueConstraint('usuario_id', 'estacionamento_id', name='uq_usuario_estacionamento'),
    )


class veiculo(Base):
    __tablename__ = 'veiculo'
    id = Column(BigInteger, primary_key=True)
    modelo = Column(String(100), nullable=False)
    placa = Column(String(100), nullable=False, unique=True)

    pessoas = relationship('pessoa_veiculo', back_populates='veiculo')


class pessoa_veiculo(Base):
    __tablename__ = 'pessoa_veiculo'
    id = Column(BigInteger, primary_key=True)
    pessoa_id = Column(BigInteger, ForeignKey('pessoa.id'), nullable=False)
    veiculo_id = Column(BigInteger, ForeignKey('veiculo.id'), nullable=False)

    pessoa = relationship('pessoa', back_populates='veiculos')
    veiculo = relationship('veiculo', back_populates='pessoas')

    __table_args__ = (
        UniqueConstraint('pessoa_id', 'veiculo_id', name='uq_pessoa_veiculo'),
    )


class vaga(Base):
    __tablename__ = 'vaga'
    id = Column(BigInteger, primary_key=True)
    estacionamento_id = Column(BigInteger, ForeignKey('estacionamento.id'), nullable=False)
    numero = Column(String(100), nullable=False)
    x = Column(BigInteger, nullable=False)
    y = Column(BigInteger, nullable=False)
    tipo = Column(Enum(tipo_vaga), nullable=False)
    ativa = Column(Boolean, nullable=False, default=True)

    estacionamento = relationship('estacionamento', back_populates='vagas')
    reservas = relationship('reserva', back_populates='vaga')

    __table_args__ = (
        UniqueConstraint('estacionamento_id', 'x', 'y', name='uq_vaga_posicao'),
        UniqueConstraint('estacionamento_id', 'numero', name='uq_vaga_numero'),
    )


class reserva(Base):
    __tablename__ = 'reserva'
    id = Column(BigInteger, primary_key=True)
    vaga_id = Column(BigInteger, ForeignKey('vaga.id'), nullable=False)
    usuario_id = Column(BigInteger, ForeignKey('usuario.id'), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)

    vaga = relationship('vaga', back_populates='reservas')
    usuario = relationship('usuario', back_populates='reservas')