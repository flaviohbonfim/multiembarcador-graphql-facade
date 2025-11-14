# src/transformation.py
from typing import List, Optional, Any, Dict
from .models import Carregamento, Pedido, ItemPedido, Participante

def safe_get(data: Dict, *keys: Any) -> Optional[Any]:
    """
    Acessa chaves aninhadas em dicionários ou listas com segurança.
    Ex: safe_get(data, 'Veiculo', 'Placa')
    Ex: safe_get(data, 'Motoristas', 0, 'Nome')
    """
    temp = data
    for key in keys:
        if temp is None:
            return None
        if isinstance(key, int): # Acesso a índice de lista
            if isinstance(temp, list) and len(temp) > key:
                temp = temp[key]
            else:
                return None
        elif isinstance(key, str): # Acesso a chave de dicionário
            if isinstance(temp, dict):
                temp = temp.get(key)
            else:
                return None
        else:
            return None
    return temp

def transformar_carga_integracao(carga_integracao: List[Dict]) -> Optional[Carregamento]:
    """
    Transforma a resposta plana do SOAP (List<CargaIntegracao>)
    em um objeto 'Carregamento' aninhado.
    """
    if not carga_integracao:
        return None

    try:
        # 1. Obter dados do Cabeçalho (do primeiro item da lista)
        linha = carga_integracao[0]

        carregamento = Carregamento(
            NumeroCarga=safe_get(linha, 'NumeroCarga'),
            Filial=safe_get(linha, 'Filial', 'CodigoIntegracao'),
            ProtocoloCarga=safe_get(linha, 'ProtocoloCarga'),
            CpfMotorista=safe_get(linha, 'Motoristas', 0, 'CPF'),
            NomeMotorista=safe_get(linha, 'Motoristas', 0, 'Nome'),
            ModeloVeicular=safe_get(linha, 'ModeloVeicular', 'CodigoIntegracao'),
            PlacaVeiculo=safe_get(linha, 'Veiculo', 'Placa'),
            TipoOperacao=safe_get(linha, 'TipoOperacao', 'CodigoIntegracao'),
            TipoVeiculo=str(safe_get(linha, 'Veiculo', 'TipoVeiculo') or ''),
            Transportador=safe_get(linha, 'TransportadoraEmitente', 'CNPJ'),
            Pedidos=[]
        )

        # 2. Iterar sobre TODOS os itens para montar a lista de Pedidos
        for p in carga_integracao:
            expedidor = Participante(
                Bairro=safe_get(p, 'Remetente', 'Endereco', 'Bairro'),
                Cep=safe_get(p, 'Remetente', 'Endereco', 'CEP'),
                Cidade=safe_get(p, 'Remetente', 'Endereco', 'Cidade', 'Descricao'),
                Cnpj=safe_get(p, 'Remetente', 'CPFCNPJ'),
                Descricao=safe_get(p, 'Remetente', 'NomeFantasia'),
                Endereco=safe_get(p, 'Remetente', 'Endereco', 'Logradouro'),
                Estado=safe_get(p, 'Remetente', 'Endereco', 'Cidade', 'SiglaUF'),
                Ibge=safe_get(p, 'Remetente', 'Endereco', 'Cidade', 'IBGE'),
                Ie=safe_get(p, 'Remetente', 'RGIE'),
                Logradouro=safe_get(p, 'Remetente', 'Endereco', 'Logradouro'),
                Numero=safe_get(p, 'Remetente', 'Endereco', 'Numero'),
                RazaoSocial=safe_get(p, 'Remetente', 'RazaoSocial')
            )

            recebedor = Participante(
                Bairro=safe_get(p, 'Destinatario', 'Endereco', 'Bairro'),
                Cep=safe_get(p, 'Destinatario', 'Endereco', 'CEP'),
                Cidade=safe_get(p, 'Destinatario', 'Endereco', 'Cidade', 'Descricao'),
                Cnpj=safe_get(p, 'Destinatario', 'CPFCNPJ'),
                Descricao=safe_get(p, 'Destinatario', 'NomeFantasia'),
                Endereco=safe_get(p, 'Destinatario', 'Endereco', 'Logradouro'),
                Estado=safe_get(p, 'Destinatario', 'Endereco', 'Cidade', 'SiglaUF'),
                Ibge=safe_get(p, 'Destinatario', 'Endereco', 'Cidade', 'IBGE'),
                Ie=safe_get(p, 'Destinatario', 'RGIE'),
                Logradouro=safe_get(p, 'Destinatario', 'Endereco', 'Logradouro'),
                Numero=safe_get(p, 'Destinatario', 'Endereco', 'Numero'),
                RazaoSocial=safe_get(p, 'Destinatario', 'RazaoSocial')
            )

            itens_pedido = []
            produtos = safe_get(p, 'Produtos')
            if produtos and isinstance(produtos, list):
                for a in produtos:
                    itens_pedido.append(ItemPedido(
                        CodigoGrupoProduto=safe_get(a, 'CodigoGrupoProduto'),
                        CodigoProduto=safe_get(a, 'CodigoProduto'),
                        DescricaoGrupoProduto=safe_get(a, 'DescricaoGrupoProduto'),
                        DescricaoProduto=safe_get(a, 'DescricaoProduto'),
                        MetroCubico=safe_get(a, 'MetroCubito'), # Atenção ao 'MetroCubito'
                        PesoUnitario=safe_get(a, 'PesoUnitario'),
                        Quantidade=safe_get(a, 'Quantidade'),
                        ValorUnitario=safe_get(a, 'ValorUnitario')
                    ))

            pedido = Pedido(
                CodFilial=safe_get(p, 'Filial', 'CodigoIntegracao'),
                NumeroPedidoEmbarcador=safe_get(p, 'NumeroPedidoEmbarcador'),
                ProtocoloPedido=safe_get(p, 'ProtocoloPedido'),
                CodigoRota=safe_get(p, 'CodigoIntegracaoRota'),
                DataInicioCarregamento=str(safe_get(p, 'DataInicioCarregamento') or ''),
                DataPrevisaoEntrega=str(safe_get(p, 'DataPrevisaoEntrega') or ''),
                Observacao=safe_get(p, 'Observacao'),
                OrdemEntrega=safe_get(p, 'OrdemEntrega'),
                PesoBruto=safe_get(p, 'PesoBruto'),
                TipoCarga=safe_get(p, 'TipoCargaEmbarcador', 'CodigoIntegracao'),
                TipoOperacao=safe_get(p, 'TipoOperacao', 'CodigoIntegracao'),
                TipoPedido=str(safe_get(p, 'TipoPedido') or ''),
                Vendedor=safe_get(p, 'Vendedor'),
                Expedidor=expedidor,
                Recebedor=recebedor,
                ItensPedido=itens_pedido
            )
            carregamento.Pedidos.append(pedido)

        return carregamento

    except Exception as e:
        print(f"Erro catastrófico ao transformar dados: {e}")
        return None
