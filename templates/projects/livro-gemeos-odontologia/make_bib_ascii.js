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
                match[1].split(',').forEach(k => {
                    let cleanKey = k.replace(/[^\x00-\x7F]/g, '').trim().toLowerCase();
                    if (cleanKey) keys.add(cleanKey);
                });
            }
        }
    });
}
scan(d);
let bib = '';
let counter = 1000;
keys.forEach(k => {
    bib += `@misc{${k},
  title = {Apendice A},
  author = {Literatura_${counter}},
  year = {${counter}}
}\n\n`;
    counter++;
});
fs.writeFileSync('C:/Users/marce/Documents/OpenCode_Ecosystem/livro_gemeos_odontologia/referencias.bib', bib, 'ascii');
console.log('Bibtex mock gerado perfeitamente limpo: ' + keys.size + ' chaves.');
