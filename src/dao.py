"""Camada DAO para acesso aos dados do projeto KartBot."""

from __future__ import annotations

import csv
import json
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal


BASE_DIR = Path(__file__).resolve().parents[1]
PRODUTOS_JSON = BASE_DIR / "data" / "produtos_financeiros.json"
TRANSACOES_CSV = BASE_DIR / "data" / "transacoes.csv"
TipoTransacao = Literal["entrada", "saida"]


@dataclass(frozen=True, slots=True)
class ProdutoMercado:
    """Representa um produto monitorado no mercado."""

    nome_produto: str
    preco_medio: float
    data_coleta: str


@dataclass(frozen=True, slots=True)
class Transacao:
    """Representa uma transacao financeira do piloto."""

    data: date
    descricao: str
    categoria: str
    valor: float
    tipo: TipoTransacao


class ProdutoDAO:
    """Abstrai a leitura dos produtos monitorados no arquivo JSON."""

    def __init__(self, caminho_arquivo: Path = PRODUTOS_JSON) -> None:
        self.caminho_arquivo = caminho_arquivo

    def listar_todos(self) -> list[ProdutoMercado]:
        """Retorna todos os produtos encontrados no JSON."""
        registros = self._ler_json()
        return [self._criar_produto(registro) for registro in registros]

    def buscar_por_nome(self, termo: str) -> list[ProdutoMercado]:
        """Busca produtos cujo nome contenha o termo informado."""
        termo_normalizado = self._normalizar_texto(termo)
        return [
            produto
            for produto in self.listar_todos()
            if termo_normalizado in self._normalizar_texto(produto.nome_produto)
        ]

    def _ler_json(self) -> list[dict[str, Any]]:
        if not self.caminho_arquivo.exists():
            return []

        with self.caminho_arquivo.open("r", encoding="utf-8") as arquivo:
            dados: Any = json.load(arquivo)

        if not isinstance(dados, list):
            raise ValueError("O arquivo de produtos deve conter uma lista JSON.")

        registros: list[dict[str, Any]] = []
        for item in dados:
            if not isinstance(item, dict):
                raise ValueError("Todos os itens do arquivo de produtos devem ser objetos JSON.")
            registros.append(item)

        return registros

    @staticmethod
    def _criar_produto(registro: dict[str, Any]) -> ProdutoMercado:
        nome = str(registro.get("nome_produto") or registro.get("nome") or "")
        preco = registro.get("preco_medio", registro.get("aporte_minimo", 0.0))
        data_coleta = str(registro.get("data_coleta") or "")

        return ProdutoMercado(
            nome_produto=nome,
            preco_medio=float(preco),
            data_coleta=data_coleta,
        )

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        texto_ascii = unicodedata.normalize("NFKD", texto)
        texto_sem_acentos = texto_ascii.encode("ascii", "ignore").decode("ascii")
        return texto_sem_acentos.casefold()


class TransacaoDAO:
    """Abstrai a leitura do historico de gastos no arquivo CSV."""

    def __init__(self, caminho_arquivo: Path = TRANSACOES_CSV) -> None:
        self.caminho_arquivo = caminho_arquivo

    def listar_todas(self) -> list[Transacao]:
        """Retorna todas as transacoes do CSV."""
        if not self.caminho_arquivo.exists():
            return []

        with self.caminho_arquivo.open("r", encoding="utf-8", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            return [self._criar_transacao(linha) for linha in leitor]

    def get_total_gasto_mes(self, mes: int | str) -> float:
        """Soma saidas de um mes.

        Aceita `mes` como inteiro de 1 a 12 ou string no formato `YYYY-MM`.
        """
        transacoes = self.listar_todas()

        if isinstance(mes, int):
            if not 1 <= mes <= 12:
                raise ValueError("O mes inteiro deve estar entre 1 e 12.")
            filtradas = [item for item in transacoes if item.data.month == mes]
        else:
            ano_mes = self._validar_ano_mes(mes)
            filtradas = [
                item for item in transacoes if item.data.strftime("%Y-%m") == ano_mes
            ]

        total = sum(item.valor for item in filtradas if item.tipo == "saida")
        return round(total, 2)

    def get_historico_manutencao(self) -> list[Transacao]:
        """Retorna transacoes ligadas a manutencao do kart."""
        historico: list[Transacao] = []

        for transacao in self.listar_todas():
            categoria = self._normalizar_texto(transacao.categoria)
            descricao = self._normalizar_texto(transacao.descricao)
            if "manutencao" in categoria or "manutencao" in descricao:
                historico.append(transacao)

        return historico

    @staticmethod
    def _criar_transacao(linha: dict[str, str]) -> Transacao:
        tipo = linha["tipo"].strip().lower()
        if tipo not in ("entrada", "saida"):
            raise ValueError(f"Tipo de transacao invalido: {tipo}")

        return Transacao(
            data=date.fromisoformat(linha["data"]),
            descricao=linha["descricao"].strip(),
            categoria=linha["categoria"].strip(),
            valor=float(linha["valor"]),
            tipo=tipo,
        )

    @staticmethod
    def _validar_ano_mes(valor: str) -> str:
        try:
            data_referencia = date.fromisoformat(f"{valor}-01")
        except ValueError as erro:
            raise ValueError("Use o mes no formato 'YYYY-MM'.") from erro

        return data_referencia.strftime("%Y-%m")

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        texto_ascii = unicodedata.normalize("NFKD", texto)
        texto_sem_acentos = texto_ascii.encode("ascii", "ignore").decode("ascii")
        return texto_sem_acentos.casefold()
