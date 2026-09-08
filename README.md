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

## Publicação

O site é publicado de graça pelo **Vercel**, ligado a este repositório. Não é
preciso fazer nada a cada mudança: todo push publica sozinho em um ou dois minutos.

- push na **`main`** → atualiza o site de verdade
- push em **qualquer outra branch** → cria um endereço só daquela versão, útil
  para conferir antes de valer

Se um dia precisar refazer a ligação: em `vercel.com/new`, importar o repositório
`Site-MF`. Não tem nada para configurar — é HTML puro, sem build.

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
