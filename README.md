# MF Sportswear

Site de vitrine da MF Sportswear — tênis e camisas importados.
Venda feita por WhatsApp: (38) 99750-6508 · [@mfsports_wear](https://instagram.com/mfsports_wear)

## Como funciona

Site estático: HTML, CSS e JavaScript comuns. Não precisa de build, instalação nem
programa nenhum. É uma pasta de arquivos que o navegador abre direto.

Para ver no computador:

```bash
python3 -m http.server 8000
```

e abrir `http://localhost:8000`.

## Publicar de graça no GitHub Pages

1. Neste repositório, vá em **Settings → Pages**
2. Em *Source*, escolha **Deploy from a branch**
3. Branch: **main**, pasta: **/ (root)** → **Save**
4. Em um ou dois minutos o site fica no ar em `https://<seu-usuario>.github.io/<nome-do-repo>/`

## Estrutura

```
index.html          o site inteiro: HTML, CSS e JavaScript
fontes/             as letras usadas no site
fotos/
  miniaturas/       fotos da grade de produtos (500 px)
  grandes/          fotos que aparecem ao ampliar (1400 px)
video/hero.mp4      o vídeo do topo
preview.jpg         imagem que aparece quando o link é compartilhado no WhatsApp
preparar-fotos.py   prepara fotos novas do celular para o site
_build/             scripts da migração de 2026 (não fazem parte do site)
```

**O site é a pasta inteira, não só o `index.html`.** Para mandar para alguém, mandar
a pasta (ou um ZIP dela).

## Adicionar um produto

1. Copiar as fotos para `fotos-originais/` e rodar `python3 preparar-fotos.py`
2. Abrir o `index.html` num editor de texto e achar a lista `id="mfProdutos"`
3. Acrescentar um bloco:

```json
{"tipo": "tenis", "nome": "Nike Air Max 90",
 "texto": "Frase curta que aparece embaixo do nome.",
 "foto": "nike-air-max-90",
 "alt": "Descrição da foto para quem não enxerga"}
```

O campo `foto` é o apelido que o `preparar-fotos.py` mostrou no fim. O site monta o
caminho das duas versões sozinho.
