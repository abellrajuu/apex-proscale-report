with open('static/js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Disable button hiding logic in app.js
js = js.replace("if (btnPrevStep) btnPrevStep.style.visibility = currentStep > 1 ? 'visible' : 'hidden';", "")
js = js.replace("if (btnNextStep) btnNextStep.style.display = (currentStep === totalSteps) ? 'none' : 'inline-flex';", "")
js = js.replace("if (btnSubmitPDF) btnSubmitPDF.style.display = (currentStep === totalSteps) ? 'inline-flex' : 'none';", "")

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Removed button hiding logic from app.js")
