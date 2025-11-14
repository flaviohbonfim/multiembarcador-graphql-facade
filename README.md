# multiembarcador-graphql-facade

Fachada GraphQL moderna para o WebService SOAP SGT, permitindo consultas de dados de carregamento em formato GraphQL aninhado e estruturado.

## Visão Geral

Este serviço atua como uma camada de abstração (facade) entre clientes modernos que consomem GraphQL e um webservice SOAP legado. Projetado especificamente para facilitar consultas e migrações de dados entre diferentes ambientes (Produção, Desenvolvimento, etc.).

### Características Principais

- **Configuração Dinâmica**: URL do WSDL e token de autenticação configuráveis por requisição via headers HTTP
- **Transformação de Dados**: Converte respostas SOAP planas em objetos GraphQL aninhados e estruturados
- **Cache Inteligente**: Cliente SOAP com cache LRU para otimizar performance
- **API Moderna**: Interface GraphQL limpa e intuitiva

## Stack Tecnológica

- **Python**: 3.10+
- **Gestor de Dependências**: Poetry
- **Servidor Web**: FastAPI
- **GraphQL**: Strawberry (`strawberry-graphql[fastapi]`)
- **Cliente SOAP**: Zeep

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Poetry (gerenciador de dependências Python)

### Setup

1. Clone o repositório:
```bash
git clone <repository-url>
cd multiembarcador-graphql-facade
```

2. Instale as dependências:
```bash
poetry install
```

3. Ative o ambiente virtual:
```bash
poetry shell
```

## Uso

### Iniciando o Servidor

Execute o servidor de desenvolvimento:

```bash
poetry run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

O servidor estará disponível em: `http://127.0.0.1:8000`

- **Endpoint GraphQL**: `http://127.0.0.1:8000/graphql`
- **Documentação GraphQL (GraphiQL)**: `http://127.0.0.1:8000/graphql` (interface web)

### Headers Obrigatórios

Cada requisição GraphQL DEVE incluir os seguintes headers HTTP:

- `X-Target-WSDL`: URL completa do WSDL do ambiente de destino
- `X-Auth-Token`: Token de autenticação para o ambiente

### Exemplo de Consulta

#### Usando curl

```bash
curl -X POST "http://127.0.0.1:8000/graphql" \
  -H "Content-Type: application/json" \
  -H "X-Target-WSDL: https://braveo.multiembarcador.com.br/SGT.WebService/Cargas.svc?wsdl" \
  -H "X-Auth-Token: 3a5cc98c141541e6bbc82bcc857c7176" \
  -d '{
    "query": "query { buscarCarga(protocolo: \"6482243\") { protocoloCarga numeroCarga nomeMotorista cpfMotorista placaVeiculo pedidos { numeroPedidoEmbarcador protocoloPedido pesoBruto recebedor { razaoSocial cidade estado cnpj } expedidor { razaoSocial cidade } itensPedido { descricaoProduto quantidade valorUnitario } } } }"
  }'
```

#### Query GraphQL Formatada

```graphql
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
}
```

#### Testando Diferentes Ambientes

Para consultar um ambiente diferente (ex: Desenvolvimento), simplesmente altere os headers:

```bash
curl -X POST "http://127.0.0.1:8000/graphql" \
  -H "Content-Type: application/json" \
  -H "X-Target-WSDL: https://dev.multiembarcador.com.br/SGT.WebService/Cargas.svc?wsdl" \
  -H "X-Auth-Token: token-dev-aqui" \
  -d '{"query": "query { ... }"}'
```

### Usando Postman ou Insomnia

1. Crie uma nova requisição POST para `http://127.0.0.1:8000/graphql`
2. Adicione os headers:
   - `Content-Type: application/json`
   - `X-Target-WSDL: <sua-url-wsdl>`
   - `X-Auth-Token: <seu-token>`
3. No body (JSON), adicione:
```json
{
  "query": "query { buscarCarga(protocolo: \"6482243\") { numeroCarga nomeMotorista pedidos { numeroPedidoEmbarcador } } }"
}
```

## Arquitetura

### Estrutura do Projeto

```
multiembarcador-graphql-facade/
├── src/
│   ├── __init__.py
│   ├── main.py           # Configuração FastAPI e injeção de contexto
│   ├── models.py         # Tipos GraphQL (Strawberry)
│   ├── soap_client.py    # Cliente SOAP com cache (Zeep)
│   ├── transformation.py # Lógica de transformação SOAP → GraphQL
│   └── resolvers.py      # Resolver GraphQL
├── pyproject.toml
└── README.md
```

### Fluxo de Dados

1. Cliente envia requisição GraphQL com headers `X-Target-WSDL` e `X-Auth-Token`
2. Resolver GraphQL (`resolvers.py`) extrai os headers do contexto
3. Cliente SOAP (`soap_client.py`) usa o WSDL dinâmico para chamar o serviço
4. Resposta SOAP (lista plana) é transformada em objeto aninhado (`transformation.py`)
5. Objeto GraphQL estruturado é retornado ao cliente

### Principais Componentes

- **models.py**: Define os tipos GraphQL (Carregamento, Pedido, Participante, ItemPedido)
- **soap_client.py**: Gerencia conexão SOAP com cache LRU de clientes WSDL
- **transformation.py**: Converte dados planos SOAP em estrutura hierárquica GraphQL
- **resolvers.py**: Implementa a query `buscarCarga` e orquestra a lógica
- **main.py**: Configura FastAPI e injeta contexto HTTP no Strawberry

## Schema GraphQL

### Query Principal

```graphql
type Query {
  buscarCarga(protocolo: String!): Carregamento
}
```

### Tipos

```graphql
type Carregamento {
  numeroCarga: String
  filial: String
  protocoloCarga: String
  cpfMotorista: String
  nomeMotorista: String
  modeloVeicular: String
  placaVeiculo: String
  tipoOperacao: String
  tipoVeiculo: String
  transportador: String
  pedidos: [Pedido!]!
}

type Pedido {
  codFilial: String
  numeroPedidoEmbarcador: String
  protocoloPedido: String
  codigoRota: String
  dataInicioCarregamento: String
  dataPrevisaoEntrega: String
  observacao: String
  ordemEntrega: Int
  pesoBruto: Float
  tipoCarga: String
  tipoOperacao: String
  tipoPedido: String
  vendedor: String
  expedidor: Participante
  recebedor: Participante
  itensPedido: [ItemPedido!]!
}

type Participante {
  bairro: String
  cep: String
  cidade: String
  cnpj: String
  descricao: String
  endereco: String
  estado: String
  ibge: String
  ie: String
  logradouro: String
  numero: String
  razaoSocial: String
}

type ItemPedido {
  codigoGrupoProduto: String
  codigoProduto: String
  descricaoGrupoProduto: String
  descricaoProduto: String
  metroCubico: Float
  pesoUnitario: Float
  quantidade: Float
  valorUnitario: Float
}
```

## Desenvolvimento

### Executar em Modo Debug

```bash
poetry run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug
```

### Executar Testes (quando implementados)

```bash
poetry run pytest
```

## Roadmap (Próximas Versões)

- [ ] Adicionar testes unitários e de integração
- [ ] Implementar mutations para criação/atualização de cargas
- [ ] Adicionar paginação para grandes volumes de dados
- [ ] Implementar autenticação/autorização na API GraphQL
- [ ] Adicionar métricas e observabilidade (Prometheus, OpenTelemetry)
- [ ] Suporte a múltiplos métodos SOAP além de BuscarCarga
- [ ] Documentação automática de schema com GraphQL SDL

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## Licença

[Especificar licença]

## Suporte

Para problemas ou dúvidas, abra uma issue no repositório do projeto.
