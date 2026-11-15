"""
Servico de Ingestao de Dados - Estagio 1 do Pipeline.
Usa yfinance para buscar noticias, tickers e dados de mercado do dia.
"""

import yfinance as yf
from loguru import logger
from typing import Optional
from datetime import datetime
import json

from models.schemas import TickerData


# Tickers padrao do mercado brasileiro e americano
DEFAULT_TICKERS = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA",
    "ABEV3.SA", "B3SA3.SA", "MGLU3.SA", "HYPE3.SA",
    "^BVSP", "^GSPC", "BTC-USD", "ETH-USD",
]


async def fetch_ticker_data(ticker: str) -> TickerData:
    """
    Busca dados completos de um ticker especifico.
    Inclui preco atual, variacao, volume, noticias e indicadores fundamentais.
    Trata erros de rede/API do yfinance graciosamente.
    """
    logger.info(f"[Ingestao] Buscando dados para ticker: {ticker}")
    try:
        yf_ticker = yf.Ticker(ticker)

        # info pode falhar com JSONDecodeError se Yahoo bloquear o request
        try:
            info = yf_ticker.info or {}
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"[Ingestao] Erro ao obter info de {ticker}: {e}")
            info = {}

        history = yf_ticker.history(period="2d")

        # Preço atual e variação
        if len(history) >= 2:
            current_price = float(history["Close"].iloc[-1])
            previous_price = float(history["Close"].iloc[-2])
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100 if previous_price else 0.0
        elif len(history) == 1:
            current_price = float(history["Close"].iloc[-1])
            change = 0.0
            change_percent = 0.0
        else:
            current_price = float(info.get("currentPrice", 0.0))
            change = 0.0
            change_percent = 0.0

        volume = int(history["Volume"].iloc[-1]) if len(history) > 0 and "Volume" in history else None

        # Indicadores fundamentais
        pe_ratio = info.get("trailingPE") or info.get("forwardPE")
        market_cap = info.get("marketCap")
        debt_to_equity = info.get("debtToEquity")
        dividend_yield = info.get("dividendYield")
        fifty_two_week_high = info.get("fiftyTwoWeekHigh")
        fifty_two_week_low = info.get("fiftyTwoWeekLow")
        revenue = info.get("totalRevenue")
        net_income = info.get("netIncomeToCommon")

        # Notícias relacionadas
        news_raw = []
        try:
            news_raw = yf_ticker.news or []
        except Exception as e:
            logger.warning(f"[Ingestão] Não foi possível obter notícias para {ticker}: {e}")

        news = [
            {
                "title": item.get("title", ""),
                "publisher": item.get("publisher", ""),
                "published": item.get("providerPublishTime", 0),
                "link": item.get("link", ""),
                "summary": item.get("summary", "")[:200] if item.get("summary") else "",
            }
            for item in news_raw[:5]  # Últimas 5 notícias
        ]

        ticker_data = TickerData(
            symbol=ticker,
            name=info.get("longName", info.get("shortName", ticker)),
            price=round(current_price, 2),
            change=round(change, 2),
            change_percent=round(change_percent, 2),
            volume=volume,
            news=news,
            pe_ratio=pe_ratio,
            market_cap=market_cap,
            debt_to_equity=debt_to_equity,
            dividend_yield=dividend_yield,
            fifty_two_week_high=fifty_two_week_high,
            fifty_two_week_low=fifty_two_week_low,
            revenue=revenue,
            net_income=net_income,
        )

        logger.info(
            f"[Ingestão] {ticker}: preço={current_price}, variação={change_percent}%, "
            f"PE={pe_ratio}, notícias={len(news)}"
        )
        return ticker_data

    except Exception as e:
        logger.error(f"[Ingestão] Erro ao buscar dados de {ticker}: {e}")
        raise


async def fetch_market_overview() -> list[dict]:
    """
    Busca uma visão geral do mercado com os tickers padrão.
    Retorna uma lista de resumos para alimentar o dashboard.
    """
    logger.info("[Ingestão] Buscando visão geral do mercado")
    results = []
    for ticker in DEFAULT_TICKERS:
        try:
            data = await fetch_ticker_data(ticker)
            results.append({
                "symbol": data.symbol,
                "name": data.name,
                "price": data.price,
                "change_percent": data.change_percent,
                "news_count": len(data.news),
            })
        except Exception as e:
            logger.warning(f"[Ingestão] Falha ao processar {ticker}: {e}")
            results.append({
                "symbol": ticker,
                "name": ticker,
                "price": 0.0,
                "change_percent": 0.0,
                "news_count": 0,
                "error": str(e),
            })
    return results


async def fetch_trending_topics() -> list[dict]:
    """
    Busca tópicos em alta baseados nos movimentos de mercado.
    Identifica os ativos com maior variação percentual do dia.
    """
    logger.info("[Ingestão] Buscando tópicos em alta")
    overview = await fetch_market_overview()

    # Ordenar por variação absoluta
    trending = sorted(
        overview,
        key=lambda x: abs(x.get("change_percent", 0)),
        reverse=True,
    )

    return [
        {
            "topic": item["name"],
            "ticker": item["symbol"],
            "trend_score": abs(item.get("change_percent", 0)),
            "change_percent": item.get("change_percent", 0),
            "direction": "alta" if item.get("change_percent", 0) >= 0 else "baixa",
        }
        for item in trending[:6]
    ]

# A função foi movida para services/script_service.py

