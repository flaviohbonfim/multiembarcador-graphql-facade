# src/soap_client.py
import zeep
from zeep.helpers import serialize_object
from lxml import etree
from typing import Optional, List, Any
from functools import lru_cache

@lru_cache(maxsize=10) # Cacheia os 10 últimos clientes WSDL
def get_zeep_client(wsdl_url: str) -> zeep.Client:
    """
    Cria e cacheia um cliente Zeep.
    Parsear WSDL é uma operação lenta e cara.
    """
    print(f"[Zeep] Criando novo cliente para: {wsdl_url}")
    return zeep.Client(wsdl=wsdl_url)

def chamar_buscar_carga(protocolo_str: str, wsdl_url: str, token: str) -> Optional[List[dict]]:
    """
    Chama o método SOAP BuscarCarga dinamicamente.
    """
    try:
        # 1. Obter cliente (possivelmente cacheado)
        client = get_zeep_client(wsdl_url=wsdl_url)

        # 2. Criar o Header SOAP com o Token dinâmico
        header = etree.Element(
            '{Token}Token',
            xmlns="Token"
        )
        header.text = token

        # 3. Criar o payload baseado no XML de exemplo
        # A estrutura esperada é:
        # <tem:protocolo>
        #   <dom:protocoloIntegracaoCarga>6482243</dom:protocoloIntegracaoCarga>
        # </tem:protocolo>

        print(f"[SOAP] Criando payload com estrutura: {{protocoloIntegracaoCarga: '{protocolo_str}'}}")

        # Criar objeto com a estrutura correta usando dicionário
        # O Zeep automaticamente converte para o tipo SOAP correto
        payload = {
            'protocoloIntegracaoCarga': protocolo_str
        }

        # 4. Chamar o serviço
        print(f"[SOAP] Chamando BuscarCarga...")
        response = client.service.BuscarCarga(
            protocolo=payload,
            _soapheaders=[header]
        )

        # 5. Processar a resposta (baseado no response.txt)
        # Caminho: BuscarCargaResult -> Objeto -> CargaIntegracao (lista)
        if response and response.CodigoMensagem == 0 and response.Objeto and response.Objeto.CargaIntegracao:
            # Serializa a resposta do Zeep para um dict/list Python padrão
            return serialize_object(response.Objeto.CargaIntegracao)

        print(f"[SOAP] Resposta vazia ou com erro: {response.CodigoMensagem} - {response.Mensagem}")
        return None

    except Exception as e:
        print(f"Erro catastrófico ao chamar SOAP: {e}")
        return None

def chamar_buscar_carga_por_codigos_integracao(codigo_filial: str, numero_carga: str, wsdl_url: str, token: str) -> Optional[List[dict]]:
    """
    Chama o método SOAP BuscarCargaPorCodigosIntegracao dinamicamente.
    """
    try:
        # 1. Obter cliente (possivelmente cacheado)
        client = get_zeep_client(wsdl_url=wsdl_url)

        # 2. Criar o Header SOAP com o Token dinâmico
        header = etree.Element(
            '{Token}Token',
            xmlns="Token"
        )
        header.text = token

        # 3. Criar o payload baseado no XML de exemplo
        # A estrutura esperada é:
        # <tem:codigosIntegracao>
        #   <dom:CodigoIntegracaoFilial>100006</dom:CodigoIntegracaoFilial>
        #   <dom:NumeroCarga>15440482</dom:NumeroCarga>
        # </tem:codigosIntegracao>

        print(f"[SOAP] Criando payload com CodigoIntegracaoFilial: '{codigo_filial}', NumeroCarga: '{numero_carga}'")

        # Criar objeto com a estrutura correta usando dicionário
        # O Zeep automaticamente converte para o tipo SOAP correto
        payload = {
            'CodigoIntegracaoFilial': codigo_filial,
            'NumeroCarga': numero_carga
        }

        # 4. Chamar o serviço
        print(f"[SOAP] Chamando BuscarCargaPorCodigosIntegracao...")
        response = client.service.BuscarCargaPorCodigosIntegracao(
            codigosIntegracao=payload,
            _soapheaders=[header]
        )

        # 5. Processar a resposta (mesmo formato do BuscarCarga)
        # Caminho: BuscarCargaPorCodigosIntegracaoResult -> Objeto -> CargaIntegracao (lista)
        if response and response.CodigoMensagem == 0 and response.Objeto and response.Objeto.CargaIntegracao:
            # Serializa a resposta do Zeep para um dict/list Python padrão
            return serialize_object(response.Objeto.CargaIntegracao)

        print(f"[SOAP] Resposta vazia ou com erro: {response.CodigoMensagem} - {response.Mensagem}")
        return None

    except Exception as e:
        print(f"Erro catastrófico ao chamar SOAP: {e}")
        return None

def chamar_buscar_notas_fiscais(protocolo_carga: str, inicio: int, limite: int, wsdl_url: str, token: str) -> Optional[List[dict]]:
    """
    Chama o método SOAP BuscarNotasFiscaisVinculadas dinamicamente.
    """
    try:
        # 1. Obter cliente (possivelmente cacheado)
        # Importante: o wsdl_url aqui deve ser o da NFe.svc
        client = get_zeep_client(wsdl_url=wsdl_url)

        # 2. Criar o Header SOAP com o Token dinâmico
        header = etree.Element(
            '{Token}Token',
            xmlns="Token"
        )
        header.text = token

        # 3. Chamar o serviço
        # O corpo da requisição é simples, sem tipos complexos aninhados:
        # <tem:BuscarNotasFiscaisVinculadas>
        #   <tem:protocoloCarga>...</tem:protocoloCarga>
        #   <tem:inicio>...</tem:inicio>
        #   <tem:limite>...</tem:limite>
        # </tem:BuscarNotasFiscaisVinculadas>
        # Zeep mapeia isso diretamente para os argumentos da função.

        print(f"[SOAP] Chamando BuscarNotasFiscaisVinculadas com protocoloCarga={protocolo_carga}, inicio={inicio}, limite={limite}")

        response = client.service.BuscarNotasFiscaisVinculadas(
            protocoloCarga=protocolo_carga,
            inicio=inicio,
            limite=limite,
            _soapheaders=[header]
        )

        # 4. Processar a resposta (baseado no response.txt)
        # Caminho: BuscarNotasFiscaisVinculadasResult -> Objeto -> Itens -> NotaFiscal (lista)
        if response and response.CodigoMensagem == 0 and response.Objeto and response.Objeto.Itens:
            # A lista de notas está dentro de Itens.NotaFiscal
            # Se 'Itens' estiver presente mas 'NotaFiscal' não (sem notas),
            # serialize_object lidará com isso e retornará None ou uma lista vazia.
            notas_fiscais = response.Objeto.Itens.get('NotaFiscal')
            if notas_fiscais:
                return serialize_object(notas_fiscais)
            else:
                print("[SOAP] Resposta OK, mas sem notas fiscais (Itens.NotaFiscal está vazio).")
                return [] # Retorna lista vazia

        print(f"[SOAP] Resposta vazia ou com erro: {response.CodigoMensagem} - {response.Mensagem}")
        return None

    except Exception as e:
        print(f"Erro catastrófico ao chamar SOAP (NFe): {e}")
        return None
