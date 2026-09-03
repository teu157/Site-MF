# MF Sportswear — instruções do projeto

## O que é este projeto

Site de **vitrine** da MF Sportswear (tênis e camisas importados). Não é loja virtual:
não tem carrinho, cadastro nem pagamento. O site existe para mostrar os produtos e
empurrar o cliente para o WhatsApp **(38) 99750-6508** ou para o Instagram
**@mfsports_wear**, onde a venda acontece de fato.

O dono é leigo em programação (ver o arquivo global `~/.claude/CLAUDE.md` para como
explicar as coisas).

## Como o site está montado

Um único arquivo `index.html` de **6,6 MB** que funciona sozinho. Sem `package.json`,
sem dependências, sem etapa de build — o navegador monta tudo.

Por dentro ele tem duas partes bem diferentes, e saber disso muda o que dá para fazer:

- **`<script type="__bundler/template">` — ~57 KB de HTML legível.** É o site de verdade:
  textos, preços, nomes de produtos, links de WhatsApp, CSS e layout. **É aqui que se
  edita.** Está guardado como uma string JSON dentro do HTML, então não dá para editar
  no bloco de notas — é preciso script (ler o JSON, alterar, gravar de volta).

- **`<script type="__bundler/manifest">` — o resto dos 6,6 MB.** 32 arquivos embutidos
  (15 JPEG, 3 PNG, 1 MP4, 10 fontes woff2, 3 JS), comprimidos e em base64, cada um
  identificado por um UUID que o template referencia. Trocar uma foto exige comprimir a
  nova e reencaixá-la aqui — trabalhoso, mas possível.

Um script no topo do arquivo descompacta tudo no navegador (`DecompressionStream`) e
monta a página. Enquanto isso a tela mostra "MF" e o aviso *Unpacking…*.

## Como abrir para testar

```bash
python3 -m http.server 8000 --directory /home/wsl/Site-MF   # sobe o servidor local
explorer.exe "http://localhost:8000"                        # abre no navegador do Windows
```

Testado e funcionando neste ambiente (WSL2). O 404 de `/favicon.ico` no log é normal —
o projeto não tem favicon.

## Publicação

GitHub Pages, repositório **público** `teu157/Site-MF`, branch `main`, pasta raiz.
Em 02/09/2026 o Pages **ainda não estava ativado**: `https://teu157.github.io/Site-MF/`
respondia 404. Os passos para ligar estão no `README.md`.

## Regras de trabalho

1. **Nunca fazer commit nem push sozinho.** O dono decide quando gravar e publicar.
   Com o Pages ativado, um push põe a mudança no ar em um ou dois minutos.

2. **Copiar o `index.html` antes de qualquer edição.** É arquivo único, gerado por uma
   ferramenta que não está neste repositório. Se corromper, não há como remontar — perde
   o site inteiro, com fotos e vídeo.

3. **Nunca reescrever o `index.html` do zero.** Só edições cirúrgicas no trecho exato.
   Reescrever significa jogar fora as 32 mídias embutidas.

4. **Só afirmar que funcionou depois de ver no navegador.** A página se monta em tempo
   de execução; um erro de sintaxe no template só aparece ao abrir. "Salvou sem erro"
   não é prova de nada aqui. Se aparecer uma faixa vermelha no rodapé (`#__bundler_err`),
   o bundle falhou ao descompactar — ler o console do navegador.

5. **Testar também em largura de celular.** A maior parte do tráfego vem do link do
   Instagram, ou seja, de telefone.

6. **Não quebrar os links de WhatsApp.** São 13 links `wa.me` — o único caminho de venda.
   Depois de qualquer mexida, conferir que continuam apontando para (38) 99750-6508.

7. **Cuidar do peso.** 6,6 MB já é pesado no 4G, e página lenta faz o cliente desistir
   antes de ver o produto. Comprimir toda imagem nova antes de embutir.

8. **O repositório é público.** Nunca colocar senha, chave de acesso ou dado sigiloso em
   arquivo deste projeto — vai para a internet junto.
