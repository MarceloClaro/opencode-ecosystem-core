const fs = require('fs');
const path = require('path');

const dir = 'C:\\Users\\marce\\Documents\\OpenCode_Ecosystem\\livro-opencode\\capitulos';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.tex') && !f.includes('_corrigido'));

let totalFixed = 0;

for (const file of files) {
    const filePath = path.join(dir, file);
    let content = fs.readFileSync(filePath, 'utf8');

    // Regex approach:
    // Match \begin{tabular}{...} ... \end{tabular}
    // But exclude if already inside adjustbox or resizebox.
    // Instead of regex, let's use a state machine over lines.

    const lines = content.split('\n');
    const newLines = [];
    let modified = false;
    let stack = [];

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];

        if (line.includes('\\begin{tabular}')) {
            // Check if previously wrapped by adjustbox or resizebox
            let alreadyWrapped = false;
            if (i > 0 && (lines[i-1].includes('adjustbox') || lines[i-1].includes('resizebox'))) {
                alreadyWrapped = true;
            }
            if (line.includes('adjustbox') || line.includes('resizebox')) {
                alreadyWrapped = true;
            }
            // Check if there's an open resizebox 2 lines ago
            if (i > 1 && (lines[i-2].includes('resizebox') || lines[i-2].includes('adjustbox'))) {
                alreadyWrapped = true;
            }

            if (!alreadyWrapped) {
                newLines.push('\\begin{adjustbox}{max width=\\textwidth}');
                stack.push(true); // remember we added an adjustbox
                modified = true;
                totalFixed++;
            } else {
                stack.push(false); // didn't add
            }
        }

        newLines.push(line);

        if (line.includes('\\end{tabular}')) {
            let added = stack.pop();
            if (added) {
                newLines.push('\\end{adjustbox}');
            }
        }
    }

    if (modified) {
        fs.writeFileSync(filePath, newLines.join('\n'), 'utf8');
        console.log(`Corrigido: ${file}`);
    }
}

console.log(`Total de tabelas protegidas com adjustbox: ${totalFixed}`);
