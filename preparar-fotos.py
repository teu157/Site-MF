#!/usr/bin/env python3
"""
Prepara as fotos dos produtos para o site da MF Sportswear.

COMO USAR
---------
1. Copie as fotos do celular para a pasta  fotos-originais/
2. Rode:   python3 preparar-fotos.py
3. Confira a tabela de pesos que aparece no fim.

O que ele faz com cada foto:

  fotos-originais/Nike Air Max 90.jpg
        |
        +--> fotos/miniaturas/nike-air-max-90.webp    (500 px  ~30 KB)  a grade
        +--> fotos/grandes/nike-air-max-90.webp      (1400 px ~130 KB)  ao ampliar

As duas versoes existem porque a grade mostra quadradinhos de 300 px: mandar a
foto grande para cada um deles faria o cliente baixar megabytes a toa. A versao
grande so desce quando alguem toca para ampliar.

O ORIGINAL NUNCA E APAGADO. A pasta fotos-originais/ fica fora do repositorio
(esta no .gitignore), entao as fotos pesadas do celular nao vao para a internet.

Se a foto ja foi convertida, ele pula. Para refazer, use:  --refazer
"""

import os
import re
import sys
import shutil
import subprocess
import unicodedata

RAIZ = os.path.dirname(os.path.abspath(__file__))
ORIGINAIS = os.path.join(RAIZ, 'fotos-originais')
MINIATURAS = os.path.join(RAIZ, 'fotos', 'miniaturas')
GRANDES = os.path.join(RAIZ, 'fotos', 'grandes')

# largura em pixels e qualidade (0-100) de cada versao
MEDIDAS = [
    (MINIATURAS, 500, 75),
    (GRANDES, 1400, 80),
]

ACEITAS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.bmp', '.tif', '.tiff'}
LIMITE_AVISO = 200 * 1024   # acima disto a foto merece um olhar

# O ffmpeg do Linux nao existe neste ambiente; usamos o do Windows, que enxerga
# as pastas do WSL pelo caminho \\wsl.localhost\... que o wslpath devolve.
FFMPEG = shutil.which('ffmpeg') or shutil.which('ffmpeg.exe')


def caminho_para_ffmpeg(p):
    """Converte caminho Linux para o formato que o ffmpeg.exe entende."""
    if FFMPEG and FFMPEG.endswith('.exe'):
        try:
            return subprocess.run(['wslpath', '-w', p], capture_output=True,
                                  text=True, check=True).stdout.strip()
        except Exception:
            return p
    return p


def apelido(nome_arquivo):
    """'Nike Air Max 90 (1).JPG' -> 'nike-air-max-90-1'  (sem acento nem espaco)."""
    base = os.path.splitext(nome_arquivo)[0]
    base = unicodedata.normalize('NFKD', base)
    base = ''.join(c for c in base if not unicodedata.combining(c))
    base = base.lower()
    base = re.sub(r'[^a-z0-9]+', '-', base)
    return re.sub(r'-+', '-', base).strip('-') or 'foto'


def converter(entrada, saida, largura, qualidade):
    """Redimensiona e comprime. Nao aumenta foto pequena: min(largura, original)."""
    cmd = [
        FFMPEG, '-hide_banner', '-loglevel', 'error', '-y',
        '-i', caminho_para_ffmpeg(entrada),
        # 'if(gt(iw,L),L,iw)' = so encolhe; foto menor que o alvo fica como esta.
        # -2 na altura mantem a proporcao e garante numero par de pixels.
        '-vf', "scale='if(gt(iw,{L}),{L},iw)':-2".format(L=largura),
        '-c:v', 'libwebp', '-quality', str(qualidade),
        caminho_para_ffmpeg(saida),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return r.stderr.strip()[:200] or 'ffmpeg falhou'
    return None


def kb(caminho):
    return os.path.getsize(caminho) / 1024


def main():
    refazer = '--refazer' in sys.argv

    if not FFMPEG:
        sys.exit('PAROU: nao encontrei o ffmpeg. Ele e quem comprime as fotos.')

    if not os.path.isdir(ORIGINAIS):
        os.makedirs(ORIGINAIS, exist_ok=True)
        print('Criei a pasta  fotos-originais/')
        print('Copie as fotos do celular para dentro dela e rode de novo.')
        return

    for pasta, _, _ in MEDIDAS:
        os.makedirs(pasta, exist_ok=True)

    arquivos = sorted(
        f for f in os.listdir(ORIGINAIS)
        if os.path.splitext(f)[1].lower() in ACEITAS
        and os.path.isfile(os.path.join(ORIGINAIS, f))
    )

    if not arquivos:
        print('A pasta fotos-originais/ esta vazia.')
        print('Formatos aceitos: ' + ', '.join(sorted(ACEITAS)))
        return

    print('%d foto(s) para preparar.\n' % len(arquivos))

    linhas, pulados, erros, usados = [], 0, [], {}

    for arq in arquivos:
        entrada = os.path.join(ORIGINAIS, arq)
        nome = apelido(arq)

        # dois arquivos diferentes que virariam o mesmo apelido
        if nome in usados:
            erros.append('%s e %s viram o mesmo nome (%s) - renomeie um deles'
                         % (usados[nome], arq, nome))
            continue
        usados[nome] = arq

        saidas, faltando = [], False
        for pasta, largura, qualidade in MEDIDAS:
            saida = os.path.join(pasta, nome + '.webp')
            saidas.append(saida)
            if refazer or not os.path.exists(saida):
                faltando = True

        if not faltando:
            pulados += 1
            continue

        falhou = None
        for (pasta, largura, qualidade), saida in zip(MEDIDAS, saidas):
            falhou = converter(entrada, saida, largura, qualidade)
            if falhou:
                erros.append('%s: %s' % (arq, falhou))
                break
        if falhou:
            continue

        linhas.append((nome, kb(entrada), kb(saidas[0]), kb(saidas[1])))
        print('  ok  %s' % nome)

    print('\n%-38s %9s %9s %9s' % ('foto', 'original', 'miniatura', 'grande'))
    print('-' * 68)
    pesadas = 0
    for nome, orig, mini, grande in linhas:
        aviso = ''
        if grande * 1024 > LIMITE_AVISO:
            aviso = '  <-- pesada'
            pesadas += 1
        print('%-38s %7.0f KB %7.0f KB %7.0f KB%s' % (nome[:38], orig, mini, grande, aviso))

    if linhas:
        soma_mini = sum(l[2] for l in linhas)
        soma_grande = sum(l[3] for l in linhas)
        print('-' * 68)
        print('%-38s %9s %7.0f KB %7.0f KB' % ('TOTAL de %d fotos' % len(linhas), '', soma_mini, soma_grande))
        print('\nA grade inteira custa %.1f MB ao cliente, e mesmo assim so baixa'
              % (soma_mini / 1024))
        print('conforme ele rola. As fotos grandes (%.1f MB) so descem quando'
              % (soma_grande / 1024))
        print('alguem toca para ampliar.')

    if pulados:
        print('\n%d foto(s) ja estavam prontas e foram puladas (use --refazer para refazer).' % pulados)
    if pesadas:
        print('\n%d foto(s) passaram de 200 KB. Vale conferir se nao tem borda'
              ' branca\nou area vazia sobrando, que incham o arquivo sem mostrar produto.' % pesadas)
    if erros:
        print('\nPROBLEMAS:')
        for e in erros:
            print('  - ' + e)

    if linhas:
        print('\nAgora me diga o nome e a descricao de cada peca que eu ponho na lista.')
        print('Os apelidos das fotos sao:')
        for nome, _, _, _ in linhas:
            print('  ' + nome)


if __name__ == '__main__':
    main()
