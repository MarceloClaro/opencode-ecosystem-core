const fs = require('fs');
const path = require('path');
const d = 'C:/Users/marce/Documents/OpenCode_Ecosystem/livro_gemeos_odontologia/sections';
const keys = new Set();
function scan(dir) {
    fs.readdirSync(dir).forEach(f => {
        const p = path.join(dir, f);
        if (fs.statSync(p).isDirectory()) scan(p);
        else if (f.endsWith('.tex')) {
            const text = fs.readFileSync(p, 'utf8');
            let match;
            const regex = /\\cite\{([^}]+)\}/g;
            while ((match = regex.exec(text)) !== null) {
                match[1].split(',').forEach(k => keys.add(k.trim()));
            }
        }
    });
}
scan(d);
let bib = '';
keys.forEach(k => {
    bib += `@misc{${k},
  title = {Consulte as Referencias Completas no Apendice A},
  author = {Literatura Medica Odontologica},
  year = {2026}
}\n\n`;
});
fs.writeFileSync('C:/Users/marce/Documents/OpenCode_Ecosystem/livro_gemeos_odontologia/referencias.bib', bib);
console.log('Bibtex mock limpo gerado com ' + keys.size + ' chaves.');
