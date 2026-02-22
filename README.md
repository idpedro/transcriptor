# Transcriber

Transcrição local de vídeos e áudios usando [faster-whisper](https://github.com/SYSTRAN/faster-whisper). Roda 100% na sua máquina, sem API key, sem envio de dados para nuvem.

## Pré-requisitos

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes e ambientes)
- [ffmpeg](https://ffmpeg.org/) instalado no sistema
- Driver NVIDIA + CUDA Toolkit + cuDNN (para GPU)

### Instalando dependências do sistema

**Arch/Manjaro:**

```bash
sudo pacman -S ffmpeg cuda cudnn
```

**Ubuntu/Debian:**

```bash
sudo apt install ffmpeg nvidia-cuda-toolkit libcudnn8
```

### Instalando o uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup de desenvolvimento

```bash
# Clonar o repositório
git clone <repo-url>
cd transcriber

# Criar venv e instalar dependências (uv faz tudo automaticamente)
uv sync

# Rodar o projeto
uv run python -m transcriber --list-models
```

O `uv sync` cria o `.venv`, resolve e instala todas as dependências do `pyproject.toml` automaticamente.

## Uso

```bash
# Transcrição básica (detecta idioma automaticamente)
uv run python -m transcriber video.mp4

# Forçar português
uv run python -m transcriber video.mp4 --lang pt

# Gerar legenda SRT
uv run python -m transcriber video.mp4 --lang pt --format srt -o legenda.srt

# Gerar VTT (compatível com HTML5 <track>)
uv run python -m transcriber video.mp4 --lang pt --format vtt -o legenda.vtt

# Gerar JSON com timestamps
uv run python -m transcriber video.mp4 --format json -o transcricao.json

# Gerar texto puro
uv run python -m transcriber video.mp4 --format txt -o transcricao.txt

# Escolher modelo
uv run python -m transcriber video.mp4 --model large-v3

# Processar pasta inteira (batch)
uv run python -m transcriber ./videos/ --lang pt --format srt

# Timestamps por palavra (útil para karaokê)
uv run python -m transcriber video.mp4 --word-timestamps --format json

# Listar modelos disponíveis
uv run python -m transcriber --list-models

# Usar CPU ao invés de GPU
uv run python -m transcriber video.mp4 --device cpu --compute-type int8
```

## Modelos

| Modelo | Tamanho | VRAM estimada | Observação |
|--------|---------|---------------|------------|
| tiny | ~75 MB | ~1 GB | Mais rápido, menos preciso |
| base | ~145 MB | ~1 GB | |
| small | ~488 MB | ~2 GB | |
| medium | ~1.5 GB | ~5 GB | |
| large-v3 | ~3.1 GB | ~10 GB | Mais preciso |
| large-v3-turbo | ~1.6 GB | ~6 GB | **Default** — boa precisao com velocidade |

## Formatos de saída

- **txt** — Texto puro, um parágrafo por segmento
- **srt** — SubRip, formato padrão de legenda
- **vtt** — WebVTT, compatível com HTML5 `<track>`
- **json** — Array de objetos com timestamps (útil para integração)

## Argumentos

| Argumento | Descrição | Default |
|-----------|-----------|---------|
| `input` | Arquivo de vídeo/áudio ou diretório | — |
| `--lang`, `-l` | Código do idioma (pt, en, es...) | auto-detect |
| `--model`, `-m` | Modelo whisper | large-v3-turbo |
| `--format`, `-f` | Formato de saída (txt, srt, vtt, json) | txt |
| `--output`, `-o` | Arquivo de saída | mesmo nome + extensão |
| `--device` | cuda ou cpu | cuda |
| `--compute-type` | float16, int8_float16, int8 | float16 |
| `--beam-size` | Beam size para decodificação | 5 |
| `--vad` / `--no-vad` | VAD filter (Silero) | ativado |
| `--word-timestamps` | Timestamps por palavra | desativado |
| `--list-models` | Lista modelos disponíveis | — |
| `--verbose`, `-v` | Modo verboso | desativado |

## Troubleshooting

### "CUDA não disponível. Usando CPU como fallback."

Instale o CUDA toolkit e cuDNN do sistema:

```bash
# Arch/Manjaro
sudo pacman -S cuda cudnn
```

Verifique se o driver NVIDIA está funcionando:

```bash
nvidia-smi
```

### "Library libcublas.so.12 is not found or cannot be loaded"

Isso acontece quando a versão do CUDA do sistema (ex: 13.x) é mais recente que a versão esperada pelo CTranslate2 (12.x). O projeto já inclui as libs CUDA 12 via pip (`nvidia-cublas-cu12`, `nvidia-cudnn-cu12`) e as pré-carrega automaticamente. Se mesmo assim der erro, verifique se o `uv sync` instalou esses pacotes:

```bash
uv run python -c "import nvidia.cublas; print('cublas OK')"
uv run python -c "import nvidia.cudnn; print('cudnn OK')"
```

### Legendas SRT não aparecem no VLC

O VLC pode ter problemas com codificação de legendas. Duas soluções:

1. **No VLC:** vá em Ferramentas > Preferências > Legendas/OSD e mude a codificação padrão para **UTF-8**.

2. **Use o mpv** (recomendado, funciona sem configuração):

```bash
sudo pacman -S mpv
mpv --sub-file="legenda.srt" video.mp4
```

## Privacidade

Este projeto roda 100% local. Nenhum dado é enviado para servidores externos. Não requer API key nem conta em nenhum serviço. Seus áudios e transcrições permanecem na sua máquina.
