from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["vagas"])


def buscar_estacionamento_ou_404(db: Session, estacionamento_id: int) -> models.estacionamento:
    obj = db.get(models.estacionamento, estacionamento_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estacionamento não encontrado",
        )
    return obj


def buscar_vaga_ou_404(db: Session, vaga_id: int) -> models.vaga:
    obj = db.get(models.vaga, vaga_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaga não encontrada",
        )
    return obj


@router.get(
    "/estacionamentos/{estacionamento_id}/vagas",
    response_model=list[schemas.VagaOut],
)
def listar(
    estacionamento_id: int,
    incluir_inativas: bool = False,
    db: Session = Depends(get_db),
):
    buscar_estacionamento_ou_404(db, estacionamento_id)
    consulta = select(models.vaga).where(models.vaga.estacionamento_id == estacionamento_id)
    if not incluir_inativas:
        consulta = consulta.where(models.vaga.ativa.is_(True))
    consulta = consulta.order_by(models.vaga.y, models.vaga.x)
    return db.scalars(consulta).all()


@router.post(
    "/estacionamentos/{estacionamento_id}/vagas/lote",
    response_model=list[schemas.VagaOut],
    status_code=status.HTTP_201_CREATED,
)
def criar_em_lote(
    estacionamento_id: int,
    dados: schemas.VagaLote,
    db: Session = Depends(get_db),
):
    est = buscar_estacionamento_ou_404(db, estacionamento_id)
    posicoes = [(p.x, p.y) for p in dados.posicoes]

    # 1. Todas as posições precisam caber na grade do estacionamento.
    fora = [(x, y) for x, y in posicoes if x >= est.colunas or y >= est.linhas]
    if fora:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Posições (x, y) fora da grade de {est.colunas} colunas x {est.linhas} linhas: {fora}",
        )

    # 2. Não pode haver posição repetida dentro do próprio pedido.
    if len(set(posicoes)) != len(posicoes):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Há posições repetidas no pedido",
        )

    # 3. Nenhuma posição pode já ter vaga (ativa ou desativada).
    existentes = db.execute(
        select(models.vaga.x, models.vaga.y).where(
            models.vaga.estacionamento_id == estacionamento_id
        )
    ).all()
    ocupadas = {(x, y) for x, y in existentes}
    conflito = [p for p in posicoes if p in ocupadas]
    if conflito:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe vaga (ativa ou desativada) nas posições (x, y): {conflito}",
        )

    # 4. Numeração automática: continua do maior número já usado
    #    e segue a ordem de leitura do mapa (linha por linha, da esquerda p/ direita).
    numeros = db.scalars(
        select(models.vaga.numero).where(models.vaga.estacionamento_id == estacionamento_id)
    ).all()
    ultimo = max((int(n) for n in numeros if n.isdigit()), default=0)

    ordenadas = sorted(dados.posicoes, key=lambda p: (p.y, p.x))
    novas = [
        models.vaga(
            estacionamento_id=estacionamento_id,
            numero=str(ultimo + i),
            x=p.x,
            y=p.y,
            tipo=p.tipo,
        )
        for i, p in enumerate(ordenadas, start=1)
    ]

    # Tudo numa única transação: entram todas as vagas ou nenhuma.
    db.add_all(novas)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflito ao gravar as vagas; tente novamente",
        )
    for v in novas:
        db.refresh(v)
    return novas


@router.patch("/vagas/{vaga_id}", response_model=schemas.VagaOut)
def atualizar(
    vaga_id: int,
    dados: schemas.VagaUpdate,
    db: Session = Depends(get_db),
):
    obj = buscar_vaga_ou_404(db, vaga_id)
    for campo, valor in dados.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(obj, campo, valor)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/vagas/{vaga_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar(vaga_id: int, db: Session = Depends(get_db)):
    """Não apaga a linha: só marca ativa = False, para preservar o histórico."""
    obj = buscar_vaga_ou_404(db, vaga_id)
    obj.ativa = False
    db.commit()