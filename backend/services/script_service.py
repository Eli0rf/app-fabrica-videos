"""
Serviço de Geração de Roteiros - Estágio 2 do Pipeline.
Absorve a inteligência de finanças analíticas (finance-skills):
Estrutura profissional: Hook -> Métricas -> Análise -> Conclusão.
"""

from typing import Optional
from backend.models.schemas import TickerData
from loguru import logger

# Constantes de configuração
CAMBICO_ESTIMADO = 5.5  # Estimativa de cotação do dólar (apenas para referência)


def _format_percentual(valor: Optional[float], com_sinal: bool = True) -> str:
    """Formata um percentual com sinal opcional."""
    if valor is None:
        return "não informado"
    sinal = "+" if (com_sinal and valor >= 0) else ""
    return f"{sinal}{valor:.2f}%"


def _format_int_commas(valor: Optional[int]) -> str:
    """Formata um inteiro com separador de milhar."""
    if valor is None:
        return "não informado"
    return f"{valor:,}"


def _format_float2(valor: Optional[float]) -> str:
    """Formata um float com duas casas decimais."""
    if valor is None:
        return "não informado"
    return f"{valor:.2f}"


def _analise_sentimento(news_titles: list) -> str:
    """Retorna uma análise básica do sentimento das últimas notícias."""
    if not news_titles:
        return "não há notícias recentes"
    positives = ["alt", "super", "positivo", "crescimento", "reserva", "aumento", "record"]
    negatives = ["queda", "desconto", "inflação", "dívida", "crise", "perda"]
    texto = " ".join(news_titles).lower()
    pos_count = sum(1 for w in positives if w in texto)
    neg_count = sum(1 for w in negatives if w in texto)
    if pos_count > neg_count:
        return "com tom mais otimista para investidores"
    elif neg_count > pos_count:
        return "com tom mais pessimista para investidores"
    return "sem direção clara de optimismo ou pessimismo"


def generate_structured_script(ticker_data: TickerData, topic: Optional[str] = None) -> str:
    """
    Gera um roteiro completo para vídeo, seguindo a estrutura:
    Hook -> Dados de mercado -> Métricas fundamentais -> Notícias -> Conclusão/CTA.
    """
    # Hooks
    direction = "alta" if ticker_data.change_percent >= 0 else "queda"
    emoji = "📈" if ticker_data.change_percent >= 0 else "📉"
    sentiment = _analise_sentimento([n["title"] for n in ticker_data.news])

    hook = (
        f"Atenção, investidores! {emoji} O mercado não para e hoje o destaque é "
        f"{ticker_data.name.upper()} ({ticker_data.symbol}). "
    )

    # Parte 1: Dados de Mercado
    market_part = (
        f"No momento, o ativo está negociando a R$ {ticker_data.price:,.2f}, "
        f"em uma variação de {_format_percentual(ticker_data.change_percent)}. "
        f"O volume de negociação foi de {_format_int_commas(ticker_data.volume)} unidades, "
        f"indicando {(f'intensa' if ticker_data.volume and ticker_data.volume > 1000000 else 'moderada')} atuação do mercado. "
    )

    # Parte 2: Métricas Fundamentais
    fundamentals = []
    if ticker_data.pe_ratio:
        fundamentals.append(
            f"O P/E atual está em {_format_float2(ticker_data.pe_ratio)}x, "
            f"indicando {(f'valorização' if ticker_data.pe_ratio < 15 else 'aposentadoria de risco')} do ciclo de rentabilidade."
        )

    if ticker_data.market_cap:
        fundamentals.append(
            f"A capitalização de mercado fica em US$ {ticker_data.market_cap / 1e9:,.2f} bilhões."
        )

    if ticker_data.dividend_yield:
        fundamentals.append(
            f"O dividend yield está em {_format_percentual(ticker_data.dividend_yield * 100, com_sinal=False)}, "
            f"representando um retorno direto aos investidores."
        )

    if ticker_data.debt_to_equity is not None:
        debt_status = "consolidada" if ticker_data.debt_to_equity < 1.0 else "elevada"
        fundamentals.append(
            f"A relação dívida/equity situa-se em {_format_float2(ticker_data.debt_to_equity)}x, "
            f"sinalizando um nível de {debt_status} de endividamento."
        )

    if (
        ticker_data.fifty_two_week_high
        and ticker_data.fifty_two_week_low
    ):
        fundamentals.append(
            f"O ativo está negociando entre R$ {ticker_data.fifty_two_week_low:,.2f} e "
            f"R$ {ticker_data.fifty_two_week_high:,.2f} nos últimos 52 semanas."
        )

    if ticker_data.revenue and ticker_data.net_income:
        fundamentals.append(
            f"Os últimos dados apontam para receita líquida de R$ {ticker_data.revenue:,.2f} "
            f"e lucro líquido de R$ {ticker_data.net_income:,.2f}."
        )

    fundamentals_text = " ".join(fundamentals)

    # Parte 3: Notícias recentes
    news_part = ""
    if ticker_data.news:
        top_news = ticker_data.news[0]
        news_part = (
            f"Nas últimas notícias, destaca-se: \"{top_news['title']}\". "
            f"{sentiment}"
        )

    # Parte 4: Tópico especial (se informado)
    topic_part = f"E, dentro do escopo de {topic}, o cenário ganha ainda mais destaque para a sua decisão." if topic else ""

    # Parte 5: Conclusão e CTA
    conclusion = (
        "Em suma, o ativo demonstra {} e está se comportando de maneira {}. "
        "Aqui no canal, não damos recomendação de compra ou venda — o investidor deve analisar a própria carteira. "
        "Gostou dessa análise? Deixe seu comentário, se inscreva para mais conteúdos e garanta acesso à análise detalhada. Até a próxima!"
    ).format(
        "uma movimentação de alta" if ticker_data.change_percent >= 0 else "uma movimentação de baixa",
        "otimismo" if ticker_data.change_percent >= 0 else "atenção",
    )

    script = (
        f"{hook}\n\n"
        f"{market_part}\n\n"
        f"Indicadores de base: {fundamentals_text}. {news_part}\n\n"
        f"{topic_part}\n\n"
        f"{conclusion}"
    )

    logger.info(f"[Script] Roteiro gerado para {ticker_data.symbol} com {'notícias' if ticker_data.news else 'sem notícias'}")
    return script

