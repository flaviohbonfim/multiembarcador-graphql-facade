# src/main.py
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
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

# --- Geração do OpenAPI Spec a partir do schema GraphQL ---
def generate_openapi_from_graphql() -> Dict[str, Any]:
    """
    Gera um documento OpenAPI 3.0 a partir do schema GraphQL.
    Esta é uma conversão simplificada que mapeia as queries GraphQL
    para endpoints REST no formato OpenAPI.
    """
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Multiembarcador GraphQL Facade - REST API",
            "description": "API REST gerada a partir do schema GraphQL para visualização no Scalar UI. "
                          "Forneça os headers X-Target-WSDL e X-Auth-Token em todas as requisições.",
            "version": "0.1.0"
        },
        "servers": [
            {
                "url": "http://127.0.0.1:8000",
                "description": "Servidor de Desenvolvimento"
            }
        ],
        "paths": {
            "/graphql": {
                "post": {
                    "summary": "Endpoint GraphQL Principal",
                    "description": "Execute queries GraphQL através deste endpoint",
                    "operationId": "graphqlQuery",
                    "tags": ["GraphQL"],
                    "parameters": [
                        {
                            "name": "X-Target-WSDL",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "URL do WSDL do webservice SOAP",
                            "example": "https://braveo.multiembarcador.com.br/SGT.WebService/Cargas.svc?wsdl"
                        },
                        {
                            "name": "X-Auth-Token",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Token de autenticação",
                            "example": "3a5cc98c141541e6bbc82bcc857c7176"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "Query GraphQL",
                                            "example": "query { buscarCarga(protocolo: \"6482243\") { numeroCarga nomeMotorista } }"
                                        },
                                        "variables": {
                                            "type": "object",
                                            "description": "Variáveis da query (opcional)"
                                        }
                                    },
                                    "required": ["query"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Resposta bem-sucedida",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "object",
                                                "description": "Dados retornados pela query"
                                            },
                                            "errors": {
                                                "type": "array",
                                                "items": {"type": "object"},
                                                "description": "Erros da query (se houver)"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Carregamento": {
                    "type": "object",
                    "description": "Dados de um carregamento",
                    "properties": {
                        "numeroCarga": {"type": "string"},
                        "filial": {"type": "string"},
                        "protocoloCarga": {"type": "string"},
                        "cpfMotorista": {"type": "string"},
                        "nomeMotorista": {"type": "string"},
                        "modeloVeicular": {"type": "string"},
                        "placaVeiculo": {"type": "string"},
                        "tipoOperacao": {"type": "string"},
                        "tipoVeiculo": {"type": "string"},
                        "transportador": {"type": "string"},
                        "pedidos": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Pedido"}
                        }
                    }
                },
                "Pedido": {
                    "type": "object",
                    "description": "Dados de um pedido",
                    "properties": {
                        "codFilial": {"type": "string"},
                        "numeroPedidoEmbarcador": {"type": "string"},
                        "protocoloPedido": {"type": "string"},
                        "codigoRota": {"type": "string"},
                        "dataInicioCarregamento": {"type": "string"},
                        "dataPrevisaoEntrega": {"type": "string"},
                        "observacao": {"type": "string"},
                        "ordemEntrega": {"type": "integer"},
                        "pesoBruto": {"type": "number"},
                        "tipoCarga": {"type": "string"},
                        "tipoOperacao": {"type": "string"},
                        "tipoPedido": {"type": "string"},
                        "vendedor": {"type": "string"},
                        "expedidor": {"$ref": "#/components/schemas/Participante"},
                        "recebedor": {"$ref": "#/components/schemas/Participante"},
                        "itensPedido": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ItemPedido"}
                        }
                    }
                },
                "Participante": {
                    "type": "object",
                    "description": "Dados de um participante (expedidor ou recebedor)",
                    "properties": {
                        "bairro": {"type": "string"},
                        "cep": {"type": "string"},
                        "cidade": {"type": "string"},
                        "cnpj": {"type": "string"},
                        "descricao": {"type": "string"},
                        "endereco": {"type": "string"},
                        "estado": {"type": "string"},
                        "ibge": {"type": "string"},
                        "ie": {"type": "string"},
                        "logradouro": {"type": "string"},
                        "numero": {"type": "string"},
                        "razaoSocial": {"type": "string"}
                    }
                },
                "ItemPedido": {
                    "type": "object",
                    "description": "Item de um pedido",
                    "properties": {
                        "codigoGrupoProduto": {"type": "string"},
                        "codigoProduto": {"type": "string"},
                        "descricaoGrupoProduto": {"type": "string"},
                        "descricaoProduto": {"type": "string"},
                        "metroCubico": {"type": "number"},
                        "pesoUnitario": {"type": "number"},
                        "quantidade": {"type": "number"},
                        "valorUnitario": {"type": "number"}
                    }
                },
                "DadosNotaFiscal": {
                    "type": "object",
                    "description": "Dados de uma Nota Fiscal",
                    "properties": {
                        "protocoloCarga": {"type": "string"},
                        "protocoloPedido": {"type": "string"},
                        "chaveAcesso": {"type": "string"},
                        "cnpjExpedidor": {"type": "string"},
                        "cnpjRecebedor": {"type": "string"},
                        "dataEmissao": {"type": "string"},
                        "numero": {"type": "string"},
                        "serie": {"type": "string"},
                        "pesoBruto": {"type": "number"},
                        "pesoLiquido": {"type": "number"},
                        "situacao": {"type": "string"},
                        "valor": {"type": "number"}
                    }
                },
                "NotaFiscalDetalhe": {
                    "type": "object",
                    "description": "Detalhe de uma Nota Fiscal incluindo XML",
                    "properties": {
                        "chaveAcesso": {"type": "string"},
                        "xml": {"type": "string"}
                    }
                }
            }
        },
        "tags": [
            {
                "name": "GraphQL",
                "description": "Operações GraphQL"
            }
        ]
    }

@app.get("/openapi-graphql.json", response_class=JSONResponse, include_in_schema=False)
async def openapi_graphql_spec():
    """
    Retorna o documento OpenAPI gerado a partir do schema GraphQL
    """
    return generate_openapi_from_graphql()

@app.get("/", include_in_schema=False)
def read_root():
    return {
        "status": "online",
        "message": "Multiembarcador GraphQL Facade",
        "endpoints": {
            "graphql": "/graphql - API GraphQL (somente API)",
            "graphiql": "/graphiql - GraphiQL com Docs Explorer e suporte a headers customizados",
            "scalar": "/scalar - Scalar UI - Interface de documentação e testes"
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

@app.get("/scalar", response_class=HTMLResponse, include_in_schema=False)
async def scalarui():
    """
    Scalar UI para visualização da API GraphQL via OpenAPI.
    Os headers X-Target-WSDL e X-Auth-Token devem ser configurados
    diretamente na interface de teste do Scalar.
    """
    # Gerar o spec inline para evitar problemas de CORS/loading
    import json
    openapi_spec = generate_openapi_from_graphql()
    spec_json = json.dumps(openapi_spec)

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Scalar API Reference - Multiembarcador GraphQL Facade</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        html, body {{
            height: 100%;
            width: 100%;
            overflow: hidden;
        }}
        #api-reference {{
            height: 100vh;
            width: 100%;
        }}
    </style>
</head>
<body>
    <div id="api-reference"></div>

    <!-- Carregar o Scalar do CDN -->
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>

    <script>
        // Spec OpenAPI inline
        const openApiSpec = {spec_json};

        // Aguardar o DOM e o Scalar estarem prontos
        document.addEventListener('DOMContentLoaded', () => {{
            console.log('DOM pronto, inicializando Scalar...');

            // Tentar inicializar o Scalar
            const initScalar = () => {{
                if (window.Scalar && window.Scalar.createApiReference) {{
                    try {{
                        console.log('Scalar encontrado, criando referência...');
                        window.Scalar.createApiReference(
                            document.getElementById('api-reference'),
                            {{
                                spec: {{
                                    content: openApiSpec
                                }},
                                theme: 'purple',
                                layout: 'modern',
                                showSidebar: true
                            }}
                        );
                        console.log('Scalar UI inicializado com sucesso!');
                    }} catch (error) {{
                        console.error('Erro ao inicializar Scalar:', error);
                    }}
                }} else {{
                    console.log('Scalar ainda não disponível, aguardando...');
                    setTimeout(initScalar, 100);
                }}
            }};

            // Pequeno delay para garantir que o script foi carregado
            setTimeout(initScalar, 100);
        }});
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

# Função para rodar o Uvicorn
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
