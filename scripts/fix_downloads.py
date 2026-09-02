import os
import glob

# Fix all HTML files
html_files = glob.glob('templates/*.html')
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '// AUTO DOWNLOAD FIX FOR SOME BROWSERS' in content:
        # We need to remove the block
        # const link = document.createElement('a');
        # link.href = currentPdfUrl;
        # link.download = currentPdfFilename;
        # document.body.appendChild(link);
        # link.click();
        # document.body.removeChild(link);
        
        # Simple string replacement
        bad_block = '''                    // AUTO DOWNLOAD FIX FOR SOME BROWSERS
                    const link = document.createElement('a');
                    link.href = currentPdfUrl;
                    link.download = currentPdfFilename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);'''
        
        bad_block2 = '''                    // AUTO DOWNLOAD FIX FOR SOME BROWSERS\n                    const link = document.createElement('a');\n                    link.href = currentPdfUrl;\n                    link.download = currentPdfFilename;\n                    document.body.appendChild(link);\n                    link.click();\n                    document.body.removeChild(link);'''
        
        if bad_block in content:
            content = content.replace(bad_block, '')
            print(f"Fixed {filepath}")
        elif bad_block2 in content:
            content = content.replace(bad_block2, '')
            print(f"Fixed {filepath} (v2)")
        else:
            # Maybe slightly different whitespace
            import re
            content, n = re.subn(r'\s*// AUTO DOWNLOAD FIX FOR SOME BROWSERS.*?document\.body\.removeChild\(link\);', '', content, flags=re.DOTALL)
            if n > 0:
                print(f"Fixed {filepath} via regex")
                
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

# Fix app.js
appjs_path = 'static/js/app.js'
with open(appjs_path, 'r', encoding='utf-8') as f:
    appjs = f.read()

bad_appjs = '''                    if (pdfUrl) {
                        // Direct download trigger (avoids browser popup blocker)
                        const linkPdf = document.createElement('a');
                        linkPdf.href = pdfUrl;
                        linkPdf.download = result.pdf_filename;
                        document.body.appendChild(linkPdf);
                        linkPdf.click();
                        document.body.removeChild(linkPdf);
                    }'''
import re
appjs, n = re.subn(r'\s*if\s*\(pdfUrl\)\s*\{\s*// Direct download trigger.*?document\.body\.removeChild\(linkPdf\);\s*\}', r'''
                    if (pdfUrl) {
                        // Instead of direct download, show the preview modal if it exists
                        if (typeof showPdfPreview === "function") {
                            showPdfPreview(pdfUrl, result.pdf_filename);
                        } else {
                            const modal = document.getElementById("pdfPreviewModal");
                            if (modal) {
                                document.getElementById("modalPreviewTitle").textContent = result.pdf_filename || "Document";
                                document.getElementById("pdfPreviewIframe").src = pdfUrl;
                                document.getElementById("btnModalDownloadPDF").href = pdfUrl;
                                modal.style.display = "flex";
                            }
                        }
                    }''', appjs, flags=re.DOTALL)
if n > 0:
    print("Fixed app.js direct download")
    with open(appjs_path, 'w', encoding='utf-8') as f:
        f.write(appjs)
        
