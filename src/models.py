# src/models.py
import strawberry
from typing import List, Optional

@strawberry.type
class ItemPedido:
    """ Baseado no 'ItemPedido' do C# """
    CodigoGrupoProduto: Optional[str]
    CodigoProduto: Optional[str]
    DescricaoGrupoProduto: Optional[str]
    DescricaoProduto: Optional[str]
    MetroCubico: Optional[float]
    PesoUnitario: Optional[float]
    Quantidade: Optional[float]
    ValorUnitario: Optional[float]

@strawberry.type
class Participante:
    """ Tipo genérico para Expedidor (Remetente) e Recebedor (Destinatario) """
    Bairro: Optional[str]
    Cep: Optional[str]
    Cidade: Optional[str]
    Cnpj: Optional[str]
    Descricao: Optional[str]
    Endereco: Optional[str]
    Estado: Optional[str]
    Ibge: Optional[str]
    Ie: Optional[str]
    Logradouro: Optional[str]
    Numero: Optional[str]
    RazaoSocial: Optional[str]

@strawberry.type
class Pedido:
    """ Baseado no 'Pedido' do C# """
    CodFilial: Optional[str]
    NumeroPedidoEmbarcador: Optional[str]
    ProtocoloPedido: Optional[str]
    CodigoRota: Optional[str]
    DataInicioCarregamento: Optional[str] # Usar str ou strawberry.DateTime
    DataPrevisaoEntrega: Optional[str]    # Usar str ou strawberry.DateTime
    Observacao: Optional[str]
    OrdemEntrega: Optional[int]
    PesoBruto: Optional[float]
    TipoCarga: Optional[str]
    TipoOperacao: Optional[str]
    TipoPedido: Optional[str]
    Vendedor: Optional[str]
    Expedidor: Optional[Participante]
    Recebedor: Optional[Participante]
    ItensPedido: List[ItemPedido]

@strawberry.type
class Carregamento:
    """ Objeto aninhado principal, baseado no 'Carregamento' do C# """
    NumeroCarga: Optional[str]
    Filial: Optional[str]
    ProtocoloCarga: Optional[str]
    CpfMotorista: Optional[str]
    NomeMotorista: Optional[str]
    ModeloVeicular: Optional[str]
    PlacaVeiculo: Optional[str]
    TipoOperacao: Optional[str]
    TipoVeiculo: Optional[str]
    Transportador: Optional[str] # CNPJ
    Pedidos: List[Pedido]
