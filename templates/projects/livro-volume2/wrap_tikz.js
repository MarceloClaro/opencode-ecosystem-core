const fs = require('fs');
const path = require('path');

const baseDir = 'C:/Users/marce/Documents/OpenCode_Ecosystem/livro_gemeos_odontologia/sections';
const parts = ['part1', 'part2', 'part3', 'part4'];

parts.forEach(part => {
    const partPath = path.join(baseDir, part);
    if (!fs.existsSync(partPath)) return;
    
    fs.readdirSync(partPath).forEach(f => {
        if (!f.endsWith('.tex')) return;
        const filePath = path.join(partPath, f);
        let content = fs.readFileSync(filePath, 'utf8');
        
        let changed = false;
        let idx = 0;
        
        while ((idx = content.indexOf('\\begin{tikzpicture}', idx)) !== -1) {
            // Check if it is already wrapped in adjustbox or resizebox in the last 150 chars
            const lookback = content.substring(Math.max(0, idx - 150), idx);
            if (lookback.includes('\\begin{adjustbox}') || lookback.includes('\\resizebox')) {
                idx += 19;
                continue;
            }
            
            // Find corresponding \end{tikzpicture}
            const endIdx = content.indexOf('\\end{tikzpicture}', idx);
            if (endIdx === -1) {
                idx += 19;
                continue;
            }
            
            const before = content.substring(0, idx);
            let tikzAround = content.substring(idx, endIdx + 17);
            const after = content.substring(endIdx + 17);
            
            // Insert font=\footnotesize into the tikzpicture options
            if (tikzAround.startsWith('\\begin{tikzpicture}[')) {
                tikzAround = tikzAround.replace('\\begin{tikzpicture}[', '\\begin{tikzpicture}[font=\\footnotesize, ');
            } else {
                tikzAround = tikzAround.replace('\\begin{tikzpicture}', '\\begin{tikzpicture}[font=\\footnotesize]');
            }
            
            // Wrap in adjustbox
            content = before + '\\begin{adjustbox}{max width=\\textwidth}\n' + tikzAround + '\n\\end{adjustbox}' + after;
            changed = true;
            
            // Set idx past this newly wrapped block
            idx = before.length + tikzAround.length + 80;
        }
        
        if (changed) {
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`Successfully wrapped diagram in adjustbox with font=\\footnotesize in ${part}/${f}`);
        }
    });
});
