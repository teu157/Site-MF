/* Tapa os dados pessoais que sobraram nas duas fotos de etiqueta de envio.
 *
 * Retangulo OPACO, nao desfoque: texto pequeno borrado as vezes volta a ser
 * legivel quando alguem forca contraste e nitidez. Retangulo solido nao tem volta.
 *
 * Coordenadas em fracao da largura/altura, lidas sobre uma grade de porcentagem.
 * O que fica de fora de proposito: o codigo de barras de rastreio (consultar
 * rastreio mostra so cidade e status, que a legenda ja diz) e o CNPJ dos Correios
 * 34.028.316/0001-03, que e publico.
 */
const { chromium } = require('/tmp/claude-0/-home-user-Site-MF/04c61a3e-439a-5efc-b851-dfec9cb3dc19/scratchpad/node_modules/playwright');
const fs = require('fs');
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const UP = '/root/.claude/uploads/04c61a3e-439a-5efc-b851-dfec9cb3dc19/';
const SAI = __dirname + '/tapadas/';

const TRABALHO = [
  {
    arquivo: '4457b616-image.png',
    saida: 'envio-valadares.png',
    tapar: [
      // O nome do dono e o codigo de barras de rastreio ficam a mostra: ele pediu,
      // e sao dados dele. Some so o CPF dele, o endereco de remetente dele e tudo
      // que identifica a destinataria.

      // codigo 2D da etiqueta: esses codigos costumam carregar o endereco do
      // destinatario dentro, entao ele sai junto com o texto
      { x: 0.245, y: 0.130, l: 0.180, a: 0.110, oque: 'datamatrix da etiqueta' },
      // bloco do destinatario + o codigo de barras do CEP logo abaixo
      { x: 0.095, y: 0.330, l: 0.380, a: 0.090, oque: 'bloco do destinatario + barras do CEP' },
      // so as tres linhas de endereco do remetente. A linha do nome, logo acima,
      // fica de fora de proposito
      { x: 0.085, y: 0.454, l: 0.130, a: 0.046, oque: 'endereco do remetente (nome fica visivel)' },

      // DACE inteira: chave de acesso (que sozinha permite consultar a declaracao
      // e ler tudo de novo), os dois CPF, os enderecos e os dados da destinataria.
      // O nome do dono ja aparece na etiqueta de cima, entao nao se perde nada.
      { x: 0.030, y: 0.605, l: 0.520, a: 0.237, oque: 'DACE inteira' },
    ],
  },
  {
    arquivo: '2bd70400-image.png',
    saida: 'envio-vermelho.png',
    tapar: [
      { x: 0.160, y: 0.285, l: 0.125, a: 0.070, oque: 'datamatrix da etiqueta' },
      { x: 0.055, y: 0.420, l: 0.315, a: 0.085, oque: 'bloco do destinatario' },
      { x: 0.060, y: 0.5105, l: 0.310, a: 0.0485, oque: 'endereco do remetente (nome fica visivel)' },

      { x: 0.045, y: 0.598, l: 0.395, a: 0.152, oque: 'DACE inteira' },
      // QR da DACE: carrega os dados da declaracao, inclusive do destinatario
      { x: 0.075, y: 0.820, l: 0.110, a: 0.070, oque: 'QR-code da DACE' },
    ],
  },
];

(async () => {
  fs.mkdirSync(SAI, { recursive: true });
  const browser = await chromium.launch({ executablePath: EXE });
  const page = await browser.newPage();

  for (const t of TRABALHO) {
    const b64 = fs.readFileSync(UP + t.arquivo).toString('base64');
    const out = await page.evaluate(async ({ b64, tapar }) => {
      const bin = atob(b64);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      const bmp = await createImageBitmap(new Blob([bytes], { type: 'image/png' }));
      const cv = new OffscreenCanvas(bmp.width, bmp.height);
      const cx = cv.getContext('2d');
      cx.drawImage(bmp, 0, 0);
      cx.fillStyle = '#000';
      for (const r of tapar) {
        cx.fillRect(Math.round(r.x * bmp.width), Math.round(r.y * bmp.height),
                    Math.round(r.l * bmp.width), Math.round(r.a * bmp.height));
      }
      const blob = await cv.convertToBlob({ type: 'image/png' });
      const buf = new Uint8Array(await blob.arrayBuffer());
      let s = '';
      for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
      return { b64: btoa(s), w: bmp.width, h: bmp.height };
    }, { b64, tapar: t.tapar });

    fs.writeFileSync(SAI + t.saida, Buffer.from(out.b64, 'base64'));
    console.log(`${t.saida}  ${out.w}x${out.h}`);
    for (const r of t.tapar) console.log(`    tapado: ${r.oque}`);
  }
  await browser.close();
})();
