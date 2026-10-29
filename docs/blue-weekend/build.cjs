const fs = require('node:fs');
const path = require('node:path');
const dir = fs.existsSync(path.join(__dirname, 'dist/index.html')) ? path.join(__dirname, 'dist') : __dirname;
let html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
html = html.replace('<link rel="stylesheet" href="styles.css">', () => '<style>\n' + fs.readFileSync(path.join(dir, 'styles.css'), 'utf8') + '\n</style>');
for (const file of ['model.js', 'app.js']) {
  const script = fs.readFileSync(path.join(dir, file), 'utf8').replace(/<\/script/gi, '<\\/script');
  html = html.replace(`<script src="${file}" defer></script>`, () => `<script>document.addEventListener('DOMContentLoaded', function () {\n${script}\n});</script>`);
}
html = html.replace('href="offline.html" download="蓝色的周末-离线面试演示.html"', 'href="#cover"');
html = html.replace('下载离线演示 ↓', '当前为离线演示 · 回到首页 ↑');
fs.writeFileSync(path.join(dir, 'offline.html'), html, 'utf8');
console.log('Built offline.html with embedded CSS, JavaScript and illustration.');
