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
