/* Faz o mesmo que o preparar-fotos.py, mas sem ffmpeg: usa o Chromium.
 *
 * Existe para a atualizacao semanal feita numa sessao do Claude Code na nuvem
 * (pelo celular ou pelo navegador), onde nao ha ffmpeg mas ha Chromium. No
 * computador de casa, o preparar-fotos.py continua sendo o caminho normal.
 *
 * Mesmas regras do preparar-fotos.py, para os dois gerarem o mesmo resultado:
 *   - le fotos-originais/  (fora do repositorio, esta no .gitignore)
 *   - 'Nike Air Max 90.jpg' vira o apelido 'nike-air-max-90'
 *   - grava fotos/miniaturas/<apelido>.webp  (500 px de largura, qualidade 75)
 *   - grava fotos/grandes/<apelido>.webp     (1400 px de largura, qualidade 80)
 *   - so encolhe: foto menor que o alvo fica do tamanho que esta
 *   - pula o que ja existe; para refazer:  --refazer
 *
 * USO
 *   node _build/fotos-chromium.js                      todas as fotos da pasta
 *   node _build/fotos-chromium.js "Nike X.jpg"         so essa
 *   node _build/fotos-chromium.js --recorte "4/3 70%" "Nike X.jpg"
 *
 * --recorte: FOTO EM PE DE CELULAR PRECISA DELE. A grade e a janela de ampliar
 * mostram so uma janela da foto (4/3 no tenis, 3/4 na camisa), e o resto nunca
 * aparece. Uma foto 2080 x 4624 viraria uma grande de 1400 x 3112 e ~450 KB, dois
 * tercos disso invisiveis. O recorte corta o arquivo exatamente na janela que o
 * site mostraria com o campo "recorte" da lista de produtos: "4/3 70%" = janela
 * 4/3, centrada na horizontal, 70% do caminho de cima para baixo (a mesma conta
 * do object-position do CSS). Recortado, o produto na lista fica SEM "recorte".
 *
 * HEIC (foto de iPhone) o Chromium nao le: converta para JPG antes.
 */
const fs = require('fs');
const path = require('path');

function carregarPlaywright() {
  for (const onde of ['playwright', '/opt/node22/lib/node_modules/playwright']) {
    try { return require(onde); } catch (e) { /* tenta o proximo */ }
  }
  console.error('PAROU: nao encontrei o Playwright (que abre o Chromium).');
  process.exit(1);
}

const RAIZ = path.join(__dirname, '..');
const ORIGINAIS = path.join(RAIZ, 'fotos-originais');
const MEDIDAS = [
  { pasta: path.join(RAIZ, 'fotos', 'miniaturas'), largura: 500, qualidade: 75 },
  { pasta: path.join(RAIZ, 'fotos', 'grandes'), largura: 1400, qualidade: 80 },
];
const TIPOS = { '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
                '.webp': 'image/webp', '.bmp': 'image/bmp' };
const LIMITE_AVISO = 200 * 1024;

/* igual ao apelido() do preparar-fotos.py */
function apelido(arquivo) {
  const base = path.parse(arquivo).name
    .normalize('NFKD').replace(/\p{M}/gu, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
  return base || 'foto';
}

/* "4/3 70%" -> { razao: 1.333, y: 0.70 } */
function lerRecorte(texto) {
  const m = /^\s*(\d+)\s*\/\s*(\d+)\s+(\d{1,3})%\s*$/.exec(texto || '');
  if (!m || +m[2] === 0 || +m[3] > 100) {
    console.error('PAROU: --recorte espera algo como "4/3 70%" e recebeu: ' + texto);
    process.exit(1);
  }
  return { razao: +m[1] / +m[2], y: +m[3] / 100 };
}

const kb = (bytes) => (bytes / 1024).toFixed(0).padStart(6) + ' KB';

(async () => {
  const args = process.argv.slice(2);
  const refazer = args.includes('--refazer');
  let recorte = null;
  const i = args.indexOf('--recorte');
  if (i >= 0) { recorte = lerRecorte(args[i + 1]); args.splice(i, 2); }
  const escolhidos = args.filter((a) => !a.startsWith('--'));

  if (!fs.existsSync(ORIGINAIS)) {
    fs.mkdirSync(ORIGINAIS, { recursive: true });
    console.log('Criei a pasta fotos-originais/. Ponha as fotos nela e rode de novo.');
    return;
  }
  MEDIDAS.forEach((m) => fs.mkdirSync(m.pasta, { recursive: true }));

  let arquivos = fs.readdirSync(ORIGINAIS).sort()
    .filter((f) => fs.statSync(path.join(ORIGINAIS, f)).isFile());
  if (escolhidos.length) {
    const faltam = escolhidos.filter((f) => !arquivos.includes(f));
    if (faltam.length) { console.error('PAROU: nao achei em fotos-originais/: ' + faltam.join(', ')); process.exit(1); }
    arquivos = escolhidos;
  }
  if (!arquivos.length) { console.log('A pasta fotos-originais/ esta vazia.'); return; }

  const { chromium } = carregarPlaywright();
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage();

  const usados = {}, linhas = [], erros = [];
  let pulados = 0;

  for (const arq of arquivos) {
    const ext = path.extname(arq).toLowerCase();
    if (!TIPOS[ext]) {
      erros.push(arq + ': formato que o Chromium nao le' + (ext === '.heic' ? ' (converta para JPG)' : ''));
      continue;
    }
    const nome = apelido(arq);
    if (usados[nome]) { erros.push(usados[nome] + ' e ' + arq + ' viram o mesmo nome (' + nome + ')'); continue; }
    usados[nome] = arq;

    const saidas = MEDIDAS.map((m) => path.join(m.pasta, nome + '.webp'));
    if (!refazer && saidas.every((s) => fs.existsSync(s))) { pulados++; continue; }

    const entrada = path.join(ORIGINAIS, arq);
    const dataUrl = 'data:' + TIPOS[ext] + ';base64,' + fs.readFileSync(entrada).toString('base64');

    /* o navegador desenha a foto ja virada pelo EXIF, corta, reduz e codifica */
    const r = await pagina.evaluate(async ({ dataUrl, medidas, recorte }) => {
      const img = new Image();
      img.src = dataUrl;
      await img.decode();
      const W = img.naturalWidth, H = img.naturalHeight;

      /* janela de origem: a foto toda, ou o pedaco que o object-fit:cover com
         object-position 50% Y% mostraria */
      let sx = 0, sy = 0, sw = W, sh = H;
      if (recorte) {
        if (W / H > recorte.razao) { sw = Math.round(H * recorte.razao); sx = Math.round((W - sw) / 2); }
        else { sh = Math.round(W / recorte.razao); sy = Math.round((H - sh) * recorte.y); }
      }

      const versoes = medidas.map(({ largura, qualidade }) => {
        const l = Math.min(largura, sw);
        let a = Math.round(sh * l / sw);
        a -= a % 2;  /* altura par, como o -2 do ffmpeg */
        const tela = document.createElement('canvas');
        tela.width = l; tela.height = a;
        const ctx = tela.getContext('2d');
        ctx.imageSmoothingQuality = 'high';
        ctx.drawImage(img, sx, sy, sw, sh, 0, 0, l, a);
        return { base64: tela.toDataURL('image/webp', qualidade / 100).split(',')[1], l, a };
      });
      return { versoes, alta: !recorte && H / W > 1.6 };
    }, { dataUrl, medidas: MEDIDAS.map(({ largura, qualidade }) => ({ largura, qualidade })), recorte });

    r.versoes.forEach((v, n) => fs.writeFileSync(saidas[n], Buffer.from(v.base64, 'base64')));
    linhas.push({ nome, orig: fs.statSync(entrada).size, alta: r.alta,
                  mini: fs.statSync(saidas[0]).size, grande: fs.statSync(saidas[1]).size,
                  medida: r.versoes[1].l + 'x' + r.versoes[1].a });
    console.log('  ok  ' + nome + '  (grande ' + r.versoes[1].l + 'x' + r.versoes[1].a + ')');
  }
  await navegador.close();

  if (linhas.length) {
    console.log('\n' + 'foto'.padEnd(38) + '  original  miniatura     grande');
    console.log('-'.repeat(72));
    for (const l of linhas) {
      console.log(l.nome.slice(0, 38).padEnd(38) + kb(l.orig) + kb(l.mini) + kb(l.grande)
                  + (l.grande > LIMITE_AVISO ? '  <-- pesada' : ''));
    }
    const altas = linhas.filter((l) => l.alta);
    if (altas.length) {
      console.log('\nFoto em pe sem --recorte: ' + altas.map((l) => l.nome).join(', '));
      console.log('O site so mostra uma janela dela. Veja --recorte no comeco deste arquivo.');
    }
  }
  if (pulados) console.log('\n' + pulados + ' foto(s) ja estavam prontas e foram puladas (use --refazer).');
  if (erros.length) { console.log('\nPROBLEMAS:'); erros.forEach((e) => console.log('  - ' + e)); }
})();
