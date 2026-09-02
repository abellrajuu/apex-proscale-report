with open('static/css/style.css', 'a', encoding='utf-8') as f:
    f.write('\n\n/* WIZARD ENGINE CSS */\n')
    f.write('.step-panel, .section-box { display: none; }\n')
    f.write('.step-panel.active, .section-box.active { display: block; }\n')
    f.write('.step-indicator { padding: 8px 16px; border-radius: 20px; background: rgba(255,255,255,0.05); color: #94a3b8; font-size: 14px; font-weight: 600; white-space: nowrap; }\n')
    f.write('.step-indicator.active { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }\n')
print('Appended wizard CSS')
