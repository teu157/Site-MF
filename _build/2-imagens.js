/* Converte as imagens extraidas para WebP no tamanho que a tela realmente usa.
 *
 * Nao ha Pillow, sharp nem cwebp neste ambiente, mas ha um Chromium completo
 * (o do Playwright). O proprio navegador decodifica e recodifica: createImageBitmap
 * -> OffscreenCanvas -> convertToBlob({type:'image/webp'}). Mesmo codificador que
 * o cliente usa para exibir, entao o resultado e exatamente o que ele vai ver.
 *
 * Medidas iguais as do preparar-fotos.py, para o script do dono seguir valendo:
 *   miniaturas  500 px de largura, qualidade 75   (a grade)
 *   grandes    1400 px de largura, qualidade 80   (so ao ampliar)
 */
const { chromium } = require('/tmp/claude-0/-home-user-Site-MF/04c61a3e-439a-5efc-b851-dfec9cb3dc19/scratchpad/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const RAIZ = __dirname + '/..';
const BRUTO = RAIZ + '/_build/bruto';
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

// destino, largura alvo, qualidade.  largura 0 = manter o original.
const AVULSAS = [
  // exibido a 34px de altura -> 3x para telas retina
  ['logo-coroa.png',  'fotos/logo-coroa.webp',   176, 0.90],
  // exibido a 15px de altura, e texto fino: 3x
  ['logo-texto.png',  'fotos/logo-texto.webp',   323, 0.90],
  // exibido a 158px de largura -> 2x
  ['logo-rodape.png', 'fotos/logo-rodape.webp',  316, 0.90],
  // primeiro quadro do video: e a primeira coisa que o cliente ve
  ['hero-poster.jpg', 'fotos/hero-poster.webp',  1024, 0.78],
  ['matheus.jpg',     'fotos/matheus.webp',      866, 0.78],
];

(async () => {
  const browser = await chromium.launch({ executablePath: EXE });
  const page = await browser.newPage();

  async function converter(entradaAbs, saidaRel, largura, qualidade) {
    const b64 = fs.readFileSync(entradaAbs).toString('base64');
    const mime = entradaAbs.endsWith('.png') ? 'image/png' : 'image/jpeg';
    const out = await page.evaluate(async ({ b64, mime, largura, qualidade }) => {
      const bin = atob(b64);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      const bmp = await createImageBitmap(new Blob([bytes], { type: mime }));
      // nunca aumenta: foto menor que o alvo fica como esta
      const l = (!largura || bmp.width <= largura) ? bmp.width : largura;
      const a = Math.round(bmp.height * (l / bmp.width));
      const cv = new OffscreenCanvas(l, a);
      const cx = cv.getContext('2d');
      cx.imageSmoothingEnabled = true;
      cx.imageSmoothingQuality = 'high';
      cx.drawImage(bmp, 0, 0, l, a);
      const blob = await cv.convertToBlob({ type: 'image/webp', quality: qualidade });
      const buf = new Uint8Array(await blob.arrayBuffer());
      let s = '';
      for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
      return { b64: btoa(s), l, a, orig: [bmp.width, bmp.height] };
    }, { b64, mime, largura, qualidade });

    const destino = path.join(RAIZ, saidaRel);
    fs.mkdirSync(path.dirname(destino), { recursive: true });
    const bytes = Buffer.from(out.b64, 'base64');
    fs.writeFileSync(destino, bytes);
    const antes = fs.statSync(entradaAbs).size;
    console.log(
      `  ${saidaRel.padEnd(42)} ${String(out.orig[0] + 'x' + out.orig[1]).padStart(10)} -> ` +
      `${String(out.l + 'x' + out.a).padStart(10)}  ${(antes / 1024).toFixed(0).padStart(4)} KB -> ` +
      `${(bytes.length / 1024).toFixed(0).padStart(4)} KB`);
    return { antes, depois: bytes.length };
  }

  let antes = 0, depois = 0;
  console.log('AVULSAS (logos, poster, foto do Matheus)');
  for (const [origem, saida, l, q] of AVULSAS) {
    const r = await converter(path.join(BRUTO, 'avulsas', origem), saida, l, q);
    antes += r.antes; depois += r.depois;
  }

  console.log('\nPRODUTOS — miniatura 500px q75 (a grade)');
  const produtos = fs.readdirSync(path.join(BRUTO, 'produtos')).sort();
  for (const f of produtos) {
    const nome = f.replace(/\.[^.]+$/, '');
    const r = await converter(path.join(BRUTO, 'produtos', f), `fotos/miniaturas/${nome}.webp`, 500, 0.75);
    antes += r.antes; depois += r.depois;
  }

  console.log('\nPRODUTOS — grande 1400px q80 (so ao ampliar)');
  for (const f of produtos) {
    const nome = f.replace(/\.[^.]+$/, '');
    await converter(path.join(BRUTO, 'produtos', f), `fotos/grandes/${nome}.webp`, 1400, 0.80);
  }

  console.log(`\nPeso que o cliente baixa ao abrir + rolar: ${(antes / 1024).toFixed(0)} KB -> ${(depois / 1024).toFixed(0)} KB`);
  console.log(`Economia: ${((antes - depois) / 1024).toFixed(0)} KB`);
  await browser.close();
})();
