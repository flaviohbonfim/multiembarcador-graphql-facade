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

        # 3. Tentar diferentes abordagens para o payload
        # Tentativa 1: Passar protocolo diretamente como string
        response = None
        ns_dom = "http://schemas.datacontract.org/2004/07/Dominio.ObjetosDeValor.WebService.Carga"

        try:
            print(f"[SOAP] Tentando chamar BuscarCarga com protocolo como string...")
            response = client.service.BuscarCarga(
                protocolo=protocolo_str,
                _soapheaders=[header]
            )
        except Exception as e1:
            print(f"[SOAP] Falha com string simples: {e1}")

            # Tentativa 2: Usar tipo Protocolos se existir
            try:
                print(f"[SOAP] Tentando com tipo 'Protocolos'...")
                ProtocolosType = client.get_type(f'{{{ns_dom}}}Protocolos')
                payload = ProtocolosType(ProtocoloCarga=protocolo_str)
                response = client.service.BuscarCarga(
                    protocolo=payload,
                    _soapheaders=[header]
                )
            except Exception as e2:
                print(f"[SOAP] Falha com tipo Protocolos: {e2}")

                # Tentativa 3: Criar objeto com estrutura dinâmica
                try:
                    print(f"[SOAP] Tentando com dicionário simples...")
                    response = client.service.BuscarCarga(
                        protocolo={'ProtocoloCarga': protocolo_str},
                        _soapheaders=[header]
                    )
                except Exception as e3:
                    print(f"[SOAP] Falha com dicionário: {e3}")
                    raise Exception("Todas as tentativas de chamada SOAP falharam")

        # 4. Processar a resposta (baseado no response.txt)
        # Caminho: BuscarCargaResult -> Objeto -> CargaIntegracao (lista)
        if response and response.CodigoMensagem == 0 and response.Objeto and response.Objeto.CargaIntegracao:
            # Serializa a resposta do Zeep para um dict/list Python padrão
            return serialize_object(response.Objeto.CargaIntegracao)

        print(f"[SOAP] Resposta vazia ou com erro: {response.CodigoMensagem} - {response.Mensagem}")
        return None

    except Exception as e:
        print(f"Erro catastrófico ao chamar SOAP: {e}")
        return None
