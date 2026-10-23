"""A main é a recepção de um prédio, e cada router é um departamento. 
A recepção não resolve nada sozinha, só sabe quais departamentos existem e para onde encaminhar cada pedido. 
Por isso, quando você criar o CRUD de vagas, pessoas e veículos, o main.py só ganha mais duas linhas por recurso:"""


from fastapi import FastAPI

from app.routers import estacionamentos

app = FastAPI(title="Garagem")

app.include_router(estacionamentos.router)