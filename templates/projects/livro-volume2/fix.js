const fs = require('fs');
const path = require('path');

const base = 'C:/Users/marce/Documents/OpenCode_Ecosystem/livro_gemeos_odontologia/sections';
const parts = ['part1', 'part2', 'part3', 'part4'];

for (const part of parts) {
    const dir = path.join(base, part);
    const files = fs.readdirSync(dir);
    for (const file of files) {
        if (file.endsWith('.tex') && !file.includes('_')) {
            const p = path.join(dir, file);
            let content = fs.readFileSync(p, 'utf8');
            content = content.replace(/\\input\{([a-zA-Z0-9_]+)(\.tex)?\}/g, (match, p1) => {
                if (!p1.startsWith('sections/')) {
                    return `\\input{sections/${part}/${p1}.tex}`;
                }
                return match;
            });
            fs.writeFileSync(p, content, 'utf8');
        }
    }
}
console.log('Fixed LaTeX paths!');
