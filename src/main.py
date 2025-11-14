# src/main.py
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from strawberry.fastapi import GraphQLRouter
import strawberry
from .resolvers import Query
from typing import Dict, Any

# --- Ponto-Chave da Arquitetura ---
async def get_context(request: Request) -> Dict[str, Any]:
    """
    Injeta a requisição FastAPI no contexto do Strawberry
    para que os resolvers possam acessar os headers.
    """
    return {
        "request": request
    }
# -----------------------------------

# Criar o Schema do Strawberry
schema = strawberry.Schema(query=Query)

# Criar o "roteador" do GraphQL, passando o 'context_getter'
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)

# Criar o app FastAPI
app = FastAPI(
    title="Multiembarcador GraphQL Facade",
    description="Fachada GraphQL para o WebService SOAP SGT. " \
                "Forneça os headers X-Target-WSDL e X-Auth-Token.",
    version="0.1.0"
)

# Montar o GraphQL no endpoint /graphql
app.include_router(graphql_app, prefix="/graphql")

@app.get("/", include_in_schema=False)
def read_root():
    return {"status": "online", "graphql_docs": "/graphql"}

# Função para rodar o Uvicorn
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
