"""Interface Streamlit do KartBot."""

from __future__ import annotations

import os
from dataclasses import asdict
from typing import Any

import requests
import streamlit as st

from dao import ProdutoDAO, ProdutoMercado, Transacao, TransacaoDAO


SYSTEM_PROMPT = (
    "Você é o KartBot, um consultor financeiro de equipes de kart. Use APENAS os "
    "preços médios do JSON e o histórico do CSV fornecidos. Se questionado sobre o "
    "custo de uma etapa, some a média de um jogo de pneus novo com as despesas de "
    "inscrição presentes no CSV."
)

DEFAULT_LLM_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_LLM_MODEL = "gpt-4o-mini"


def carregar_config_llm() -> tuple[str, str, str]:
    """Carrega configuracoes da API de LLM por variaveis de ambiente ou secrets."""
    api_url = str(
        st.secrets.get("LLM_API_URL", os.getenv("LLM_API_URL", DEFAULT_LLM_API_URL))
    )
    modelo = str(st.secrets.get("LLM_MODEL", os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)))
    api_key = str(
        st.secrets.get(
            "LLM_API_KEY",
            os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or "",
        )
    )

    return api_url, modelo, api_key


@st.cache_data(show_spinner=False)
def carregar_produtos() -> list[ProdutoMercado]:
    """Carrega os produtos de mercado via DAO."""
    return ProdutoDAO().listar_todos()


@st.cache_data(show_spinner=False)
def carregar_transacoes() -> list[Transacao]:
    """Carrega o historico financeiro via DAO."""
    return TransacaoDAO().listar_todas()


def calcular_total_inscricoes(transacoes: list[Transacao]) -> float:
    """Soma gastos de inscricao registrados no CSV."""
    total = 0.0

    for transacao in transacoes:
        texto = f"{transacao.categoria} {transacao.descricao}".casefold()
        if transacao.tipo == "saida" and "inscri" in texto:
            total += transacao.valor

    return round(total, 2)


def montar_contexto(produtos: list[ProdutoMercado], transacoes: list[Transacao]) -> str:
    """Monta o contexto financeiro entregue ao modelo."""
    produtos_payload = [asdict(produto) for produto in produtos]
    transacoes_payload = [
        {
            "data": transacao.data.isoformat(),
            "descricao": transacao.descricao,
            "categoria": transacao.categoria,
            "valor": transacao.valor,
            "tipo": transacao.tipo,
        }
        for transacao in transacoes
    ]
    total_inscricoes = calcular_total_inscricoes(transacoes)

    return (
        "Contexto autorizado para resposta:\n"
        f"Produtos do JSON: {produtos_payload}\n"
        f"Transacoes do CSV: {transacoes_payload}\n"
        f"Total de despesas de inscricao no CSV: {total_inscricoes:.2f}\n"
        "Nao use dados externos, estimativas livres ou conhecimento de mercado fora "
        "do contexto acima."
    )


def montar_mensagens_llm(
    contexto: str, historico: list[dict[str, str]], pergunta: str
) -> list[dict[str, str]]:
    """Cria a lista de mensagens enviada para a API de LLM."""
    mensagens = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": contexto},
    ]
    mensagens.extend(historico[-8:])
    mensagens.append({"role": "user", "content": pergunta})
    return mensagens


def chamar_llm(mensagens: list[dict[str, str]]) -> str:
    """Chama uma API de LLM compativel com Chat Completions."""
    api_url, modelo, api_key = carregar_config_llm()

    if not api_key:
        return (
            "Configure LLM_API_KEY ou OPENAI_API_KEY para ativar a resposta do modelo."
        )

    resposta = requests.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": modelo,
            "messages": mensagens,
            "temperature": 0.2,
        },
        timeout=45,
    )
    resposta.raise_for_status()

    payload: dict[str, Any] = resposta.json()
    return str(payload["choices"][0]["message"]["content"]).strip()


def inicializar_estado_chat() -> None:
    """Inicializa o historico de chat da sessao."""
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [
            {
                "role": "assistant",
                "content": "Olá, sou o KartBot. Posso analisar custos usando o JSON e o CSV do projeto.",
            }
        ]


def renderizar_sidebar(produtos: list[ProdutoMercado], transacoes: list[Transacao]) -> None:
    """Mostra um resumo do contexto carregado."""
    total_saidas = round(sum(item.valor for item in transacoes if item.tipo == "saida"), 2)
    total_inscricoes = calcular_total_inscricoes(transacoes)

    with st.sidebar:
        st.header("Contexto")
        st.metric("Produtos monitorados", len(produtos))
        st.metric("Transações no CSV", len(transacoes))
        st.metric("Gastos registrados", f"R$ {total_saidas:,.2f}")
        st.metric("Inscrições no CSV", f"R$ {total_inscricoes:,.2f}")
        st.caption("Fonte: data/produtos_financeiros.json e data/transacoes.csv")


def main() -> None:
    st.set_page_config(page_title="KartBot", page_icon="🏁", layout="centered")
    st.title("KartBot")

    produtos = carregar_produtos()
    transacoes = carregar_transacoes()
    contexto = montar_contexto(produtos, transacoes)

    renderizar_sidebar(produtos, transacoes)
    inicializar_estado_chat()

    for mensagem in st.session_state.mensagens:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    pergunta = st.chat_input("Pergunte sobre custos, pneus, inscrições ou manutenção")
    if not pergunta:
        return

    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    historico_llm = [
        mensagem
        for mensagem in st.session_state.mensagens[:-1]
        if mensagem["role"] in {"user", "assistant"}
    ]
    mensagens_llm = montar_mensagens_llm(contexto, historico_llm, pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Analisando os dados do KartBot..."):
            try:
                resposta = chamar_llm(mensagens_llm)
            except requests.RequestException as erro:
                resposta = f"Não consegui chamar a API de LLM: {erro}"

        st.markdown(resposta)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})


if __name__ == "__main__":
    main()
