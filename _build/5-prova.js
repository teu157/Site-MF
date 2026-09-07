/* Prepara as fotos da secao "Ja saiu daqui".
 *
 * Duas ja passaram pelo 4-tapar.js (as de envio); as outras vem direto do que o
 * dono mandou. Sai tudo em fotos/miniaturas/prova-*.webp, na mesma medida e no
 * mesmo lugar que o preparar-fotos.py usa, para nao existir um segundo fluxo.
 *
 * Sao fotos de story (retrato ~9:16) e aparecem numa faixa de ate 300 px de
 * largura, entao 600 px cobre tela retina com folga.
 */
const { chromium } = require('/tmp/claude-0/-home-user-Site-MF/04c61a3e-439a-5efc-b851-dfec9cb3dc19/scratchpad/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const RAIZ = path.dirname(__dirname);
const UP = '/root/.claude/uploads/04c61a3e-439a-5efc-b851-dfec9cb3dc19/';
const TAPADAS = __dirname + '/tapadas/';
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const LARGURA = 600, QUALIDADE = 0.78;

// recorte: fracao a tirar de cada lado antes de redimensionar
const FOTOS = [
  { de: UP + '615bfaf3-image.jpg', para: 'prova-cliente-tenis-rosa',
    oque: 'cliente com o adidas rosa, "MF arrasou na qualidade"' },
  { de: UP + 'abbf3c86-image.jpg', para: 'prova-cliente-camisa-brasil',
    oque: 'cliente com a camisa do Brasil' },
  { de: UP + 'cebe609e-image.jpg', para: 'prova-estoque-brasil',
    oque: 'estoque de camisas do Brasil (mantem a faixa de preco)' },
  { de: UP + 'a3a8a568-image.png', para: 'prova-estoque-clubes',
    // a tarja de baixo dizia "manda no direct, sete lagoas e regiao", e o site
    // promete envio para todo o Brasil. Some a tarja, fica a foto.
    corte: { baixo: 0.175 },
    oque: 'estoque Atletico/Cruzeiro/Brasil (sem a tarja "sete lagoas")' },
  { de: TAPADAS + 'envio-valadares.png', para: 'prova-envio-valadares',
    oque: 'encomenda postada para Governador Valadares' },
  { de: TAPADAS + 'envio-vermelho.png', para: 'prova-envio-adidas-vermelho',
    oque: 'encomenda do adidas vermelho pronta para postar' },
];

(async () => {
  const browser = await chromium.launch({ executablePath: EXE });
  const page = await browser.newPage();
  const destino = path.join(RAIZ, 'fotos', 'miniaturas');
  fs.mkdirSync(destino, { recursive: true });
  let total = 0;

  for (const f of FOTOS) {
    const b64 = fs.readFileSync(f.de).toString('base64');
    const mime = f.de.endsWith('.png') ? 'image/png' : 'image/jpeg';
    const c = Object.assign({ cima: 0, baixo: 0, esq: 0, dir: 0 }, f.corte || {});
    const out = await page.evaluate(async ({ b64, mime, c, LARGURA, QUALIDADE }) => {
      const bin = atob(b64);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      const bmp = await createImageBitmap(new Blob([bytes], { type: mime }));
      const sx = Math.round(c.esq * bmp.width);
      const sy = Math.round(c.cima * bmp.height);
      const sl = Math.round(bmp.width * (1 - c.esq - c.dir));
      const sa = Math.round(bmp.height * (1 - c.cima - c.baixo));
      const l = Math.min(LARGURA, sl);
      const a = Math.round(sa * (l / sl));
      const cv = new OffscreenCanvas(l, a);
      const cx = cv.getContext('2d');
      cx.imageSmoothingEnabled = true;
      cx.imageSmoothingQuality = 'high';
      cx.drawImage(bmp, sx, sy, sl, sa, 0, 0, l, a);
      const blob = await cv.convertToBlob({ type: 'image/webp', quality: QUALIDADE });
      const buf = new Uint8Array(await blob.arrayBuffer());
      let s = '';
      for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
      return { b64: btoa(s), l, a };
    }, { b64, mime, c, LARGURA, QUALIDADE });

    const arq = path.join(destino, f.para + '.webp');
    const bytes = Buffer.from(out.b64, 'base64');
    fs.writeFileSync(arq, bytes);
    total += bytes.length;
    console.log(`  ${(f.para + '.webp').padEnd(36)} ${String(out.l + 'x' + out.a).padStart(9)}  ${(bytes.length / 1024).toFixed(0).padStart(3)} KB   ${f.oque}`);
  }
  console.log(`\n${FOTOS.length} fotos, ${(total / 1024).toFixed(0)} KB no total — todas abaixo da dobra, com loading="lazy"`);
  await browser.close();
})();
