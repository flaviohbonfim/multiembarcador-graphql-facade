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
            "graphiql": "/graphiql - GraphiQL IDE com Docs Explorer e headers customizados",
            "altair": "/altair - Altair GraphQL Client - IDE avançado com features modernas",
            "voyager": "/voyager - GraphQL Voyager - Visualização gráfica do schema",
            "scalar": "/scalar - Scalar UI - Documentação OpenAPI moderna",
            "openapi": "/openapi-graphql.json - Documento OpenAPI gerado do schema GraphQL"
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
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Scalar API Reference - Multiembarcador GraphQL Facade</title>
</head>
<body>
    <!-- Usar o método de script tag que é mais confiável -->
    <script
        id="api-reference"
        type="application/json"
        data-configuration='{{"theme": "purple"}}'>{spec_json}</script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/voyager", response_class=HTMLResponse, include_in_schema=False)
async def voyager():
    """
    GraphQL Voyager - Visualização interativa do schema GraphQL como um grafo.
    Mostra todas as relações entre tipos de forma visual e intuitiva.
    """
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>GraphQL Voyager - Schema Visualization</title>
    <style>
        body {
            height: 100%;
            margin: 0;
            width: 100%;
            overflow: hidden;
        }
        #voyager {
            height: 100vh;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/react@16/umd/react.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react-dom@16/umd/react-dom.production.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphql-voyager/dist/voyager.css" />
    <script src="https://cdn.jsdelivr.net/npm/graphql-voyager/dist/voyager.min.js"></script>
</head>
<body>
    <div id="voyager">Carregando GraphQL Voyager...</div>
    <script>
        // Função para fazer introspecção com headers customizados
        function introspectionProvider(query) {
            // Headers padrão - usuário pode modificar no código se necessário
            const headers = {
                'Content-Type': 'application/json',
                'X-Target-WSDL': 'https://braveo.multiembarcador.com.br/SGT.WebService/Cargas.svc?wsdl',
                'X-Auth-Token': '3a5cc98c141541e6bbc82bcc857c7176'
            };

            return fetch('/graphql', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ query: query }),
            }).then(response => response.json());
        }

        // Renderizar o Voyager
        GraphQLVoyager.init(document.getElementById('voyager'), {
            introspection: introspectionProvider,
            displayOptions: {
                rootType: 'Query',
                skipRelay: false,
                skipDeprecated: false,
                showLeafFields: true,
                sortByAlphabet: true
            },
            hideDocs: false,
            hideSettings: false
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/altair", response_class=HTMLResponse, include_in_schema=False)
async def altair():
    """
    Altair GraphQL Client - IDE GraphQL avançado com features modernas.
    Suporta múltiplos ambientes, pre-request scripts, upload de arquivos e mais.
    """
    html_content = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Altair GraphQL Client - Multiembarcador Facade</title>
  <base href="./">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link href="https://cdn.jsdelivr.net/npm/altair-static/build/styles.css"
        rel="stylesheet"/>
  <style>
    body {
      margin: 0;
      padding: 0;
      height: 100vh;
      overflow: hidden;
    }
    app-root {
      display: block;
      height: 100%;
    }
  </style>
</head>
<body>
  <app-root>
    <style>
      .loading-screen {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background: #1d1d1d;
        color: #fff;
        font-family: system-ui, -apple-system, sans-serif;
      }
    </style>
    <div class="loading-screen">
      <div class="loading-screen-inner">
        <div class="loading-screen-logo-container">
          <h2>⚡ Carregando Altair GraphQL Client...</h2>
        </div>
      </div>
    </div>
  </app-root>

  <script type="text/javascript"
          src="https://cdn.jsdelivr.net/npm/altair-static/build/main.js">
  </script>

  <script>
    // Configurar Altair com endpoint e headers pré-configurados
    window.addEventListener('load', function() {
      console.log('Window loaded, initializing Altair...');

      if (typeof AltairGraphQL !== 'undefined') {
        console.log('AltairGraphQL found, setting options...');

        var altairOptions = {
          endpointURL: '/graphql',
          initialHeaders: {
            'X-Target-WSDL': 'https://braveo.multiembarcador.com.br/SGT.WebService/Cargas.svc?wsdl',
            'X-Auth-Token': '3a5cc98c141541e6bbc82bcc857c7176'
          },
          initialQuery: `# Bem-vindo ao Altair GraphQL Client! ⚡
#
# Os headers X-Target-WSDL e X-Auth-Token já estão pré-configurados.
# Você pode modificá-los no painel "Set Headers" (ícone de engrenagem) se necessário.
#
# Features disponíveis:
# - 📝 Editor com syntax highlighting e autocomplete
# - 🔍 Explorador de documentação GraphQL
# - 📊 Histórico de queries
# - 🎨 Múltiplos temas (dark/light)
# - 🌍 Suporte a múltiplos ambientes
# - 📤 Upload de arquivos
# - 🔔 Subscriptions GraphQL
#
# Exemplo de query:

query BuscarCargaExemplo {
  buscarCarga(protocolo: "6482243") {
    numeroCarga
    nomeMotorista
    placaVeiculo
    transportador
    pedidos {
      numeroPedidoEmbarcador
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
}`,
          initialSettings: {
            theme: 'dark',
            language: 'en-US',
            addQueryDepthLimit: 7,
            tabSize: 2
          }
        };

        try {
          AltairGraphQL.init(altairOptions);
          console.log('Altair initialized successfully!');
        } catch (error) {
          console.error('Error initializing Altair:', error);
        }
      } else {
        console.error('AltairGraphQL is not defined!');
      }
    });
  </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

# Função para rodar o Uvicorn
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
