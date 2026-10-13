import os
import shutil
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))

# Pasta onde estão os overlays (tela cheia) de cada posição
PASTA_OVERLAYS = os.path.join(AQUI, "overlays")

# Para cada posição, o script testa estes arquivos na ordem e usa o primeiro
# que tiver transparência de verdade. Se nenhum tiver, usa o primeiro que existir.
POSICOES = ["BASE", "CENTRO", "TOPO"]
CANDIDATOS = [
    "{pos} OVERLAY.png",
    "{pos}.png",
    "FUNDO @ {pos}.mov",
]

# Você coloca cada vídeo na subpasta da posição desejada: BASE, CENTRO ou TOPO
ENTRADA = os.path.join(AQUI, "para_overlay")
SAIDA = os.path.join(AQUI, "com_overlay")

# Tamanho final (9:16 em pé, Full HD)
LARGURA, ALTURA = 1080, 1920

EXTENSOES = (".mp4", ".mov", ".mkv", ".webm")
IMAGENS = (".png", ".jpg", ".jpeg", ".webp")
ALFA = ("yuva", "rgba", "bgra", "argb", "abgr", "gbrap", "ya8", "ya16")


def interpretar(texto, total):
    """Aceita: todos | 1,3,5 | 2-6 | 1,4-8"""
    texto = texto.strip().lower()
    if texto in ("", "todos", "t", "all"):
        return list(range(total))
    indices = set()
    for parte in texto.split(","):
        parte = parte.strip()
        if not parte:
            continue
        if "-" in parte:
            a, b = parte.split("-")
            indices.update(range(int(a) - 1, int(b)))
        else:
            indices.add(int(parte) - 1)
    return sorted(i for i in indices if 0 <= i < total)


def destino_de(nome):
    return os.path.join(SAIDA, os.path.splitext(nome)[0] + ".mp4")


def tem_alfa(arquivo):
    """Confere se o arquivo guarda transparência de verdade."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=pix_fmt", "-of", "csv=p=0", arquivo],
        capture_output=True, text=True,
    )
    pix = r.stdout.strip().lower()
    return any(k in pix for k in ALFA), pix


def escolher_overlay(pos):
    """Devolve (arquivo, tem_alfa, pix_fmt) ou None se não achar nenhum."""
    existentes = []
    for modelo in CANDIDATOS:
        caminho = os.path.join(PASTA_OVERLAYS, modelo.format(pos=pos))
        if os.path.isfile(caminho):
            alfa, pix = tem_alfa(caminho)
            if alfa:
                return caminho, True, pix
            existentes.append((caminho, False, pix))
    return existentes[0] if existentes else None


def entrada_overlay(arquivo):
    """Imagem fica parada e vale o vídeo todo; vídeo repete em loop."""
    if arquivo.lower().endswith(IMAGENS):
        return ["-loop", "1", "-i", arquivo]
    return ["-stream_loop", "-1", "-i", arquivo]


def montar_filtro(modo):
    base = (
        f"[0:v]scale={LARGURA}:{ALTURA}:force_original_aspect_ratio=decrease,"
        f"pad={LARGURA}:{ALTURA}:(ow-iw)/2:(oh-ih)/2"
    )
    if modo == "alfa":
        return (
            f"{base}[b];[1:v]scale={LARGURA}:{ALTURA},format=rgba[o];"
            "[b][o]overlay=0:0:shortest=1,format=yuv420p[v]"
        )
    if modo == "preto":
        # "Tela": o preto some e o resto clareia o vídeo por baixo
        return (
            f"{base},format=gbrp[b];[1:v]scale={LARGURA}:{ALTURA},format=gbrp[o];"
            "[b][o]blend=all_mode=screen:shortest=1,format=yuv420p[v]"
        )
    # verde
    return (
        f"{base}[b];[1:v]scale={LARGURA}:{ALTURA},format=rgba,"
        "colorkey=0x00FF00:0.3:0.1[o];"
        "[b][o]overlay=0:0:shortest=1,format=yuv420p[v]"
    )


def main():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("FFmpeg não encontrado. Instale com: winget install ffmpeg")
        print("Depois feche e abra este programa de novo.")
        return

    # Cria as pastas de overlays e de entrada, se ainda não existirem
    os.makedirs(PASTA_OVERLAYS, exist_ok=True)
    for pos in POSICOES:
        os.makedirs(os.path.join(ENTRADA, pos), exist_ok=True)

    # Lista os vídeos de cada posição
    itens = []
    for pos in POSICOES:
        pasta = os.path.join(ENTRADA, pos)
        for nome in sorted(os.listdir(pasta)):
            if nome.lower().endswith(EXTENSOES):
                itens.append((pos, os.path.join(pasta, nome), nome))

    if not itens:
        print("Nenhum vídeo encontrado.")
        print(f"Coloque os vídeos nas pastas:\n  {ENTRADA}\\BASE\n"
              f"  {ENTRADA}\\CENTRO\n  {ENTRADA}\\TOPO")
        return

    # Escolhe e confere o overlay de cada posição que tem vídeo
    usar = {}  # pos -> (arquivo, modo)
    cor = None
    for pos in POSICOES:
        if not any(p == pos for p, _, _ in itens):
            continue
        achado = escolher_overlay(pos)
        if not achado:
            print(f"{pos}: não achei nenhum overlay em {PASTA_OVERLAYS}")
            continue
        arquivo, alfa, pix = achado
        nome_arq = os.path.basename(arquivo)
        if alfa:
            usar[pos] = (arquivo, "alfa")
            print(f"{pos}: usando '{nome_arq}' (transparência real)")
        else:
            print(f"{pos}: '{nome_arq}' NÃO tem transparência ({pix}).")
            if cor is None:
                print("  O fundo é uma cor sólida.")
                c = input("  Qual é a cor do fundo? 1 - preto  2 - verde [1]: ").strip()
                cor = "verde" if c == "2" else "preto"
            usar[pos] = (arquivo, cor)

    os.makedirs(SAIDA, exist_ok=True)
    print()
    for n, (pos, _, nome) in enumerate(itens, 1):
        aviso = ""
        if pos not in usar:
            aviso = "  (sem overlay)"
        elif os.path.exists(destino_de(nome)):
            aviso = "  (já feito)"
        print(f"{n:>3} | {pos:<6} | {nome}{aviso}")

    escolha = input(
        "\nQuais aplicar? (ex: 1,3,5 ou 2-6, Enter = todos os que faltam): "
    )
    indices = interpretar(escolha, len(itens))

    pendentes = [
        i for i in indices
        if itens[i][0] in usar and not os.path.exists(destino_de(itens[i][2]))
    ]
    if not pendentes:
        print("Nada a fazer.")
        return

    for n, i in enumerate(pendentes, 1):
        pos, caminho, nome = itens[i]
        arquivo, modo = usar[pos]
        destino = destino_de(nome)
        print(f"\n[{n}/{len(pendentes)}] {pos} - {nome}")
        cmd = (
            ["ffmpeg", "-y", "-loglevel", "error", "-stats", "-i", caminho]
            + entrada_overlay(arquivo)
            + [
                "-filter_complex", montar_filtro(modo),
                "-map", "[v]", "-map", "0:a?",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                destino,
            ]
        )
        r = subprocess.run(cmd)
        if r.returncode != 0:
            print("  Falhou neste vídeo.")
            if os.path.exists(destino):
                os.remove(destino)

    print(f"\nPronto! Vídeos com overlay em: {SAIDA}")


if __name__ == "__main__":
    main()
