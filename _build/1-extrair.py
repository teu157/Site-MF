#!/usr/bin/env python3
"""Extrai as 32 midias e o template de dentro do index.html empacotado.

Reversivel byte a byte: o que sai daqui e exatamente o que estava no manifest.
Roda uma vez; depois disso o bundle nao e mais necessario.
"""
import base64, gzip, json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUTO = os.path.join(RAIZ, '_build', 'bruto')

# uuid -> nome de arquivo de destino (sem extensao para imagens: o passo 2 decide)
FONTES = {
    '90a893f7-2199-4e33-8421-899d1b63444d': 'bebas-neue-latin-ext',
    'd34997b6-5461-46ea-96f8-0fb4823b31d8': 'bebas-neue-latin',
    'b8db1586-78fe-4a64-95d2-2b4110610134': 'sora-latin-ext',
    '387211bb-3476-4286-9d41-c6b13e56e652': 'sora-latin',
    '52e96f96-7847-4fb1-b93f-a266876aa30c': 'space-mono-400-latin-ext',
    '126730da-d6a2-4395-b130-42b3e3e42d6e': 'space-mono-400-latin',
    'e9c1bd19-e49d-4f63-ac45-2a1a494c67b9': 'space-mono-400-vietnamese',
    '7a7add65-f61b-4d56-bd32-e70bbebbd750': 'space-mono-700-latin-ext',
    'fd2bc764-30de-40eb-96b2-748af5325d66': 'space-mono-700-latin',
    '38be1672-4a48-42f2-b561-8479b0e0bc55': 'space-mono-700-vietnamese',
}

# fotos de produto: o apelido segue a mesma regra do preparar-fotos.py
PRODUTOS = {
    '3537d8a7-efdd-4112-8c70-7e4f4ee08fa8': 'nike-air-zoom-alphafly-3',
    '630a5222-0fa8-44e7-9a63-f14ee3bd934d': 'nike-air-vapormax-plus',
    'd6a4f977-98a9-4e3e-97a2-2eb3a8918631': 'nike-air-vapormax-2020-flyknit',
    '34cd74ec-296f-433b-9a08-a0da4bcb9559': 'nike-dunk-low-azul',
    '4488d39a-0e2e-4d8a-84e4-bc50398e053e': 'nike-dunk-low-creme',
    '76dedb75-077c-42d6-af90-fcd6fc236928': 'brasil-amarela',
    '43fab31a-edf8-4136-aaeb-a372b186d24f': 'brasil-amarela-costas',
    '77f679d8-ce1f-4939-92de-bf9232f57b59': 'brasil-verde',
    '36866e06-4489-40a5-ab98-4c18d89cc48b': 'brasil-verde-costas',
    'dd189d11-dae4-496e-ac0b-99a234f377e5': 'atletico-mineiro',
    'd6c55689-e7c5-40e1-a5f4-9582152fe158': 'atletico-mineiro-costas',
    'c4d315b6-b0b3-48ed-a591-c7b7fc5d22a9': 'cruzeiro',
    '597fcfc5-aee1-4698-8886-d3249ba81f80': 'cruzeiro-costas',
}

# imagens que nao sao produto (nao entram na grade, nao precisam de duas versoes)
AVULSAS = {
    '365f9974-b69a-42d1-bae6-425cec8514cc': 'logo-coroa',
    '351a7ae2-946d-43c0-a040-ccee4ad80531': 'logo-texto',
    '243f7afa-b9d9-4efb-b147-895257b21ce8': 'logo-rodape',
    '63b7295a-7197-46e7-8ae2-e9e2b8575d74': 'hero-poster',
    'b7c4ac79-7fe8-445b-9e6f-3c0d797cb98b': 'matheus',
}

VIDEO = {'0fd9929d-f59b-425b-8e13-d8fbaf5a0ef5': 'hero'}

# React/ReactDOM/dc-runtime: registrados na ilha ext_resources. O site estatico
# nao usa nenhum dos tres, entao ficam de fora de proposito.
DESCARTAR = {
    'a23b6230-3dcb-4417-ac70-bd4dbadf27c0',   # react 18.3.1
    '23ec7ce6-1dfb-400f-a9bc-1d8092537e7c',   # react-dom 18.3.1
    '68c616c4-3268-4edb-905d-19c46fdc3605',   # dc-runtime
}

EXT = {'image/jpeg': '.jpg', 'image/png': '.png', 'video/mp4': '.mp4',
       'font/woff2': '.woff2', 'text/javascript': '.js'}


def main():
    src = open(os.path.join(RAIZ, 'index.html'), encoding='utf-8').read()
    man = json.loads(re.search(
        r'<script type="__bundler/manifest"[^>]*>(.*?)</script>', src, re.S).group(1))
    tpl = json.loads(re.search(
        r'<script type="__bundler/template"[^>]*>(.*?)</script>', src, re.S).group(1))

    for sub in ('fontes', 'produtos', 'avulsas', 'video'):
        os.makedirs(os.path.join(BRUTO, sub), exist_ok=True)

    open(os.path.join(BRUTO, 'template.html'), 'w', encoding='utf-8').write(tpl)
    print('template.html  %d caracteres' % len(tpl))

    vistos, total = set(), 0
    for uuid, entrada in man.items():
        dados = base64.b64decode(entrada['data'])
        if str(entrada.get('compressed')).lower() == 'true':
            dados = gzip.decompress(dados)
        ext = EXT.get(entrada['mime'], '.bin')

        if uuid in DESCARTAR:
            print('  descartado (nao usado no site estatico): %s' % uuid[:8])
            vistos.add(uuid)
            continue
        if uuid in FONTES:
            destino = os.path.join(BRUTO, 'fontes', FONTES[uuid] + '.woff2')
        elif uuid in PRODUTOS:
            destino = os.path.join(BRUTO, 'produtos', PRODUTOS[uuid] + ext)
        elif uuid in AVULSAS:
            destino = os.path.join(BRUTO, 'avulsas', AVULSAS[uuid] + ext)
        elif uuid in VIDEO:
            destino = os.path.join(BRUTO, 'video', VIDEO[uuid] + ext)
        else:
            sys.exit('PAROU: uuid sem destino definido: %s (%s)' % (uuid, entrada['mime']))

        open(destino, 'wb').write(dados)
        vistos.add(uuid)
        total += len(dados)
        print('  %-42s %8.1f KB' % (os.path.relpath(destino, BRUTO), len(dados) / 1024))

    faltando = set(man) - vistos
    if faltando:
        sys.exit('PAROU: %d uuid(s) nao extraidos: %s' % (len(faltando), faltando))
    print('\n%d midias extraidas, %.2f MB' % (len(vistos) - len(DESCARTAR), total / 1024 / 1024))


if __name__ == '__main__':
    main()
