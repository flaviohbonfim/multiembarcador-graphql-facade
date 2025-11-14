# src/resolvers.py
import strawberry
from typing import Optional
from .models import Carregamento
from .soap_client import chamar_buscar_carga, chamar_buscar_carga_por_codigos_integracao
from .transformation import transformar_carga_integracao
from fastapi import HTTPException

@strawberry.type
class Query:

    @strawberry.field
    def buscarCarga(self, protocolo: str, info: strawberry.Info) -> Optional[Carregamento]:
        """
        Busca dados de uma carga no webservice SOAP (endpoint e token
        via headers) e os transforma para um formato aninhado.
        """

        # 1. Acessar o contexto para ler a requisição (e os headers)
        # Isso só funciona por causa do 'context_getter' no main.py
        request = info.context.get("request")
        if not request:
            raise HTTPException(status_code=500, detail="Contexto da requisição não encontrado.")

        # 2. Ler os headers dinâmicos
        target_wsdl_url = request.headers.get("X-Target-WSDL")
        target_token = request.headers.get("X-Auth-Token")

        # 3. Validar os headers
        if not target_wsdl_url or not target_token:
            print("Erro: Headers X-Target-WSDL ou X-Auth-Token não fornecidos.")
            raise HTTPException(
                status_code=400,
                detail="Headers X-Target-WSDL e X-Auth-Token são obrigatórios."
            )

        print(f"[Query] buscando protocolo {protocolo} em {target_wsdl_url}")

        # 4. Chamar o cliente SOAP
        raw_data = chamar_buscar_carga(
            protocolo_str=protocolo,
            wsdl_url=target_wsdl_url,
            token=target_token
        )

        if not raw_data:
            print("Nenhum dado retornado do SOAP.")
            return None

        print(f"[Query] Recebidos {len(raw_data)} registros do SOAP. Transformando...")

        # 5. Chamar a função de transformação
        carregamento_transformado = transformar_carga_integracao(raw_data)

        if not carregamento_transformado:
             print("Falha na transformação dos dados.")

        return carregamento_transformado

    @strawberry.field
    def buscarCargaPorCodigosIntegracao(self, codigoFilial: str, numeroCarga: str, info: strawberry.Info) -> Optional[Carregamento]:
        """
        Busca dados de uma carga por código de filial e número da carga.
        Retorna o mesmo formato do buscarCarga.
        """

        # 1. Acessar o contexto para ler a requisição (e os headers)
        request = info.context.get("request")
        if not request:
            raise HTTPException(status_code=500, detail="Contexto da requisição não encontrado.")

        # 2. Ler os headers dinâmicos
        target_wsdl_url = request.headers.get("X-Target-WSDL")
        target_token = request.headers.get("X-Auth-Token")

        # 3. Validar os headers
        if not target_wsdl_url or not target_token:
            print("Erro: Headers X-Target-WSDL ou X-Auth-Token não fornecidos.")
            raise HTTPException(
                status_code=400,
                detail="Headers X-Target-WSDL e X-Auth-Token são obrigatórios."
            )

        print(f"[Query] buscando carga com filial {codigoFilial} e número {numeroCarga} em {target_wsdl_url}")

        # 4. Chamar o cliente SOAP
        raw_data = chamar_buscar_carga_por_codigos_integracao(
            codigo_filial=codigoFilial,
            numero_carga=numeroCarga,
            wsdl_url=target_wsdl_url,
            token=target_token
        )

        if not raw_data:
            print("Nenhum dado retornado do SOAP.")
            return None

        print(f"[Query] Recebidos {len(raw_data)} registros do SOAP. Transformando...")

        # 5. Chamar a função de transformação (mesma do buscarCarga)
        carregamento_transformado = transformar_carga_integracao(raw_data)

        if not carregamento_transformado:
             print("Falha na transformação dos dados.")

        return carregamento_transformado
