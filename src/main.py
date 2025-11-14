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

# Criar endpoint GraphiQL com documentação interativa
graphiql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphql_ide="graphiql"
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

# Montar o GraphiQL (com documentação interativa) no endpoint /graphiql
app.include_router(graphiql_app, prefix="/graphiql")

@app.get("/", include_in_schema=False)
def read_root():
    return {
        "status": "online",
        "message": "Multiembarcador GraphQL Facade",
        "endpoints": {
            "graphql": "/graphql - API GraphQL (somente API)",
            "graphiql": "/graphiql - GraphiQL com documentação do Schema (Docs Explorer)",
            "playground": "/playground - Interface de testes interativa com suporte a headers"
        }
    }

@app.get("/playground", response_class=HTMLResponse, include_in_schema=False)
async def playground():
    """
    Interface GraphQL Playground com suporte a headers customizados
    """
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GraphQL Playground - Multiembarcador Facade</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f1419;
            color: #e8eaed;
        }
        #header {
            background: #1a1d23;
            padding: 15px 20px;
            border-bottom: 1px solid #2d3139;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        #header h1 {
            margin: 0;
            font-size: 18px;
            font-weight: 500;
        }
        #header-config {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        #container {
            display: flex;
            height: calc(100vh - 60px);
        }
        #sidebar {
            width: 350px;
            background: #1a1d23;
            border-right: 1px solid #2d3139;
            padding: 20px;
            overflow-y: auto;
        }
        #main {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .input-group {
            margin-bottom: 15px;
        }
        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            color: #9aa0a6;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .input-group input {
            width: 100%;
            padding: 10px;
            background: #0f1419;
            border: 1px solid #2d3139;
            border-radius: 4px;
            color: #e8eaed;
            font-size: 13px;
            box-sizing: border-box;
        }
        .input-group input:focus {
            outline: none;
            border-color: #5183f5;
        }
        textarea {
            width: 100%;
            height: 50%;
            padding: 15px;
            background: #0f1419;
            border: 1px solid #2d3139;
            border-radius: 4px;
            color: #e8eaed;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            resize: vertical;
            box-sizing: border-box;
        }
        textarea:focus {
            outline: none;
            border-color: #5183f5;
        }
        button {
            background: #5183f5;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: background 0.2s;
        }
        button:hover {
            background: #3d6ee6;
        }
        button:active {
            background: #2d5dd4;
        }
        #result {
            flex: 1;
            padding: 15px;
            background: #0f1419;
            overflow-y: auto;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .error {
            color: #f28b82;
        }
        .success {
            color: #81c995;
        }
        .example-link {
            color: #5183f5;
            text-decoration: none;
            font-size: 12px;
            margin-left: 10px;
        }
        .example-link:hover {
            text-decoration: underline;
        }
        .info-box {
            background: #1e2833;
            border-left: 3px solid #5183f5;
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 4px;
            font-size: 12px;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div id="header">
        <h1>🚀 Multiembarcador GraphQL Facade - Playground</h1>
        <div id="header-config">
            <span style="font-size: 12px; color: #9aa0a6;">Endpoint: /graphql</span>
        </div>
    </div>

    <div id="container">
        <div id="sidebar">
            <div class="info-box">
                <strong>⚠️ Headers Obrigatórios:</strong><br>
                Configure os headers abaixo antes de executar queries.
            </div>

            <div class="input-group">
                <label>X-Target-WSDL</label>
                <input type="text" id="wsdl" placeholder="https://braveo.multiembarcador.com.br/SGT.WebService/Cargas.svc?wsdl" value="https://braveo.multiembarcador.com.br/SGT.WebService/Cargas.svc?wsdl">
            </div>

            <div class="input-group">
                <label>X-Auth-Token</label>
                <input type="text" id="token" placeholder="Seu token de autenticação" value="3a5cc98c141541e6bbc82bcc857c7176">
            </div>

            <hr style="border: none; border-top: 1px solid #2d3139; margin: 20px 0;">

            <div class="info-box">
                <strong>📝 Query de Exemplo:</strong><br>
                <a href="#" class="example-link" onclick="loadExample(); return false;">Carregar exemplo de buscarCarga</a>
            </div>
        </div>

        <div id="main">
            <textarea id="query" placeholder="Digite sua query GraphQL aqui...">query {
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
}</textarea>

            <div style="padding: 15px; background: #1a1d23; border-top: 1px solid #2d3139; border-bottom: 1px solid #2d3139;">
                <button onclick="executeQuery()">▶ Executar Query</button>
                <button onclick="clearResult()" style="background: #5f6368; margin-left: 10px;">Limpar</button>
            </div>

            <div id="result">Resultado aparecerá aqui...</div>
        </div>
    </div>

    <script>
        function loadExample() {
            document.getElementById('query').value = `query {
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
      dataPrevisaoEntrega
      recebedor {
        razaoSocial
        cidade
        estado
        cnpj
        endereco
        cep
      }
      expedidor {
        razaoSocial
        cidade
        estado
      }
      itensPedido {
        descricaoProduto
        codigoProduto
        quantidade
        valorUnitario
        pesoUnitario
      }
    }
  }
}`;
        }

        async function executeQuery() {
            const query = document.getElementById('query').value;
            const wsdl = document.getElementById('wsdl').value;
            const token = document.getElementById('token').value;
            const resultDiv = document.getElementById('result');

            if (!wsdl || !token) {
                resultDiv.innerHTML = '<span class="error">❌ Erro: Configure os headers X-Target-WSDL e X-Auth-Token</span>';
                return;
            }

            resultDiv.innerHTML = '<span style="color: #9aa0a6;">⏳ Executando query...</span>';

            try {
                const response = await fetch('/graphql', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Target-WSDL': wsdl,
                        'X-Auth-Token': token
                    },
                    body: JSON.stringify({ query })
                });

                const result = await response.json();

                if (response.ok) {
                    if (result.errors) {
                        resultDiv.innerHTML = '<span class="error">❌ Erros GraphQL:</span>\\n' +
                            JSON.stringify(result, null, 2);
                    } else {
                        resultDiv.innerHTML = '<span class="success">✅ Sucesso:</span>\\n' +
                            JSON.stringify(result, null, 2);
                    }
                } else {
                    resultDiv.innerHTML = '<span class="error">❌ Erro HTTP ' + response.status + ':</span>\\n' +
                        JSON.stringify(result, null, 2);
                }
            } catch (error) {
                resultDiv.innerHTML = '<span class="error">❌ Erro de conexão:</span>\\n' + error.message;
            }
        }

        function clearResult() {
            document.getElementById('result').innerHTML = 'Resultado aparecerá aqui...';
        }

        // Permitir executar com Ctrl+Enter
        document.getElementById('query').addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                executeQuery();
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
