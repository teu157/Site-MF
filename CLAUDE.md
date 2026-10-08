# MF Sportswear — instruções do projeto

## O que é este projeto

Site de **vitrine** da MF Sportswear (tênis e camisas importados). Não é loja virtual:
não tem carrinho, cadastro nem pagamento. O site existe para mostrar os produtos e
empurrar o cliente para o WhatsApp **(38) 99750-6508** ou para o Instagram
**@mfsports_wear**, onde a venda acontece de fato.

O dono é leigo em programação (ver o arquivo global `~/.claude/CLAUDE.md` para como
explicar as coisas).

### Papel do site (decidido em 27/set/2026)

O site **não traz cliente**: ele ajuda a **fechar** quem já chegou pelo Instagram e está
desconfiado. O gargalo da loja é alcance (quanta gente nova vê o produto), e isso se
resolve no conteúdo do Instagram, não aqui. Os números do negócio ficam fora deste
arquivo: o repositório é público (regra 8).
Por isso, **nada de redesenho, seção nova, SEO, domínio próprio ou anúncio** até a
revisão abaixo. O link da bio continua indo direto para o WhatsApp; o site é o segundo
link e o que o dono manda na conversa quando o cliente hesita.

**Revisão em 26/nov/2026.** Somar as conversas com "pelo site" no WhatsApp (ver
Medição), a anotação de origem de cada venda e o Vercel Analytics, se já ligado:
- 2 ou mais vendas pelo site em 60 dias → manter e atualizar; aí discutir domínio próprio;
- 1 venda → mais 30 dias de teste;
- zero → o site vira página fixa de confiança e o catálogo fica só nos stories.

**Exceção decidida pelo dono em 8/out/2026:** entrou o "Ver mais N modelos" com fotos de
fornecedor na seção de tênis (ver "Mais modelos" abaixo). Foi pedido dele, não iniciativa da sessão.

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
_build/                     scripts da migração de 2026 e o fotos-chromium.js
                            (nada daqui vai para o ar)
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
  `costas` (apelido da foto das costas, só camisa), `tamanhos` (ex.: `"37 ao 43"`),
  `razao`, `recorte`, `etiqueta`.

- **Mais modelos (foto de fornecedor)** — a lista `<script type="application/json" id="mfEncomenda">`,
  logo depois da `mfProdutos`. Mesmo formato de produto. Aparecem só depois que o cliente toca em
  "Ver mais N modelos", logo abaixo dos tênis do dono, em cartão **quadrado** (a foto do fornecedor
  vem em pé e o recorte 4/3 cortaria o tênis), com o mesmo "Consultar" e a mesma mensagem de
  WhatsApp dos outros. Antes do toque nenhuma dessas fotos é baixada. O apelido da foto **sempre
  começa com `fornecedor-`**. Quando o par ganha foto com a placa MF, ele **sai da `mfEncomenda` e
  entra na `mfProdutos`**, com foto nova sem o prefixo. Funciona igual para camisa.

  **Decisão do dono (8/out/2026): o site não separa em texto "o que está comigo" do que não está.**
  A primeira versão tinha título "Ainda não estão comigo" e etiqueta "Encomenda"; ele achou estranho
  e pediu texto comum de loja. O cliente distingue pela foto: placa MF = par com o dono.

- **Fotos de prova** — a lista `id="mfProva"`, logo acima da seção `#prova`
  ("Já saiu daqui"): encomendas postadas e clientes com a peça. Mesmo formato,
  com `foto`, `alt` e `legenda`. **Lista vazia esconde a seção inteira**, então dá
  para tirar tudo sem quebrar o layout.

- **Textos, seções, CSS** — direto no `index.html`, que agora abre em qualquer
  editor de texto.

- **Fotos novas** — no computador de casa, `preparar-fotos.py` (ver `fotos/LEIA-ME.txt`).
  Numa sessão na nuvem, onde não há ffmpeg, `node _build/fotos-chromium.js`: mesmo
  resultado, pelo Chromium. **Foto em pé de celular precisa de `--recorte`**: a grade e a
  janela de ampliar só mostram uma janela da foto (4/3 no tênis, 3/4 na camisa), então o
  arquivo é cortado nessa janela — sem isso a grande sai com ~450 KB, dois terços
  invisíveis. Ajustar o recorte olhando o cartão no navegador; recortado, o produto fica
  sem o campo `recorte`.

  **Foto de fornecedor só entra na `mfEncomenda`**, para as fotos do dono virem sempre primeiro: o
  site **se recusa** a mostrar na grade principal qualquer foto com apelido `fornecedor-` e acusa
  no console (F12). Recortar em quadrado: `--recorte "1/1 45%"`, ajustando o número até o tênis
  caber inteiro.

  **Regra que não pode quebrar:** com foto de fornecedor no site, **nenhum texto pode prometer**
  "foto real", "sem foto de catálogo", "você vê exatamente a peça", "em estoque" ou "fotos das peças
  que passaram pelo estoque". Foi por isso que essas frases saíram em out/2026. Prometer foto real
  e mostrar foto de fornecedor é propaganda enganosa (CDC, art. 37); foto de fornecedor sem essa
  promessa, com disponibilidade confirmada no WhatsApp, é prática comum de loja. Em setembro de 2026 saíram por isso o Dunk azul royal e o
  VaporMax Plus, mesmo em estoque (voltam quando houver foto do dono), e as fotos do Dunk
  creme e do VaporMax 2020 foram trocadas pelas do dono, com a placa MF ao fundo.

- **Preço** — aparece na tela em **três lugares**, todos escritos à mão no `index.html`:
  o parágrafo da seção `#tenis` (R$ 249), o da seção `#camisas` (R$ 169) e a primeira
  pergunta do `#duvidas` (os dois). Existe um **quarto**, invisível: o bloco
  `<script type="application/ld+json">` do `FAQPage`, no topo do arquivo, que repete a
  resposta palavra por palavra para o Google. **Mudou o preço, mudar nos quatro.** Os
  que citam valor estão marcados com `<!-- PRECO: ... -->`; procurar por `R$` acha todos.

  O preço fica de propósito **fora** do título, do topo, da faixa rolante e do cartão do
  WhatsApp: o site vende acesso e curadoria, não preço baixo. Contra Shopee e revenda de
  Instagram sempre vai existir alguém mais barato, então preço como manchete é briga
  perdida. Ele responde a dúvida ao lado do produto, e só.

- **Política de troca** — está escrita na terceira pergunta do `#duvidas` (e repetida no
  `FAQPage`): 7 dias de arrependimento, que é obrigação legal em venda a distância
  (CDC, art. 49), **mais** troca de numeração com o frete da troca por conta do cliente.
  Se essa regra mudar na prática, mudar o texto junto — política escrita no site vale.

- **Foto ou vídeo antes de pagar** — quando o par está com o dono, o cliente recebe **vídeo**; quando
  vem do fornecedor, **fotos do par** (o dono não consegue garantir vídeo). Por isso o site promete
  sempre "**fotos ou vídeo**": subtítulo do topo, faixa rolante, passo 2 do "Como funciona", a pergunta
  "Como tenho certeza de que a compra é segura?" (e o `FAQPage`) e a descrição do site, que aparece
  **4 vezes** no topo do arquivo (Google, `og:`, Twitter e o `Store`). Não voltar a prometer só "vídeo".

- **Entrega** — em Sete Lagoas é em mãos. Está em três lugares: a última pergunta do
  `#duvidas`, a mesma resposta no `FAQPage` (palavra por palavra) e o primeiro selo da
  seção "Quem vende". Se a entrega local parar, tirar dos três.

### Duas coisas para não esquecer nas fotos de prova

1. **Dado de cliente não vai para o site.** Nome, CPF, endereço e CEP de quem
   comprou não podem aparecer numa foto de etiqueta — é dado pessoal de terceiro
   num site público, e serve de material para golpe contra o próprio cliente.
   Cuidado com o que não é texto: o **código 2D e o QR da declaração guardam os
   mesmos dados dentro**, e a **chave de acesso da DACE** (o número de 44 dígitos)
   permite consultar a declaração e ler tudo de novo. Tapar com retângulo opaco,
   nunca desfoque — texto pequeno borrado às vezes volta a ser legível com
   realce de contraste. Foto da caixa fechada evita o problema todo.
   As fotos que já estão no site foram tratadas pelo `_build/4-tapar.js`.

2. **Preço dentro de foto não entra no site.** A foto `prova-estoque-brasil` foi
   tirada da lista `mfProva` em setembro de 2026: ela traz "Os primeiros 10 clientes,
   R$ 199,90 → R$ 169,90" queimado na imagem, e como R$ 169 virou o preço normal da
   camisa aquilo anunciava uma escassez que não existe mais. O arquivo continua em
   `fotos/` caso um dia seja tratado. Regra geral: preço queimado em imagem não pode
   ser atualizado, então vira propaganda enganosa sozinho (CDC, art. 30 e 37).

## Atualização da semana

O site não promete mais estoque em tempo real (a seção de tênis diz "Disponibilidade e
numeração confirmadas na hora, pelo WhatsApp"). Mesmo assim, manter a lista em dia evita
conversa perdida com modelo que acabou. A rotina, numa sessão do Claude Code (dá para fazer
pelo celular):

1. O dono manda as fotos dos pares novos (no cenário da placa MF) e diz o que esgotou.
2. Copiar a foto escolhida de cada par — **a de lado**, que é a que cabe no cartão 4/3 —
   para `fotos-originais/` com o nome do produto (`Nike SB Dunk Low Pro marinho.jpg`) e
   rodar `node _build/fotos-chromium.js --recorte "4/3 70%" "Nike SB Dunk Low Pro marinho.jpg"`.
3. Tirar da lista o que esgotou e pôr o que entrou. O nome vem da etiqueta da língua do
   tênis, não do que o fornecedor chamou. Se o par que chegou estava na `mfEncomenda`, tirar
   de lá.
   Modelo novo com **foto do fornecedor**: arquivo `fornecedor-<modelo>-<cor>.jpg`,
   `--recorte "1/1 45%"`, e vai para a `mfEncomenda`, nunca para a `mfProdutos`.
4. Conferir no navegador (regras 4, 5 e 6) e mandar as telas para o dono.
5. Push só na branch de teste; `main` só com ordem do dono (regra 1).

## Medição

- **Toda mensagem de WhatsApp que sai do site contém "pelo site"** (os 4 botões gerais e
  a função `zap()` dos produtos). Buscar "pelo site" no WhatsApp conta as conversas que o
  site trouxe. Não tirar essa frase.
- **Vercel Web Analytics:** não estava ligado em 27/set/2026. Ligar em Vercel → projeto
  `site-mf` → Analytics → Enable e **só depois** colar no `index.html`, antes do
  `</body>`, o trecho que o painel mostrar — colado antes, o script dá erro no console.
- Links com etiqueta, para o Analytics separar a origem: bio do Instagram →
  `https://site-mf-xi.vercel.app/?utm_source=instagram`; link mandado no WhatsApp →
  `https://site-mf-xi.vercel.app/?utm_source=whatsapp`.

## Como abrir para testar

```bash
python3 -m http.server 8000 --directory /home/wsl/Site-MF   # sobe o servidor local
explorer.exe "http://localhost:8000"                        # abre no navegador do Windows
```

Precisa do servidor: abrir o `index.html` com dois cliques funciona, mas alguns
navegadores bloqueiam o vídeo e as fontes em `file://`.

## Publicação

**Vercel**, ligado ao repositório **público** `teu157/Site-MF`. Cada push publica
sozinho em um ou dois minutos:

- push na **`main`** → atualiza o site de verdade
- push em **qualquer outra branch** → cria um endereço só daquela versão, para
  conferir antes de valer

O `.vercelignore` mantém a pasta `_build/` fora do que vai para o ar.

O GitHub Pages ficou de lado: dava no mesmo, mas com endereço mais comprido e uma
tela de configuração difícil de achar no celular.

## Regras de trabalho

1. **Nunca fazer commit nem push sozinho.** O dono decide quando gravar e publicar.
   Com o Vercel ligado, um push na `main` põe a mudança no ar em um ou dois minutos.

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

6. **Não quebrar os links de WhatsApp.** São 4 links `wa.me` fixos, mais 1 por produto, mais 1
   por modelo de encomenda (31 em out/2026) — o único caminho de venda. O número mora num lugar só (a constante
   `ZAP` no JavaScript), então produto novo não consegue apontar para o telefone errado.
   Depois de qualquer mexida, conferir que todos apontam para (38) 99750-6508 e que
   todos contêm "pelo site".

7. **Cuidar do peso.** Toda foto nova passa pelo `preparar-fotos.py` (ou pelo
   `_build/fotos-chromium.js`, na nuvem) antes de entrar.
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
