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
            
            // Rename class names
            content = content.replace(/class="overline"/g, 'class="super-title"');
            content = content.replace(/\.overline \{/g, '.super-title {');
            // Handle variants like err-overline, hero-overline
            content = content.replace(/class="([a-z-]+)-overline"/g, 'class="$1-super-title"');
            content = content.replace(/\.([a-z-]+)-overline \{/g, '.$1-super-title {');
            
            // Handle specific SlackoTip nested CSS selectors
            content = content.replace(/\.overline/g, '.super-title');
            
            // And rename the JS variable in SlackoTip
            content = content.replace(/const overline:/g, 'const superTitle:');
            content = content.replace(/overline\[kind\]/g, 'superTitle[kind]');

            if (content !== originalContent) {
                fs.writeFileSync(fullPath, content, 'utf8');
                console.log('Renamed classes in', fullPath);
            }
        }
    }
}

processDirectory(path.join(__dirname, 'frontend/src'));
console.log('Done renaming overline to super-title.');
