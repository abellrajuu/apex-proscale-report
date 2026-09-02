import glob
html_files = glob.glob('templates/*.html')
for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # We will inject android detection in showPdfPreview
    android_fix = '''
                // ANDROID WEBVIEW FIX
                if (/Android/i.test(navigator.userAgent)) {
                    iframe.style.display = 'none';
                    const msg = document.getElementById('androidFixMsg') || document.createElement('div');
                    msg.id = 'androidFixMsg';
                    msg.style.padding = '40px';
                    msg.style.textAlign = 'center';
                    msg.style.color = '#fff';
                    msg.innerHTML = '<i class=\"fa-solid fa-file-pdf\" style=\"font-size:48px; color:#38bdf8; margin-bottom:16px;\"></i><br><h3>PDF Generated Successfully!</h3><p>Android WebView does not support inline PDF previews.</p><p>Please tap the <b>Download</b> button above to view your document.</p>';
                    iframe.parentNode.appendChild(msg);
                } else {
                    iframe.src = pdfUrl;
                }
'''
    if 'iframe.src = pdfUrl;' in content and 'ANDROID WEBVIEW FIX' not in content:
        content = content.replace('iframe.src = pdfUrl;', android_fix)
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Fixed Android preview in {f}")
