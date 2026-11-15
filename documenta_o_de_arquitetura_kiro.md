# Especificação Técnica: Automação de Canal Dark de Finanças

## 1. Visão Geral do Projeto
Desenvolver uma aplicação local (híbrida Web/Desktop) para automação ponta a ponta de vídeos estilo "Shorts/Reels" para um canal dark de finanças. O sistema fará ingestão de dados, geração de roteiro via LLM, síntese de voz, geração de assets visuais e renderização final em vídeo.

## 2. Stack Tecnológico (Obrigatório)
*   **Backend:** Python 3.10+ com FastAPI.
*   **Banco de Dados:** SQLite (local, via SQLAlchemy) para controle de status dos vídeos e logs.
*   **Frontend:** React.js (Vite) com Tailwind CSS.
*   **Processamento Assíncrono:** Celery + Redis (ou `BackgroundTasks` nativo do FastAPI para simplificar o deploy local inicial).

## 3. Pipeline de Processamento (A Esteira)
O agente deve implementar as seguintes etapas de forma modular (uma classe/serviço para cada):
1.  **Data Ingestion:** Módulo usando a biblioteca `yfinance` para buscar altas/baixas do dia e feed RSS do Yahoo Finance.
2.  **Roteirização:** Integração com Groq API (modelo Llama 3) para gerar roteiro em formato JSON (coluna voz / coluna visual). O prompt do sistema deve focar em retenção e scripts curtos (60 segundos).
3.  **Voz:** Utilizar a biblioteca `edge-tts` (Python) para gerar o áudio em português (pt-BR-AntonioNeural ou similar) a partir do texto.
4.  **Imagens/Assets:** Módulo de geração local. Deixar um script preparado para invocar Stable Diffusion localmente via `diffusers` (HuggingFace) ou Ollama, gerando imagens e removendo o fundo (pode usar a lib `rembg`).
5.  **Renderização de Vídeo:** Utilizar `moviepy` para juntar áudio, imagens (animadas com zoom/bounce) e gerar as legendas dinâmicas no centro da tela sincronizadas com o áudio.

## 4. UI/UX: A "Fábrica de Vídeos"
O Frontend deve ter duas telas principais:

**A. Tela Principal (A Fábrica)**
*   A interface deve carregar a imagem estática `image_e618bb.jpg` ocupando a área central/direita.
*   **Metáfora Visual:** Sobrepor a imagem com elementos HTML absolutos (`divs` circulares ou indicadores LED neon).
    *   *Base da fábrica:* LED de Ingestão de Dados.
    *   *Meio da fábrica:* LEDs de Roteiro e Voz.
    *   *Topo:* LED de Renderização.
*   **Comportamento:** O Kiro deve usar WebSockets ou Polling (a cada 3s) para buscar o status das `Tasks` no FastAPI. Conforme o vídeo avança, a luz de cada setor muda de Desligada (Cinza) -> Processando (Amarelo Piscante) -> Concluído (Verde).
*   **Tratamento de Erro:** Se uma etapa falhar, o LED do setor específico pisca em VERMELHO. Um modal de log deve poder ser aberto ao clicar no LED vermelho.

**B. Painel Lateral / Dashboard**
*   Menu para alternar entre "Modo Manual" (aguarda aprovação humana antes de renderizar) e "Modo Automático" (cron job posta direto).
*   Input para "Forçar Criação" de um vídeo com tema específico.
*   Dashboard exibindo dados da biblioteca `google-api-python-client` (YouTube Data API v3): Vídeos postados, visualizações totais e status de conexão. O app deve ler o `client_secrets.json` na raiz do projeto.

## 5. Regras Críticas e Prevenção de Falhas (Atenção Agente Kiro)
1.  **Não bloqueie o Event Loop:** A renderização de vídeo no `moviepy` é extremamente pesada. Ela *nunca* deve rodar na thread principal do FastAPI. Use filas de background.
2.  **Modularidade Absoluta:** Se o módulo de `rembg` (remoção de fundo) falhar, o sistema deve continuar e usar a imagem com fundo como fallback. Se o `yfinance` falhar por falta de internet, o sistema deve registrar o erro no SQLite e parar a esteira graciosamente, sem derrubar a API.
3.  **Paths Multiplataforma:** Use `os.path.join` ou `pathlib` para todos os caminhos de arquivos. O ambiente base é macOS, arquivos gerados devem ir para uma pasta `output/` na raiz.