# src/models.py
import strawberry
from typing import List, Optional

@strawberry.type
class ItemPedido:
    """ Baseado no 'ItemPedido' do C# """
    codigoGrupoProduto: Optional[str]
    codigoProduto: Optional[str]
    codigoNcm: Optional[str]
    descricaoGrupoProduto: Optional[str]
    descricaoProduto: Optional[str]
    metroCubico: Optional[float]
    pesoUnitario: Optional[float]
    quantidade: Optional[float]
    valorUnitario: Optional[float]

@strawberry.type
class Participante:
    """ Tipo genérico para Expedidor (Remetente) e Recebedor (Destinatario) """
    bairro: Optional[str]
    cep: Optional[str]
    cidade: Optional[str]
    cnpj: Optional[str]
    descricao: Optional[str]
    endereco: Optional[str]
    estado: Optional[str]
    ibge: Optional[str]
    ie: Optional[str]
    logradouro: Optional[str]
    numero: Optional[str]
    razaoSocial: Optional[str]

@strawberry.type
class Pedido:
    """ Baseado no 'Pedido' do C# """
    codFilial: Optional[str]
    numeroPedidoEmbarcador: Optional[str]
    protocoloPedido: Optional[str]
    codigoRota: Optional[str]
    dataInicioCarregamento: Optional[str] # Usar str ou strawberry.DateTime
    dataPrevisaoEntrega: Optional[str]    # Usar str ou strawberry.DateTime
    observacao: Optional[str]
    ordemEntrega: Optional[int]
    pesoBruto: Optional[float]
    tipoCarga: Optional[str]
    tipoOperacao: Optional[str]
    tipoPedido: Optional[str]
    vendedor: Optional[str]
    expedidor: Optional[Participante]
    recebedor: Optional[Participante]
    itensPedido: List[ItemPedido]

@strawberry.type
class Carregamento:
    """ Objeto aninhado principal, baseado no 'Carregamento' do C# """
    numeroCarga: Optional[str]
    filial: Optional[str]
    protocoloCarga: Optional[str]
    cpfMotorista: Optional[str]
    nomeMotorista: Optional[str]
    modeloVeicular: Optional[str]
    placaVeiculo: Optional[str]
    tipoOperacao: Optional[str]
    tipoVeiculo: Optional[str]
    transportador: Optional[str] # CNPJ
    pedidos: List[Pedido]

@strawberry.type
class DadosNotaFiscal:
    """
    Representa os dados transformados de uma Nota Fiscal,
    baseado no transformer C#.
    """
    protocoloCarga: str # O protocoloCarga passado como argumento
    protocoloPedido: Optional[str]
    chaveAcesso: Optional[str]
    cnpjExpedidor: Optional[str] # x.Emitente.CPFCNPJ
    cnpjRecebedor: Optional[str] # x.Destinatario.CPFCNPJ
    dataEmissao: Optional[str]
    numero: Optional[str]
    serie: Optional[str]
    pesoBruto: Optional[float]
    pesoLiquido: Optional[float]
    situacao: Optional[str]      # x.SituacaoNFeSefaz.ToString()
    valor: Optional[float]

@strawberry.type
class NotaFiscalDetalhe:
    """
    Representa o detalhe de uma NFe, incluindo seu XML.
    Retorno do método BuscarNotaFiscal do CTe.svc.
    """
    chaveAcesso: Optional[str]
    xml: Optional[str]
