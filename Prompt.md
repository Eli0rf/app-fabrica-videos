# Prompt: Fábrica de Vídeos Dark - Contexto Completo para IA

## Visão Geral do Projeto

Sistema autônomo de criação de vídeos de finanças com pipeline de 4 estágios, otimizado para rodar localmente em macOS. O sistema gera vídeos financeiros estilo "Shorts/Reels" a partir de dados de mercado em tempo real.

---

## Stack Tecnológica

| Camada | Tecnologia | Custo |
|--------|-----------|-------|
| **Frontend** | React 18 + Vite + TypeScript + Tailwind CSS + Recharts | Gratuito |
| **Backend** | Python 3.11+ com FastAPI + Uvicorn (assíncrono) | Gratuito |
| **Ingestão de Dados** | yfinance — notícias e cotações do mercado | Gratuito |
| **Voz/Locução** | edge-tts — voz realista pt-BR (Microsoft Edge) | Gratuito |
| **Imagem** | Pillow (PIL) — geração de gráficos visuais | Gratuito |
| **Renderização** | moviepy 2.x + ffmpeg — composição de vídeo | Gratuito |
| **Upload** | YouTube Data API v3 — OAuth 2.0 | Gratuito (quota) |

---
# Prompt: Fábrica de Vídeos Dark - Contexto Completo para IA

## Visão Geral do Projeto

Sistema autônomo de criação de vídeos de finanças com pipeline de 4 estágios, otimizado para rodar localmente em macOS. O sistema gera vídeos financeiros estilo "Shorts/Reels" a partir de dados de mercado em tempo real.

---
# Prompt: Fábrica de Vídeos Dark - Contexto Completo para IA

## Visão Geral do Projeto

Sistema autônomo de criação de vídeos de finanças com pipeline de 4 estágios, otimizado para rodar localmente em macOS. O sistema gera vídeos financeiros estilo "Shorts/Reels" a partir de dados de mercado em tempo real.

--- 

## Stack Tecnológica

| Camada | Tecnologia | Custo |
|--------|-----------|-------|
| **Frontend** | React 18 + Vite + TypeScript + Tailwind CSS + Recharts | Gratuito |
| **Backend** | Python 3.11+ com FastAPI + Uvicorn (assíncrono) | Gratuito |
| **Ingestão de Dados** | yfinance — notícias e cotações do mercado | Gratuito |
| **Voz/Locução** | edge-tts — voz realista pt-BR (Microsoft Edge) | Gratuito |
| **Imagem** | Pillow (PIL) — geração de gráficos visuais | Gratuito |
| **Renderização** | moviepy 2.x + ffmpeg — composição de vídeo | Gratuito |
```
```text
┌──────────────┐    ┌──────────────────┐    ┌─────────────────────┐    ┌──────────────┐
│  1. INGESTÃO │ -> │  2. IA: ROTEIRO    │ -> │  3. IMG: GRÁFICO   │ -> │ 4. RENDERIZ. │
│   (yfinance) │    │   E + VOZ          │    │   VISUAL (PIL)      │    │ (moviepy+ff) │
│              │    │   (edge-tts)       │    │                     │    │              │
│ Preço, var.  │    │ Roteiro auto +     │    │ PNG 1920x1080 com   │    │ MP4 final    │
│ Notícias     │    │ Locução MP3 +      │    │ tema dark + barras  │    | h264 + aac   │
│ Tickers      │    │ Legendas SRT       │    │ de volume           │    | + legendas   │
└──────────────┘    └──────────────────┘    └─────────────────────┘    └──────────────┘
```

---