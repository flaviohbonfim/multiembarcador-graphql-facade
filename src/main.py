# src/main.py
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
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
    return {
        "status": "online",
        "message": "Multiembarcador GraphQL Facade",
        "endpoints": {
            "graphql": "/graphql - API GraphQL (somente API)",
            "graphiql": "/graphiql - GraphiQL com Docs Explorer e suporte a headers customizados"
        }
    }

@app.get("/graphiql", response_class=HTMLResponse, include_in_schema=False)
async def graphiql():
    """
    GraphiQL customizado com Docs Explorer e suporte a headers customizados
    """
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GraphiQL - Multiembarcador GraphQL Facade</title>
    <style>
        body {
            height: 100%;
            margin: 0;
            width: 100%;
            overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        #graphiql {
            height: 100vh;
        }
        #header-config {
            background: #1a1d23;
            padding: 12px 20px;
            border-bottom: 1px solid #2d3139;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        #header-config h1 {
            margin: 0;
            font-size: 16px;
            font-weight: 500;
            color: #e8eaed;
            flex-shrink: 0;
        }
        .input-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .input-group label {
            font-size: 11px;
            color: #9aa0a6;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }
        .input-group input {
            padding: 6px 10px;
            background: #0f1419;
            border: 1px solid #2d3139;
            border-radius: 4px;
            color: #e8eaed;
            font-size: 12px;
            min-width: 300px;
        }
        .input-group input:focus {
            outline: none;
            border-color: #5183f5;
        }
        .status-indicator {
            margin-left: auto;
            font-size: 11px;
            color: #81c995;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            background: #81c995;
            border-radius: 50%;
        }
    </style>
    <link rel="stylesheet" href="https://unpkg.com/graphiql@3.0.10/graphiql.min.css" />
</head>
<body>
    <div id="header-config">
        <h1>🚀 Multiembarcador GraphQL Facade</h1>
        <div class="input-group">
            <label>X-Target-WSDL</label>
            <input
                type="text"
                id="wsdl"
                placeholder="URL do WSDL"
                value="https://braveo.multiembarcador.com.br/SGT.WebService/Cargas.svc?wsdl"
            >
        </div>
        <div class="input-group">
            <label>X-Auth-Token</label>
            <input
                type="text"
                id="token"
                placeholder="Token de autenticação"
                value="3a5cc98c141541e6bbc82bcc857c7176"
            >
        </div>
        <div class="status-indicator">
            <div class="status-dot"></div>
            <span>GraphiQL com Docs Explorer</span>
        </div>
    </div>
    <div id="graphiql">Carregando GraphiQL...</div>

    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/graphiql@3.0.10/graphiql.min.js"></script>

    <script>
        // Função para criar o fetcher customizado com os headers
        function createFetcher() {
            return function graphQLFetcher(graphQLParams) {
                const wsdl = document.getElementById('wsdl').value;
                const token = document.getElementById('token').value;

                const headers = {
                    'Content-Type': 'application/json',
                };

                if (wsdl) {
                    headers['X-Target-WSDL'] = wsdl;
                }

                if (token) {
                    headers['X-Auth-Token'] = token;
                }

                return fetch('/graphql', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(graphQLParams),
                })
                .then(response => response.json())
                .catch(error => {
                    console.error('GraphQL request error:', error);
                    return { errors: [{ message: error.message }] };
                });
            };
        }

        // Query padrão de exemplo
        const defaultQuery = `# Bem-vindo ao GraphiQL!
#
# Configure os headers acima (X-Target-WSDL e X-Auth-Token)
# Clique em "< Docs" no canto superior direito para explorar o Schema
#
# Exemplo de query:

query {
  buscarCarga(protocolo: "6482243") {
    protocoloCarga
    numeroCarga
    nomeMotorista
    cpfMotorista
    placaVeiculo
    transportador
    pedidos {
      numeroPedidoEmbarcador
      protocoloPedido
      pesoBruto
      recebedor {
        razaoSocial
        cidade
        estado
      }
      itensPedido {
        descricaoProduto
        quantidade
        valorUnitario
      }
    }
  }
}`;

        // Renderizar o GraphiQL
        const root = ReactDOM.createRoot(document.getElementById('graphiql'));
        root.render(
            React.createElement(GraphiQL, {
                fetcher: createFetcher(),
                defaultQuery: defaultQuery,
                headerEditorEnabled: false,
                shouldPersistHeaders: false
            })
        );

        // Atualizar o fetcher quando os headers mudarem
        document.getElementById('wsdl').addEventListener('change', () => {
            root.render(
                React.createElement(GraphiQL, {
                    fetcher: createFetcher(),
                    defaultQuery: defaultQuery,
                    headerEditorEnabled: false,
                    shouldPersistHeaders: false
                })
            );
        });

        document.getElementById('token').addEventListener('change', () => {
            root.render(
                React.createElement(GraphiQL, {
                    fetcher: createFetcher(),
                    defaultQuery: defaultQuery,
                    headerEditorEnabled: false,
                    shouldPersistHeaders: false
                })
            );
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

# Função para rodar o Uvicorn
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
