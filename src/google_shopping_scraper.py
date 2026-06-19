"""Scraper de precos do Google Shopping usando Selenium e Regex.

O script busca produtos de kart no Google Shopping, extrai os textos dos
primeiros resultados e calcula o preco medio encontrado em cada busca.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Iterable
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


PRODUTOS = [
    "Capacete Arai SK-6",
    "Capacete Bell KC7",
    "Viseira Bell",
    "Spoiler aerodinâmico kart",
    "Pneu de kart MG vermelho",
]

BASE_DIR = Path(__file__).resolve().parents[1]
ARQUIVO_SAIDA = BASE_DIR / "data" / "produtos_financeiros.json"
GOOGLE_SHOPPING_URL = "https://www.google.com/search?tbm=shop&hl=pt-BR&gl=br&q={query}"
PRICE_PATTERN = re.compile(
    r"(?:R\$\s*)?(?<!\w)(\d{1,3}(?:[.\s]\d{3})*(?:,\d{2})|\d+(?:,\d{2})|\d+(?:\.\d{2}))"
)


@dataclass(frozen=True)
class ProdutoColetado:
    nome_produto: str
    preco_medio: float
    data_coleta: str


def configurar_driver() -> webdriver.Chrome:
    """Configura o Chrome WebDriver em modo headless."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--lang=pt-BR")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )

    return webdriver.Chrome(options=options)


def aceitar_cookies_se_aparecer(driver: webdriver.Chrome) -> None:
    """Clica em um botao de consentimento quando ele aparece."""
    textos_botoes = ("Aceitar tudo", "Concordo", "I agree", "Accept all")

    for texto in textos_botoes:
        try:
            botao = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f"//button[.//span[contains(., '{texto}')]] | //button[contains(., '{texto}')]",
                    )
                )
            )
            botao.click()
            time.sleep(1)
            return
        except TimeoutException:
            continue


def buscar_textos_google_shopping(
    driver: webdriver.Chrome, nome_produto: str, limite: int = 5
) -> list[str]:
    """Busca um produto no Google Shopping e retorna textos dos primeiros resultados."""
    url = GOOGLE_SHOPPING_URL.format(query=quote_plus(nome_produto))
    driver.get(url)
    aceitar_cookies_se_aparecer(driver)

    seletores_resultado = [
        "div.sh-dgr__content",
        "div[data-docid]",
        "div.i0X6df",
        "div.sh-dlr__list-result",
        "div.mnIHsc",
    ]

    wait = WebDriverWait(driver, 12)
    ultimo_erro: Exception | None = None

    for seletor in seletores_resultado:
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, seletor)))
            elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
            textos = [elemento.text.strip() for elemento in elementos if elemento.text.strip()]
            if textos:
                return textos[:limite]
        except TimeoutException as erro:
            ultimo_erro = erro

    if ultimo_erro:
        raise TimeoutException(f"Nenhum resultado encontrado para '{nome_produto}'.")

    return []


def converter_valor_para_float(valor: str) -> float:
    """Converte valores monetarios como 'R$ 1.234,56' ou '199.99' para float."""
    numero = re.sub(r"[^\d,.\s]", "", valor).strip().replace(" ", "")

    if "," in numero and "." in numero:
        if numero.rfind(",") > numero.rfind("."):
            numero = numero.replace(".", "").replace(",", ".")
        else:
            numero = numero.replace(",", "")
    elif "," in numero:
        numero = numero.replace(".", "").replace(",", ".")

    return float(numero)


def extrair_precos(textos_resultados: Iterable[str]) -> list[float]:
    """Extrai todos os valores monetarios encontrados nos textos dos resultados."""
    precos: list[float] = []

    for texto in textos_resultados:
        for match in PRICE_PATTERN.finditer(texto):
            try:
                precos.append(converter_valor_para_float(match.group(0)))
            except ValueError:
                continue

    return precos


def calcular_preco_medio(precos: list[float]) -> float:
    """Calcula a media de preco arredondada para duas casas decimais."""
    if not precos:
        return 0.0

    return round(mean(precos), 2)


def salvar_resultados(resultados: list[ProdutoColetado], arquivo_saida: Path) -> None:
    """Salva a lista de resultados no arquivo JSON definido."""
    arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "nome_produto": item.nome_produto,
            "preco_medio": item.preco_medio,
            "data_coleta": item.data_coleta,
        }
        for item in resultados
    ]

    arquivo_saida.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def coletar_precos() -> list[ProdutoColetado]:
    """Executa a coleta para todos os produtos configurados."""
    resultados: list[ProdutoColetado] = []
    data_coleta = datetime.now().isoformat(timespec="seconds")
    driver = configurar_driver()

    try:
        for produto in PRODUTOS:
            print(f"Buscando: {produto}")
            textos_resultados = buscar_textos_google_shopping(driver, produto, limite=5)
            precos = extrair_precos(textos_resultados)
            preco_medio = calcular_preco_medio(precos)
            resultados.append(
                ProdutoColetado(
                    nome_produto=produto,
                    preco_medio=preco_medio,
                    data_coleta=data_coleta,
                )
            )
            print(f"  Precos encontrados: {precos}")
            print(f"  Preco medio: R$ {preco_medio:.2f}")
    finally:
        driver.quit()

    return resultados


def main() -> None:
    resultados = coletar_precos()
    salvar_resultados(resultados, ARQUIVO_SAIDA)
    print(f"Resultados salvos em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
