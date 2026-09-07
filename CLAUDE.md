# MF Sportswear — instruções do projeto

## O que é este projeto

Site de **vitrine** da MF Sportswear (tênis e camisas importados). Não é loja virtual:
não tem carrinho, cadastro nem pagamento. O site existe para mostrar os produtos e
empurrar o cliente para o WhatsApp **(38) 99750-6508** ou para o Instagram
**@mfsports_wear**, onde a venda acontece de fato.

O dono é leigo em programação (ver o arquivo global `~/.claude/CLAUDE.md` para como
explicar as coisas).

## Como o site está montado

Site estático comum: HTML, CSS e JavaScript, sem build, sem dependências, sem
servidor. O navegador abre e pronto.

```
index.html          77 KB   o site inteiro: HTML, CSS e JavaScript
fontes/             10 arquivos .woff2  (o navegador só baixa os 4 que usa)
fotos/
  miniaturas/       500 px — as fotos da grade de produtos
  grandes/         1400 px — só descem quando alguém toca para ampliar
  logo-*.webp  hero-poster.webp  matheus.webp
video/hero.mp4     876 KB — o vídeo do topo, carregado depois da primeira tela
preview.jpg                 o cartão que aparece ao colar o link no WhatsApp
robots.txt  sitemap.xml  .nojekyll
_build/                     scripts da migração de 2026 (não afetam o site)
```

O site pesa 2,7 MB no total, mas a **primeira tela custa ~130 KB** e aparece em
menos de meio segundo no 4G. O resto entra conforme o cliente rola.

### Onde se edita cada coisa

- **Produtos** — a lista `<script type="application/json" id="mfProdutos">` dentro do
  `index.html`. É a única coisa que precisa ser mexida para adicionar, tirar ou
  reescrever um produto. Um produto é um bloco assim:

  ```json
  {"tipo": "tenis", "nome": "Nike Air Max 90",
   "texto": "Frase curta que aparece embaixo do nome.",
   "foto": "nike-air-max-90",
   "alt": "Descrição da foto para quem não enxerga"}
  ```

  O campo `foto` é só o apelido: o site monta sozinho
  `fotos/miniaturas/nike-air-max-90.webp` e `fotos/grandes/nike-air-max-90.webp`.
  `"tipo"` é `tenis` ou `camisa`. Campos opcionais: `destaque` (formato grande),
  `costas` (apelido da foto das costas, só camisa), `razao`, `recorte`, `etiqueta`.

- **Textos, preços, seções, CSS** — direto no `index.html`, que agora abre em
  qualquer editor de texto.

- **Fotos novas** — `preparar-fotos.py` (ver `fotos/LEIA-ME.txt`).

## Como abrir para testar

```bash
python3 -m http.server 8000 --directory /home/wsl/Site-MF   # sobe o servidor local
explorer.exe "http://localhost:8000"                        # abre no navegador do Windows
```

Precisa do servidor: abrir o `index.html` com dois cliques funciona, mas alguns
navegadores bloqueiam o vídeo e as fontes em `file://`.

## Publicação

GitHub Pages, repositório **público** `teu157/Site-MF`, branch `main`, pasta raiz.
Em 02/09/2026 o Pages ainda não estava ativado. Os passos para ligar estão no
`README.md`.

## Regras de trabalho

1. **Nunca fazer commit nem push sozinho.** O dono decide quando gravar e publicar.
   Com o Pages ativado, um push na `main` põe a mudança no ar em um ou dois minutos.

2. **O site é uma pasta, não um arquivo.** O `index.html` sozinho não funciona mais —
   ele depende de `fotos/`, `fontes/` e `video/`. Para mandar o site para alguém,
   mandar a pasta inteira (ou um ZIP dela).

3. **Editar cirurgicamente.** O `index.html` é legível e versionado no git, então um
   erro é recuperável (`git checkout index.html`). Ainda assim, mudança grande merece
   ser conferida no navegador antes de gravar.

4. **Só afirmar que funcionou depois de ver no navegador.** Um erro de sintaxe no
   JavaScript só aparece ao abrir a página. "Salvou sem erro" não é prova de nada.
   Conferir também o console do navegador (F12).

5. **Testar também em largura de celular.** A maior parte do tráfego vem do link do
   Instagram, ou seja, de telefone.

6. **Não quebrar os links de WhatsApp.** São 13 links `wa.me` — o único caminho de
   venda. O número mora num lugar só (a constante `ZAP` no JavaScript), então produto
   novo não consegue apontar para o telefone errado. Depois de qualquer mexida,
   conferir que continuam apontando para (38) 99750-6508.

7. **Cuidar do peso.** Toda foto nova passa pelo `preparar-fotos.py` antes de entrar.
   Foto direto do celular tem 3 a 8 MB e sozinha desfaz o ganho de desempenho.

8. **O repositório é público.** Nunca colocar senha, chave de acesso ou dado sigiloso
   em arquivo deste projeto — vai para a internet junto.

## Histórico

Até setembro de 2026 o site era um `index.html` único de 3,9 MB, gerado por uma
ferramenta externa, com todas as mídias embutidas em base64 e montadas em tempo de
execução por React. Levava **7,9 s para aparecer no 4G** (20,7 s no 4G fraco, 44,3 s
no 3G) porque nada era desenhado antes do pacote inteiro chegar.

A migração para site estático (scripts em `_build/`) derrubou isso para **0,3 s** e
tornou o conteúdo visível para o Google. Nenhuma foto, texto ou link foi perdido.
