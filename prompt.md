Crie um projeto Python chamado "transcriber" para transcrição local de vídeos usando faster-whisper. O projeto roda numa máquina com RTX 3060 12GB, Ubuntu/WSL2.

## Estrutura do projeto

transcriber/
├── transcriber/
│   ├── __init__.py
│   ├── cli.py            # Entry point CLI com argparse
│   ├── transcribe.py     # Core de transcrição
│   ├── formatter.py      # Formatadores de saída (srt, vtt, txt, json)
│   └── utils.py          # Helpers (extração de áudio, timestamps, progress)
├── pyproject.toml        # Config do projeto com dependências
├── README.md
└── .gitignore

## Dependências

- faster-whisper (CTranslate2 backend, roda 100% local, sem API key)
- ffmpeg-python (extração de áudio de vídeo)
- rich (progress bar e output bonito no terminal)

## CLI — Interface esperada

# Transcrição básica (detecta idioma automaticamente)
python -m transcriber video.mp4

# Forçar português
python -m transcriber video.mp4 --lang pt

# Gerar legenda SRT
python -m transcriber video.mp4 --lang pt --format srt -o legenda.srt

# Gerar VTT (compatível com web/HTML5 <track>)
python -m transcriber video.mp4 --lang pt --format vtt -o legenda.vtt

# Gerar JSON com timestamps (útil pra integrar com outros sistemas)
python -m transcriber video.mp4 --format json -o transcricao.json

# Gerar texto puro
python -m transcriber video.mp4 --format txt -o transcricao.txt

# Escolher modelo (default: large-v3-turbo)
python -m transcriber video.mp4 --model large-v3

# Processar pasta inteira de vídeos (batch)
python -m transcriber ./videos/ --lang pt --format srt

# Listar modelos disponíveis
python -m transcriber --list-models

## Argumentos CLI

- input (positional): arquivo de vídeo/áudio OU diretório para batch
- --lang / -l: código do idioma (pt, en, es, etc). Default: auto-detect
- --model / -m: modelo whisper. Default: large-v3-turbo. Opções: tiny, base, small, medium, large-v3, large-v3-turbo
- --format / -f: formato de saída. Default: txt. Opções: txt, srt, vtt, json
- --output / -o: arquivo de saída. Default: mesmo nome do input com extensão do formato
- --device: cuda ou cpu. Default: cuda
- --compute-type: float16, int8_float16, int8. Default: float16
- --beam-size: beam size para decodificação. Default: 5
- --vad / --no-vad: ativar/desativar VAD filter (Silero). Default: ativado
- --word-timestamps: incluir timestamps por palavra (útil pra karaokê/highlight)
- --list-models: lista modelos disponíveis com tamanho e VRAM estimada
- --verbose / -v: modo verboso com detalhes de cada segmento

## Requisitos técnicos

1. Transcrição:
   - Usar faster_whisper.WhisperModel
   - device="cuda", compute_type="float16" como defaults
   - VAD filter ativado por padrão (vad_filter=True) com min_silence_duration_ms=500
   - beam_size=5 por padrão
   - Suportar input de vídeo (mp4, mkv, avi, mov, webm) e áudio (mp3, wav, flac, ogg, m4a)

2. Formatadores de saída:
   - SRT: formato padrão com índice sequencial, timestamps HH:MM:SS,mmm
   - VTT: WebVTT com header "WEBVTT\n\n", timestamps HH:MM:SS.mmm
   - TXT: texto puro, um parágrafo por segmento, separado por quebra de linha
   - JSON: array de objetos {start, end, text, words?} com precisão de 2 casas decimais

3. Batch processing:
   - Quando input é diretório, processar todos os arquivos de vídeo/áudio encontrados
   - Gerar output com mesmo nome do arquivo original + extensão do formato
   - Mostrar progresso geral (arquivo X de Y) e progresso individual

4. UX no terminal:
   - Usar rich para progress bars e formatação
   - Mostrar info do modelo carregado (nome, device, compute type)
   - Mostrar duração do áudio detectada
   - Mostrar idioma detectado (quando auto-detect)
   - No final, mostrar tempo total de processamento e velocidade (ex: "45min de áudio em 38s — 71x realtime")

5. Tratamento de erros:
   - Verificar se ffmpeg está instalado no sistema
   - Verificar se CUDA está disponível quando device=cuda
   - Mensagem clara se arquivo não existe ou formato não suportado
   - Fallback pra CPU com aviso se CUDA falhar

## pyproject.toml

Usar pyproject.toml com:
- [project] com name, version, description, requires-python >= 3.10
- [project.scripts] com entry point: transcriber = "transcriber.cli:main"
- dependencies listadas

## README.md

README em português com:
- Descrição do projeto
- Pré-requisitos (Python 3.10+, ffmpeg, CUDA toolkit)
- Instalação (pip install -e .)
- Exemplos de uso
- Tabela de modelos com VRAM estimada
- Nota sobre privacidade (100% local, sem API key, sem envio de dados)
