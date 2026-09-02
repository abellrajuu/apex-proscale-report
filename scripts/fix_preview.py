with open('static/js/app.js', 'r', encoding='utf-8') as f:
    appjs = f.read()

preview_logic = '''
    const btnPreview = document.getElementById('btnPreviewForm');
    if (btnPreview) {
        btnPreview.addEventListener('click', async (e) => {
            e.preventDefault();
            const btnPrev = document.getElementById('btnPreviewForm');
            const origHTML = btnPrev.innerHTML;
            btnPrev.disabled = true;
            btnPrev.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Preparing...';
            
            // Build full payload just like submit
            const formData = new FormData(form);
            const payload = Object.fromEntries(formData.entries());
            payload.grid_data = extractGridData ? extractGridData() : [];
            payload.routine_tests = extractRoutineTests ? extractRoutineTests() : [];
            payload.timestamp = new Date().toISOString();
            
            try {
                const res = await fetch(${getServerBaseUrl()}/api/submit, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                btnPrev.disabled = false;
                btnPrev.innerHTML = origHTML;
                
                if (result.status === 'success' && result.pdf_download_url) {
                    if (typeof showPdfPreview === "function") {
                        showPdfPreview(result.pdf_download_url, result.pdf_filename);
                    } else {
                        const modal = document.getElementById("pdfPreviewModal");
                        if (modal) {
                            document.getElementById("modalPreviewTitle").textContent = result.pdf_filename || "Document";
                            const iframe = document.getElementById("pdfPreviewIframe");
                            if (/Android/i.test(navigator.userAgent)) {
                                iframe.style.display = 'none';
                                let msg = document.getElementById('androidFixMsg');
                                if(!msg) {
                                    msg = document.createElement('div');
                                    msg.id = 'androidFixMsg';
                                    msg.style.padding = '40px';
                                    msg.style.textAlign = 'center';
                                    msg.style.color = '#fff';
                                    msg.innerHTML = '<i class=\"fa-solid fa-file-pdf\" style=\"font-size:48px; color:#38bdf8; margin-bottom:16px;\"></i><br><h3>PDF Generated Successfully!</h3><p>Android WebView does not support inline PDF previews.</p><p>Please tap the <b>Download</b> button above to view your document.</p>';
                                    iframe.parentNode.appendChild(msg);
                                }
                            } else {
                                iframe.src = result.pdf_download_url;
                            }
                            document.getElementById("btnModalDownloadPDF").href = result.pdf_download_url;
                            modal.style.display = "flex";
                        }
                    }
                } else {
                    alert('Preview Failed: ' + (result.message || 'Unknown error'));
                }
            } catch (err) {
                btnPrev.disabled = false;
                btnPrev.innerHTML = origHTML;
                alert('Network error during preview.');
            }
        });
    }
'''

if 'btnPreview.addEventListener' not in appjs:
    appjs = appjs.replace("form.addEventListener('submit', async (e) => {", preview_logic + "\n        form.addEventListener('submit', async (e) => {")
    with open('static/js/app.js', 'w', encoding='utf-8') as f:
        f.write(appjs)
    print("Injected btnPreview handler into app.js")
