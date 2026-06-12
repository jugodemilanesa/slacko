const fs = require('fs');
const path = require('path');

function processDirectory(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            processDirectory(fullPath);
        } else if (fullPath.endsWith('.svelte')) {
            let content = fs.readFileSync(fullPath, 'utf8');
            let originalContent = content;
            
            // We want to replace the typical overline typography styles
            // font-family: var(--font-mono);
            // font-size: 0.62rem; (or 0.6rem, 0.65rem, etc)
            // letter-spacing: 0.2em; (or 0.18em, 0.22em, etc)
            // text-transform: uppercase;
            
            content = content.replace(/font-family:\s*var\(--font-mono\);\s*\n\s*font-size:\s*0\.6[0-9]?rem;\s*\n\s*letter-spacing:\s*0\.[0-9]+em;\s*\n\s*text-transform:\s*uppercase;/g,
                'font-family: var(--font-display);\n\t\tfont-size: 0.85rem;\n\t\tfont-weight: 500;'
            );

            // Also handle cases where font-size is just .6rem instead of .62
            // And what if the order is slightly different? 
            
            if (content !== originalContent) {
                fs.writeFileSync(fullPath, content, 'utf8');
                console.log('Updated', fullPath);
            }
        }
    }
}

processDirectory(path.join(__dirname, 'frontend/src'));
console.log('Done.');
