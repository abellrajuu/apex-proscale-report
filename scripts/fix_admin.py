import re

with open('templates/admin_users.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove the Server DB Sync Status card
html = re.sub(r'<div class="stat-card">[^<]*<div class="stat-icon" style="background: linear-gradient\(135deg, #8b5cf6, #6d28d9\);">.*?</div>\s*</div>\s*</div>\s*</div>', '</div>', html, flags=re.DOTALL)

# 2. Add Clear Data button
btn_refresh = '<button type="button" id="btnRefreshAuditLogs" class="btn-secondary" style="font-size: 13px;">\n                        <i class="fa-solid fa-rotate"></i> Refresh\n                    </button>'
btn_clear = '<button type="button" id="btnClearData" class="btn-primary" style="font-size: 13px; background: linear-gradient(135deg, #ef4444, #dc2626); border-color: #ef4444;">\n                        <i class="fa-solid fa-trash"></i> Clear Data\n                    </button>'
html = html.replace(btn_refresh, btn_refresh + '\n                    ' + btn_clear)

# 3. Add Clear Data JS logic
js_logic = '''
            document.getElementById('btnClearData')?.addEventListener('click', async () => {
                if (confirm('Are you sure you want to completely clear all production records? This cannot be undone.')) {
                    try {
                        const res = await fetch('/api/clear_records', { method: 'POST' });
                        const data = await res.json();
                        if (data.status === 'success') {
                            alert('All data cleared successfully.');
                            loadAuditLogs();
                        } else {
                            alert('Error: ' + data.message);
                        }
                    } catch(e) {
                        alert('Failed to clear data.');
                    }
                }
            });
'''
html = html.replace('document.getElementById(\'btnRefreshAuditLogs\')?.addEventListener(\'click\', loadAuditLogs);', 'document.getElementById(\'btnRefreshAuditLogs\')?.addEventListener(\'click\', loadAuditLogs);' + js_logic)

with open('templates/admin_users.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated admin_users.html")
