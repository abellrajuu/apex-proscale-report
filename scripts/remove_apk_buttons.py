import glob
import re

html_files = glob.glob('templates/*.html')
for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove mobile Get APK
    content = re.sub(r'<a href="/download/ProductionReportApp\.apk" target="_blank" class="mobile-nav-item" style="color: #10b981;">\s*<i class="fa-solid fa-mobile-screen-button"></i>\s*<span>Get APK</span>\s*</a>', '', content)
    
    # Remove desktop Download Android APK
    content = re.sub(r'<a href="/download/ProductionReportApp\.apk" download class="header-nav-link" style="background: linear-gradient\(135deg, #10b981, #059669\); color: #ffffff; border: none; font-weight: 700; box-shadow: 0 4px 12px rgba\(16, 185, 129, 0\.3\);">\s*<i class="fa-solid fa-android"></i> Download Android APK\s*</a>', '', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print("Removed APK download buttons from all templates")
