with open('static/js/app.js', 'r', encoding='utf-8') as f:
    appjs = f.read()

# We will just replace typeof extractGridData === "function" ? extractGridData() : []
# with a function call to a new function getGridData(payload)

new_logic = '''
            if (typeof extractGridData === "function") {
                payload.grid_data = extractGridData();
            } else {
                payload.grid_data = [];
                for (let i = 0; i < 11; i++) {
                    const rowVals = [];
                    for (let j = 0; j < 6; j++) {
                        const el = document.getElementById('g_' + i + '_' + j);
                        if (el) rowVals.push(el.value || '');
                    }
                    if (rowVals.length > 0) payload.grid_data.push(rowVals);
                }
            }
            if (typeof extractRoutineTests === "function") {
                payload.routine_tests = extractRoutineTests();
            } else {
                payload.routine_tests = [];
                for (let i = 0; i < 5; i++) {
                    const t = document.getElementById('t_spec_' + i);
                    const a = document.getElementById('t_act_' + i);
                    if (t && a) payload.routine_tests.push({ spec: t.value, actual: a.value });
                }
            }
'''

appjs = appjs.replace('payload.grid_data = typeof extractGridData === "function" ? extractGridData() : [];\n            payload.routine_tests = typeof extractRoutineTests === "function" ? extractRoutineTests() : [];', new_logic)

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(appjs)
