from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/estacionamentos", tags=["estacionamentos"])


def buscar_ou_404(db: Session, estacionamento_id: int) -> models.estacionamento:
    obj = db.get(models.estacionamento, estacionamento_id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estacionamento não encontrado")
    return obj


@router.post("", response_model=schemas.EstacionamentoOut, status_code=status.HTTP_201_CREATED)
def criar(dados: schemas.EstacionamentoCreate, db: Session = Depends(get_db)):
    novo = models.estacionamento(**dados.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo
 
 
@router.get("", response_model=list[schemas.EstacionamentoOut])
def listar(db: Session = Depends(get_db)):
    consulta = select(models.estacionamento).order_by(models.estacionamento.id)
    return db.scalars(consulta).all()
 
 
@router.get("/{estacionamento_id}", response_model=schemas.EstacionamentoOut)
def obter(estacionamento_id: int, db: Session = Depends(get_db)):
    return buscar_ou_404(db, estacionamento_id)
 
 
@router.patch("/{estacionamento_id}", response_model=schemas.EstacionamentoOut)
def atualizar(
    estacionamento_id: int,
    dados: schemas.EstacionamentoUpdate,
    db: Session = Depends(get_db),
):
    obj = buscar_ou_404(db, estacionamento_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(obj, campo, valor)
    db.commit()
    db.refresh(obj)
    return obj
 
 
@router.delete("/{estacionamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar(estacionamento_id: int, db: Session = Depends(get_db)):
    obj = buscar_ou_404(db, estacionamento_id)
    try:
        db.delete(obj)
        db.commit()
    except IntegrityError:
        # Ainda existem vagas ou vínculos apontando para este estacionamento.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível apagar: há vagas ou usuários vinculados",
        )
 