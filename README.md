# overlay-em-massa

Aplica um overlay (moldura, marca d'água, legenda fixa, efeito) em **vários vídeos de uma vez**, no formato vertical 9:16 (1080×1920), pronto para TikTok, Reels e Shorts.

*Batch-apply a full-screen overlay to many videos at once (vertical 9:16, 1080×1920). English below.*

## O que ele faz

- Três posições de overlay: `BASE`, `CENTRO` e `TOPO`. Cada vídeo usa o overlay da pasta em que você o colocar.
- Aceita overlay em **imagem** (PNG/JPG/WEBP) ou **vídeo** (MOV/MP4), que fica repetindo em loop.
- Reconhece sozinho se o overlay tem **transparência** de verdade. Se não tiver, pergunta se o fundo é **preto** (modo "tela") ou **verde** (chroma key).
- Ajusta qualquer vídeo para 1080×1920 sem distorcer.
- Deixa escolher quais vídeos processar (`1,3,5`, `2-6` ou Enter para todos) e pula os que já estão prontos.

## Como usar

1. Instale o Python 3 e o FFmpeg. No Windows:
   ```
   winget install Python.Python.3.12
   winget install ffmpeg
   ```
2. Coloque os overlays na pasta `overlays/` com um destes nomes (o script usa o primeiro que encontrar):
   - `BASE OVERLAY.png` ou `BASE.png` ou `FUNDO @ BASE.mov`
   - a mesma coisa para `CENTRO` e `TOPO`
3. Rode uma vez para criar as pastas:
   ```
   python aplicar_overlay.py
   ```
4. Coloque os vídeos em `para_overlay/BASE`, `para_overlay/CENTRO` ou `para_overlay/TOPO`.
5. Rode de novo e escolha os vídeos. O resultado fica em `com_overlay/`.

Para mudar o tamanho final, altere `LARGURA, ALTURA` no começo do script.

---

## English

1. Install Python 3 and FFmpeg.
2. Put your overlays in `overlays/`, named `BASE.png`, `CENTRO.png`, `TOPO.png` (or `<POS> OVERLAY.png` / `FUNDO @ <POS>.mov`).
3. Run `python aplicar_overlay.py` once to create the folders.
4. Drop videos into `para_overlay/BASE`, `para_overlay/CENTRO` or `para_overlay/TOPO`.
5. Run it again and pick which videos to process. Output goes to `com_overlay/`.

Overlays with real transparency (alpha) are used as is. Without alpha, the script asks if the background is black (screen blend) or green (chroma key).

## Licença / License

MIT
