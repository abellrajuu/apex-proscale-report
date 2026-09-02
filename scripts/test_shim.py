import runpy
mod = runpy.run_path('app.pyc', run_name='not_main')
app = mod.get('app')
print('Found app:', app)
