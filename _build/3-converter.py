#!/usr/bin/env python3
"""Converte o template do bundler em um index.html estatico de verdade.

Nada de React, nada de dc-runtime, nada de "Unpacking...". O miolo do JavaScript
e copiado literalmente; so muda o inv�lucro e os enderecos das midias.
"""
import os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(RAIZ, '_build', 'bruto', 'template.html')
SAIDA = os.path.join(RAIZ, 'index.html')

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
AVULSAS = {
    '365f9974-b69a-42d1-bae6-425cec8514cc': 'fotos/logo-coroa.webp',
    '351a7ae2-946d-43c0-a040-ccee4ad80531': 'fotos/logo-texto.webp',
    '243f7afa-b9d9-4efb-b147-895257b21ce8': 'fotos/logo-rodape.webp',
    '63b7295a-7197-46e7-8ae2-e9e2b8575d74': 'fotos/hero-poster.webp',
    'b7c4ac79-7fe8-445b-9e6f-3c0d797cb98b': 'fotos/matheus.webp',
    '0fd9929d-f59b-425b-8e13-d8fbaf5a0ef5': 'video/hero.mp4',
}
# passar o mouse: no bundler vinha do atributo style-hover, aqui vira CSS de verdade
HOVER = {
    'color:#4fb98d': 'mf-hv-verde',
    'color:#eef2ee': 'mf-hv-claro',
    'background:#7fd9b0': 'mf-hv-menta',
    'background:#7fd9b0;color:#080b09': 'mf-hv-menta-escuro',
    'border-color:#4fb98d;background:rgba(79,185,141,.1);color:#eef2ee': 'mf-hv-contorno',
}

def exigir(cond, msg):
    if not cond:
        sys.exit('PAROU: ' + msg)

def fatiar(tpl):
    """Separa helmet (vai para o <head>), corpo e script."""
    a = tpl.index('<helmet>') + len('<helmet>')
    b = tpl.index('</helmet>')
    helmet = tpl[a:b]
    c = tpl.index('</helmet>') + len('</helmet>')
    d = tpl.index('</x-dc>')
    corpo = tpl[c:d]
    e = tpl.index('<script type="text/x-dc" data-dc-script="">')
    e = tpl.index('\n', e) + 1
    f = tpl.rindex('</script>')
    script = tpl[e:f]
    return helmet, corpo, script

def trocar_midias(txt):
    for uuid, nome in FONTES.items():
        txt = txt.replace('"%s"' % uuid, '"fontes/%s.woff2"' % nome)
    for uuid, caminho in AVULSAS.items():
        txt = txt.replace(uuid, caminho)
    for uuid, apelido in PRODUTOS.items():
        # so na lista de produtos: pequena()/grande() montam o caminho sozinhas
        txt = txt.replace('"%s"' % uuid, '"%s"' % apelido)
    return txt

def traduzir_hover(txt):
    """style-hover="..." -> classe CSS. Junta a classe com as que ja existirem."""
    regras, faltando = [], []
    def sub(m):
        valor = m.group(1)
        classe = HOVER.get(valor)
        if not classe:
            faltando.append(valor)
            return ''
        return '\x00' + classe + '\x00'
    txt = re.sub(r'\s*style-hover="([^"]*)"', sub, txt)
    exigir(not faltando, 'style-hover sem classe definida: %r' % faltando)

    # move o marcador para dentro do class= da propria tag
    def dentro(m):
        tag = m.group(0)
        classes = re.findall(r'\x00([\w-]+)\x00', tag)
        if not classes:
            return tag
        tag = re.sub(r'\x00[\w-]+\x00', '', tag)
        if re.search(r'\sclass="', tag):
            tag = re.sub(r'\sclass="([^"]*)"', lambda x: ' class="%s %s"' % (x.group(1), ' '.join(classes)), tag, count=1)
        else:
            tag = tag[:tag.index(' ')] + ' class="%s"' % ' '.join(classes) + tag[tag.index(' '):]
        return tag
    txt = re.sub(r'<[a-zA-Z][^>]*>', dentro, txt)
    exigir('\x00' not in txt, 'sobrou marcador de hover sem tag')
    for valor, classe in HOVER.items():
        regras.append('.%s:hover{%s}' % (classe, valor))
    return txt, regras

def main():
    tpl = open(TPL, encoding='utf-8').read()
    helmet, corpo, script = fatiar(tpl)

    # --- SVG: o runtime desfazia o camelCase; em HTML puro precisa do nome real
    n = corpo.count('sc-camel-view-box')
    exigir(n == 3, 'esperava 3 sc-camel-view-box, achei %d' % n)
    corpo = corpo.replace('sc-camel-view-box=', 'viewBox=')

    helmet = trocar_midias(helmet)
    corpo = trocar_midias(corpo)
    corpo, regras_hover = traduzir_hover(corpo)

    # o texto "style-hover" ainda aparece num comentario do CSS; o que nao pode
    # sobrar e o atributo de verdade
    exigir(not re.search(r'style-hover=', corpo + helmet), 'sobrou o atributo style-hover')
    sobrou = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', helmet + corpo)
    exigir(not sobrou, 'sobraram uuids sem destino: %r' % set(sobrou))

    # ---------- CORRECOES DOS DEFEITOS ----------
    # (a) botao "Tocar o video" nascia no centro da tela, em cima do <h1>
    antes_btn = 'position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:8;display:none;'
    exigir(antes_btn in corpo, 'nao achei o estilo do botao de play')
    corpo = corpo.replace(
        antes_btn,
        'position:absolute;left:clamp(16px,4vw,40px);top:clamp(84px,11vh,104px);z-index:8;display:none;')

    # (c) alvo de toque do botao de WhatsApp da barra: 40px -> 44px
    exigir(corpo.count('min-height:40px;padding:0 18px') == 1, 'nao achei o botao da barra')
    corpo = corpo.replace('min-height:40px;padding:0 18px', 'min-height:44px;padding:0 18px')

    # video so entra depois que a pagina ja apareceu: preload="none" + data-src
    exigir('preload="auto" poster="fotos/hero-poster.webp" src="video/hero.mp4"' in corpo,
           'nao achei os atributos do video')
    corpo = corpo.replace(
        'preload="auto" poster="fotos/hero-poster.webp" src="video/hero.mp4"',
        'preload="none" poster="fotos/hero-poster.webp" data-src="video/hero.mp4"')

    # ---------- CSS extra ----------
    extra = (
        '\n/* O menu e fixo (69px): sem isto o titulo da secao para debaixo dele. */\n'
        'section[id]{scroll-margin-top:88px}\n'
        '/* Alvo de toque de 44px sem mudar o tamanho do texto: cresce so a area. */\n'
        '.mf-link{min-height:44px}\n'
        '.mf-vira-btn{display:inline-flex;align-items:center;min-height:44px}\n'
        '.mf-marca{min-height:44px}\n'
        'footer nav{gap:0!important}\n'
        'footer nav a{display:flex;align-items:center;min-height:44px}\n'
        '#mfMenu a[href^="#"]{padding:15px 0}\n'
        '/* Passar o mouse — vinha do atributo style-hover do bundler. */\n'
        + '\n'.join(regras_hover) + '\n'
        '/* Quem pediu menos movimento no sistema nao recebe as animacoes. */\n'
        '@media (prefers-reduced-motion: reduce){\n'
        '  *,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;'
        'transition-duration:.001ms!important;scroll-behavior:auto!important}\n'
        '}\n'
    )
    exigir(helmet.count('.mf-link{display:inline-flex') == 1, 'nao achei a regra .mf-link')
    # marca a logo da barra para receber os 44px
    exigir(corpo.count('<a href="#topo" style="display:flex;align-items:center;gap:10px;color:#eef2ee">') == 1,
           'nao achei o link da logo')
    corpo = corpo.replace('<a href="#topo" style="display:flex;align-items:center;gap:10px;color:#eef2ee">',
                          '<a class="mf-marca" href="#topo" style="display:flex;align-items:center;gap:10px;color:#eef2ee">')
    helmet = helmet.replace('</style>', extra + '</style>', 1) if '</style>' in helmet else helmet
    exigir('scroll-margin-top:88px' in helmet, 'o CSS extra nao entrou')

    # ---------- JavaScript ----------
    script = script.replace('class Component extends DCLogic {', 'class MFSite {', 1)
    exigir('class MFSite {' in script, 'nao troquei a classe')
    script = script.replace('  componentDidMount() {', '  iniciar() {', 1)
    # o runtime recriava o documento e o lang se perdia; agora o <html lang> e real
    script = re.sub(
        r'\s*/\* o runtime recria o documento.*?\*/\s*\n\s*document\.documentElement\.lang = \'pt-BR\';',
        '', script, flags=re.S)
    exigir('documentElement.lang' not in script, 'nao removi o ajuste de lang')
    # nada desmonta numa pagina estatica: componentWillUnmount e renderVals saem
    i = script.index('  componentWillUnmount() {')
    j = script.index('  renderVals() { return {}; }')
    script = script[:i] + script[j:]
    script = script.replace('  renderVals() { return {}; }\n', '')
    exigir('componentWillUnmount' not in script and 'renderVals' not in script, 'sobrou metodo do React')

    # o video so ganha endereco depois que a pagina inteira ja carregou
    alvo = "    const reduzido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;\n    const mostrarBotao"
    exigir(alvo in script, 'nao achei o ponto de entrada do video')
    script = script.replace(alvo,
        "    /* o endereco do video so e ligado depois que a pagina ja apareceu:\n"
        "       assim os 876 KB dele nunca disputam banda com a primeira tela */\n"
        "    const ligarFonte = () => {\n"
        "      if (v.getAttribute('src') || !v.dataset.src) return;\n"
        "      v.setAttribute('src', v.dataset.src);\n"
        "    };\n"
        "    const reduzido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;\n"
        "    const mostrarBotao", 1)
    alvo2 = "      const p = v.play();"
    exigir(script.count(alvo2) == 1, 'nao achei o play()')
    script = script.replace(alvo2, "      ligarFonte();\n      const p = v.play();", 1)
    # a primeira tentativa espera o load da pagina
    alvo3 = "      tocar();\n      v.addEventListener('loadeddata', tocar, { once: true });"
    exigir(alvo3 in script, 'nao achei a primeira tentativa de tocar')
    script = script.replace(alvo3,
        "      if (document.readyState === 'complete') tocar();\n"
        "      else window.addEventListener('load', tocar, { once: true });\n"
        "      v.addEventListener('loadeddata', tocar, { once: true });", 1)

    # o link "Consultar" ganhou 44px de altura no CSS; a margem de cima encolhe
    # para o cartao nao crescer de tamanho
    exigir(script.count("' style=\"margin-top:12px\">Consultar") == 2,
           'esperava 2 links Consultar com margin-top:12px')
    script = script.replace("' style=\"margin-top:12px\">Consultar", "' style=\"margin-top:2px\">Consultar")

    script += "\n\ndocument.addEventListener('DOMContentLoaded', function () { new MFSite().iniciar(); });\n"

    # ---------- cabecalho ----------
    # as fontes agora sao locais: abrir conexao com o Google nao serve mais para
    # nada e ainda custa uma consulta de DNS e um aperto de mao TLS a toa
    exigir(helmet.count('rel="preconnect"') == 2, 'esperava 2 preconnect')
    helmet = re.sub(r'\s*<link rel="preconnect"[^>]*>', '', helmet)

    # o que pinta a primeira tela vai na frente da fila
    preload = (
        '\n<link rel="preload" as="image" href="fotos/hero-poster.webp" fetchpriority="high">\n'
        '<link rel="preload" as="font" type="font/woff2" href="fontes/bebas-neue-latin.woff2" crossorigin>\n'
        '<link rel="preload" as="font" type="font/woff2" href="fontes/sora-latin.woff2" crossorigin>\n'
    )

    # Dados estruturados. So do que e HTML estatico de verdade: a loja e as
    # duvidas. Os produtos continuam sendo montados por JavaScript a partir da
    # lista mfProdutos, entao descreve-los aqui seria duplicar a mesma informacao
    # em dois lugares — e o dono teria de lembrar de mexer nos dois.
    duvidas = re.findall(
        r'<h3 style="font-size:18px[^"]*">(.*?)</h3>\s*<p[^>]*>(.*?)</p>', corpo, re.S)
    exigir(len(duvidas) == 6, 'esperava 6 duvidas, achei %d' % len(duvidas))
    import json as _json
    dados = [{
        '@context': 'https://schema.org', '@type': 'Store',
        'name': 'MF Sportswear',
        'description': 'Tênis e camisas importados, linha premium. Venda por WhatsApp, '
                       'com foto real da peça antes do pagamento e envio para todo o Brasil.',
        'url': 'https://teu157.github.io/Site-MF/',
        'image': 'https://teu157.github.io/Site-MF/preview.jpg',
        'telephone': '+5538997506508',
        'areaServed': {'@type': 'Country', 'name': 'Brasil'},
        'sameAs': ['https://instagram.com/mfsports_wear'],
        'founder': {'@type': 'Person', 'name': 'Matheus'},
    }, {
        '@context': 'https://schema.org', '@type': 'FAQPage',
        'mainEntity': [{
            '@type': 'Question', 'name': re.sub(r'\s+', ' ', p).strip(),
            'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'\s+', ' ', r).strip()},
        } for p, r in duvidas],
    }]
    ld = '\n'.join(
        '<script type="application/ld+json">%s</' % _json.dumps(d, ensure_ascii=False) + 'script>'
        for d in dados)

    helmet = helmet.replace('<style>', preload + ld + '\n<style>', 1)

    # ---------- montar o arquivo ----------
    saida = (
        '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
        + helmet.strip()
        + '\n</head>\n<body>\n'
        + corpo.strip()
        + '\n\n<script>\n' + script.strip() + '\n</' + 'script>\n</body>\n</html>\n'
    )
    open(SAIDA, 'w', encoding='utf-8').write(saida)
    print('index.html escrito: %d caracteres (%.0f KB)' % (len(saida), len(saida.encode()) / 1024))
    print('  %d regras :hover traduzidas' % len(regras_hover))

if __name__ == '__main__':
    main()
