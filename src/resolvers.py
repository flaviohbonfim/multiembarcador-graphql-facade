# src/resolvers.py
import strawberry
from typing import Optional, List
from .models import Carregamento, DadosNotaFiscal, NotaFiscalDetalhe
from .soap_client import chamar_buscar_carga, chamar_buscar_carga_por_codigos_integracao, chamar_buscar_notas_fiscais, chamar_buscar_nota_fiscal_por_chave
from .transformation import transformar_carga_integracao, transformar_nota_fiscal, transformar_nota_fiscal_detalhe
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

    @strawberry.field
    def buscarNotasFiscaisVinculadas(
        self,
        protocoloCarga: str,
        info: strawberry.Info,
        inicio: Optional[int] = 0,
        limite: Optional[int] = 100
    ) -> Optional[List[DadosNotaFiscal]]:
        """
        Busca as Notas Fiscais vinculadas a um protocolo de carga.
        Usa o WSDL da NFe (endpoint e token via headers).
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

        print(f"[Query] buscando Notas Fiscais para protocolo {protocoloCarga} em {target_wsdl_url}")

        # 4. Chamar o cliente SOAP (nova função)
        raw_data = chamar_buscar_notas_fiscais(
            protocolo_carga=protocoloCarga,
            inicio=inicio,
            limite=limite,
            wsdl_url=target_wsdl_url,
            token=target_token
        )

        if raw_data is None:
            print("Nenhum dado retornado do SOAP (NFe).")
            return None # Retorna null em caso de erro na chamada

        if not raw_data:
            print("Nenhuma NF-e encontrada.")
            return [] # Retorna lista vazia se a consulta foi OK mas não achou nada

        print(f"[Query] Recebidos {len(raw_data)} registros de NF-e. Transformando...")

        # 5. Chamar a função de transformação (nova função)
        notas_transformadas = transformar_nota_fiscal(
            notas=raw_data,
            protocolo_carga_str=protocoloCarga
        )

        return notas_transformadas

    @strawberry.field
    def buscarNotaFiscalPorChave(
        self,
        chaveNFe: str,
        info: strawberry.Info
    ) -> Optional[NotaFiscalDetalhe]:
        """
        Busca o XML de uma Nota Fiscal específica pela chave.
        Usa o WSDL do CTe (endpoint e token via headers).
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

        print(f"[Query] buscando Detalhe da NF-e {chaveNFe} em {target_wsdl_url}")

        # 4. Chamar o cliente SOAP (nova função)
        raw_data = chamar_buscar_nota_fiscal_por_chave(
            chave_nfe=chaveNFe,
            wsdl_url=target_wsdl_url,
            token=target_token
        )

        if raw_data is None:
            print("Nenhum dado retornado do SOAP (CTe.BuscarNotaFiscal).")
            return None # Retorna null em caso de erro ou se não achou

        print(f"[Query] Recebido 1 registro de NF-e. Transformando...")

        # 5. Chamar a função de transformação (nova função)
        nota_transformada = transformar_nota_fiscal_detalhe(
            nota=raw_data
        )

        return nota_transformada
