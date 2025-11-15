# src/transformation.py
from typing import List, Optional, Any, Dict
from .models import Carregamento, Pedido, ItemPedido, Participante, DadosNotaFiscal

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
            numeroCarga=safe_get(linha, 'NumeroCarga'),
            filial=safe_get(linha, 'Filial', 'CodigoIntegracao'),
            protocoloCarga=safe_get(linha, 'ProtocoloCarga'),
            # Motoristas é um OrderedDict com estrutura: {'Motorista': [{...}, {...}]}
            # Similar a Produtos, precisamos acessar a chave 'Motorista' que contém a lista
            cpfMotorista=safe_get(linha, 'Motoristas', 'Motorista', 0, 'CPF'),
            nomeMotorista=safe_get(linha, 'Motoristas', 'Motorista', 0, 'Nome'),
            modeloVeicular=safe_get(linha, 'ModeloVeicular', 'CodigoIntegracao'),
            placaVeiculo=safe_get(linha, 'Veiculo', 'Placa'),
            tipoOperacao=safe_get(linha, 'TipoOperacao', 'CodigoIntegracao'),
            tipoVeiculo=str(safe_get(linha, 'Veiculo', 'TipoVeiculo') or ''),
            transportador=safe_get(linha, 'TransportadoraEmitente', 'CNPJ'),
            pedidos=[]
        )

        # 2. Iterar sobre TODOS os itens para montar a lista de Pedidos
        for p in carga_integracao:
            expedidor = Participante(
                bairro=safe_get(p, 'Remetente', 'Endereco', 'Bairro'),
                cep=safe_get(p, 'Remetente', 'Endereco', 'CEP'),
                cidade=safe_get(p, 'Remetente', 'Endereco', 'Cidade', 'Descricao'),
                cnpj=safe_get(p, 'Remetente', 'CPFCNPJ'),
                descricao=safe_get(p, 'Remetente', 'NomeFantasia'),
                endereco=safe_get(p, 'Remetente', 'Endereco', 'Logradouro'),
                estado=safe_get(p, 'Remetente', 'Endereco', 'Cidade', 'SiglaUF'),
                ibge=safe_get(p, 'Remetente', 'Endereco', 'Cidade', 'IBGE'),
                ie=safe_get(p, 'Remetente', 'RGIE'),
                logradouro=safe_get(p, 'Remetente', 'Endereco', 'Logradouro'),
                numero=safe_get(p, 'Remetente', 'Endereco', 'Numero'),
                razaoSocial=safe_get(p, 'Remetente', 'RazaoSocial')
            )

            recebedor = Participante(
                bairro=safe_get(p, 'Destinatario', 'Endereco', 'Bairro'),
                cep=safe_get(p, 'Destinatario', 'Endereco', 'CEP'),
                cidade=safe_get(p, 'Destinatario', 'Endereco', 'Cidade', 'Descricao'),
                cnpj=safe_get(p, 'Destinatario', 'CPFCNPJ'),
                descricao=safe_get(p, 'Destinatario', 'NomeFantasia'),
                endereco=safe_get(p, 'Destinatario', 'Endereco', 'Logradouro'),
                estado=safe_get(p, 'Destinatario', 'Endereco', 'Cidade', 'SiglaUF'),
                ibge=safe_get(p, 'Destinatario', 'Endereco', 'Cidade', 'IBGE'),
                ie=safe_get(p, 'Destinatario', 'RGIE'),
                logradouro=safe_get(p, 'Destinatario', 'Endereco', 'Logradouro'),
                numero=safe_get(p, 'Destinatario', 'Endereco', 'Numero'),
                razaoSocial=safe_get(p, 'Destinatario', 'RazaoSocial')
            )

            itens_pedido = []
            # Produtos é um OrderedDict com estrutura: {'Produto': [{...}, {...}]}
            # Precisamos acessar a chave 'Produto' que contém a lista
            produtos = safe_get(p, 'Produtos', 'Produto')

            if produtos and isinstance(produtos, list):
                for a in produtos:
                    itens_pedido.append(ItemPedido(
                        codigoGrupoProduto=safe_get(a, 'CodigoGrupoProduto'),
                        codigoProduto=safe_get(a, 'CodigoProduto'),
                        codigoNcm=safe_get(a, 'CodigoNCM'),
                        descricaoGrupoProduto=safe_get(a, 'DescricaoGrupoProduto'),
                        descricaoProduto=safe_get(a, 'DescricaoProduto'),
                        metroCubico=safe_get(a, 'MetroCubito'), # Atenção ao 'MetroCubito'
                        pesoUnitario=safe_get(a, 'PesoUnitario'),
                        quantidade=safe_get(a, 'Quantidade'),
                        valorUnitario=safe_get(a, 'ValorUnitario')
                    ))

            pedido = Pedido(
                codFilial=safe_get(p, 'Filial', 'CodigoIntegracao'),
                numeroPedidoEmbarcador=safe_get(p, 'NumeroPedidoEmbarcador'),
                protocoloPedido=safe_get(p, 'ProtocoloPedido'),
                codigoRota=safe_get(p, 'CodigoIntegracaoRota'),
                dataInicioCarregamento=str(safe_get(p, 'DataInicioCarregamento') or ''),
                dataPrevisaoEntrega=str(safe_get(p, 'DataPrevisaoEntrega') or ''),
                observacao=safe_get(p, 'Observacao'),
                ordemEntrega=safe_get(p, 'OrdemEntrega'),
                pesoBruto=safe_get(p, 'PesoBruto'),
                tipoCarga=safe_get(p, 'TipoCargaEmbarcador', 'CodigoIntegracao'),
                tipoOperacao=safe_get(p, 'TipoOperacao', 'CodigoIntegracao'),
                tipoPedido=str(safe_get(p, 'TipoPedido') or ''),
                vendedor=safe_get(p, 'Vendedor'),
                expedidor=expedidor,
                recebedor=recebedor,
                itensPedido=itens_pedido
            )
            carregamento.pedidos.append(pedido)

        return carregamento

    except Exception as e:
        print(f"Erro catastrófico ao transformar dados: {e}")
        return None

def transformar_nota_fiscal(notas: List[Dict], protocolo_carga_str: str) -> List[DadosNotaFiscal]:
    """
    Transforma a resposta do SOAP (List<NotaFiscal>)
    em uma lista de 'DadosNotaFiscal', baseado na lógica C#.
    """
    if not notas:
        return []

    try:
        lista_transformada = []
        for x in notas:
            # Mapeamento baseado no transformer C#
            nota = DadosNotaFiscal(
                protocoloCarga=protocolo_carga_str, # O protocolo passado para a função
                protocoloPedido=safe_get(x, 'ProtocoloPedido'),
                chaveAcesso=safe_get(x, 'Chave'),
                cnpjExpedidor=safe_get(x, 'Emitente', 'CPFCNPJ'),
                cnpjRecebedor=safe_get(x, 'Destinatario', 'CPFCNPJ'),
                dataEmissao=safe_get(x, 'DataEmissao'),
                numero=safe_get(x, 'Numero'),
                serie=safe_get(x, 'Serie'),
                pesoBruto=safe_get(x, 'PesoBruto'),
                pesoLiquido=safe_get(x, 'PesoLiquido'),
                situacao=str(safe_get(x, 'SituacaoNFeSefaz') or ''),
                valor=safe_get(x, 'Valor')
            )
            lista_transformada.append(nota)

        return lista_transformada

    except Exception as e:
        print(f"Erro catastrófico ao transformar dados da Nota Fiscal: {e}")
        return [] # Retorna lista vazia em caso de erro
