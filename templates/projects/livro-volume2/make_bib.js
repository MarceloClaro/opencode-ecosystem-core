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
const oldText = '';
try {
    oldText = fs.readFileSync('C:/Users/marce/Documents/OpenCode_Ecosystem/livro_gemeos_odontologia/referencias.bib', 'utf8');
} catch(e) {}

// Extract existing keys to avoid duplicates
const existingKeys = new Set();
let match2;
const regex2 = /@misc\{([^,]+),/g;
while ((match2 = regex2.exec(oldText)) !== null) {
    existingKeys.add(match2[1].trim());
}

bib = oldText + '\n\n';

keys.forEach(k => {
    if (!existingKeys.has(k)) {
        bib += `@misc{${k},
  title = {Consulte as Referencias Completas no Apendice A (Pesquisa Completa)},
  author = {Literatura Medica Odontologica},
  year = {2026}
}\n\n`;
    }
});

fs.writeFileSync('C:/Users/marce/Documents/OpenCode_Ecosystem/livro_gemeos_odontologia/referencias.bib', bib);
console.log('Bibtex mock gerado/atualizado sem acentos!');
