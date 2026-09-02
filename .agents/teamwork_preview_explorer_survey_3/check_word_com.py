import sys

try:
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    version = word.Version
    word.Quit()
    pythoncom.CoUninitialize()
    print(f"MS Word COM Automation SUCCESS! Word Version: {version}")
except Exception as e:
    print(f"MS Word COM Automation WARNING/ERROR: {e}")
