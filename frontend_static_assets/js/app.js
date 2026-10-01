// Deprecated wrapper removed. The submit handler will be assigned after its definition.



// Auto-highlight key technical specifications & hardware models (Load Cell Model, Indicator Model, Tag No, etc.)
function applyKeySpecHighlights() {
    const keyPatterns = [
        /load\s*cell\s*model/i,
        /sensor.*model/i,
        /digital\s*indicator\s*model/i,
        /indicator\s*model/i,
        /di[_\s]*model/i,
        /lc[_\s]*model/i,
        /conveyor\s*no/i,
        /tag\s*no/i,
        /crane\s*id/i,
        /tracking\s*no/i,
        /scale\s*no/i,
        /capacity/i,
        /job\s*no/i,
        /customer/i,
        /junction\s*box\s*model/i,
        /jbox\s*model/i,
        /firmware\s*sw\s*version/i
    ];
    const keyFieldNames = ['lc_model', 'di_model', 'capacity', 'job_no', 'customer', 'conveyor_no', 'crane_id', 'tracking_no', 'jbox_model', 'sw_version'];

    document.querySelectorAll('.input-group, .form-group').forEach(group => {
        let isMatch = false;
        const label = group.querySelector('label');
        if (label) {
            const txt = label.textContent.trim();
            isMatch = keyPatterns.some(rx => rx.test(txt));
        }
        if (!isMatch) {
            const input = group.querySelector('input, select');
            if (input) {
                const name = (input.name || '').toLowerCase();
                const id = (input.id || '').toLowerCase();
                if (keyFieldNames.includes(name) || keyFieldNames.includes(id)) {
                    isMatch = true;
                }
            }
        }
        if (isMatch) {
            group.setAttribute('data-key-highlight', 'true');
            group.classList.add('highlight-spec');
        }
    });
}
window.applyKeySpecHighlights = applyKeySpecHighlights;

document.addEventListener('DOMContentLoaded', () => {
    applyKeySpecHighlights();
    
    window.closeDownloadBanner = function() {
        const banner = document.getElementById("downloadBanner");
        if (banner) {
            banner.classList.remove("show-banner");
            banner.style.setProperty("display", "none", "important");
        }
    };

    // Ensure download banner is strictly hidden on page load
    const initialBanner = document.getElementById("downloadBanner");
    if (initialBanner) {
        initialBanner.classList.remove("show-banner");
        initialBanner.style.setProperty("display", "none", "important");
    }

    const CURRENT_BUILD_VERSION = document.querySelector('meta[name="app-build-version"]')?.getAttribute('content') || '';

    // STEP-BY-STEP WIZARD STATE
    
    const stepPanels = document.querySelectorAll('.step-panel').length > 0 ? document.querySelectorAll('.step-panel') : document.querySelectorAll('.section-box');
    const totalSteps = stepPanels.length > 0 ? stepPanels.length : 1;

    let currentStep = 1;

    // Elements
    const btnNextStep = document.getElementById('btnNextStep');
    const btnPrevStep = document.getElementById('btnPrevStep');
    const btnSubmitPDF = document.getElementById('btnSubmitPDF');
    const progressFill = document.getElementById('wizardProgressFill');
    const stepIndicators = document.querySelectorAll('.step-indicator');
    
    const btnTopAutoFill = document.getElementById('btnTopAutoFill');
    const numReadingsSelect = document.getElementById('num_readings_select');

    // OFFLINE STORAGE & WI-FI SERVER CONFIG MANAGEMENT
    const OFFLINE_STORAGE_KEY = 'belt_scale_offline_records_v1';
    let isServerOnline = false;

    async function downloadWithSaveAsPrompt(fileUrl, suggestedFilename) {
        if (!fileUrl) return;
        const fname = suggestedFilename || "Report.pdf";

        // Standard direct automatic download
        const a = document.createElement("a");
        a.href = fileUrl;
        a.download = fname;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
    window.downloadWithSaveAsPrompt = downloadWithSaveAsPrompt;

    function getServerBaseUrl() {

        if (window.location.protocol.startsWith('http')) {
            return window.location.origin;
        }
        const savedServerIp = localStorage.getItem('apex_wifi_server_ip') || '127.0.0.1:5050';
        return savedServerIp.startsWith('http') ? savedServerIp : `http://${savedServerIp}`;
    }

    function getOfflineRecords() {
        try {
            return JSON.parse(localStorage.getItem(OFFLINE_STORAGE_KEY) || '[]');
        } catch(e) { return []; }
    }

    function saveOfflineRecord(payload) {
        const records = getOfflineRecords();
        payload._offline_id = 'OFFLINE_' + Date.now();
        payload._created_at = new Date().toLocaleString();
        records.push(payload);
        localStorage.setItem(OFFLINE_STORAGE_KEY, JSON.stringify(records));
        updateOfflineBadge();
        showToast('Saved Locally on Device (Offline Mode)', 'warning');
    }

    function removeOfflineRecord(offlineId) {
        let records = getOfflineRecords();
        records = records.filter(r => r._offline_id !== offlineId);
        localStorage.setItem(OFFLINE_STORAGE_KEY, JSON.stringify(records));
        updateOfflineBadge();
    }

    function updateOfflineBadge() {
        const count = getOfflineRecords().length;
        const badge = document.getElementById('offlineQueueBadge');
        if (badge) {
            if (count > 0) {
                badge.style.display = 'inline-flex';
                badge.style.cursor = 'pointer';
                badge.innerHTML = `<i class="fa-solid fa-cloud-arrow-up"></i> ${count} Pending Sync (Tap to Sync Now)`;
                badge.onclick = () => {
                    showToast('Syncing offline records to server...', 'warning');
                    syncOfflineRecords();
                };
            } else {
                badge.style.display = 'none';
            }
        }
    }

    // AUTOMATIC SYNC WHEN BACK IN SERVER RANGE
    async function syncOfflineRecords() {
        const records = getOfflineRecords();
        if (records.length === 0) {
            updateOfflineBadge();
            return;
        }

        let syncedCount = 0;
        for (const record of records) {
            try {
                const res = await fetch(`${getServerBaseUrl()}/api/submit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(record)
                });
                const data = await res.json();
                if (data.status === 'success') {
                    removeOfflineRecord(record._offline_id);
                    syncedCount++;
                }
            } catch(e) {
                break; // Server went offline again
            }
        }

        if (syncedCount > 0) {
            showToast(`Auto-Synced ${syncedCount} Offline Records to Server Database`, 'success');
            loadHistory();
        }
        updateOfflineBadge();
    }

    // SERVER ONLINE HEARTBEAT MONITOR
    async function checkConnectivity() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2500);
            const res = await fetch(`${getServerBaseUrl()}/api/version`, { signal: controller.signal });
            clearTimeout(timeoutId);
            if (res.ok) {
                const wasOffline = !isServerOnline;
                isServerOnline = true;
                if (wasOffline) {
                    showToast('Connected to Server Network', 'success');
                }
                if (getOfflineRecords().length > 0) {
                    syncOfflineRecords();
                }
            } else {
                isServerOnline = false;
            }
        } catch(e) {
            isServerOnline = false;
        }
        updateNetworkStatusIndicator();
        updateOfflineBadge();
    }

    function updateNetworkStatusIndicator() {
        const indicator = document.getElementById('networkStatusIndicator');
        if (indicator) {
            if (isServerOnline) {
                indicator.className = 'user-badge';
                indicator.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                indicator.style.color = '#34d399';
                indicator.innerHTML = '<span class="pulse-dot"></span> Server Connected';
            } else {
                indicator.className = 'user-badge';
                indicator.style.borderColor = 'rgba(245, 158, 11, 0.5)';
                indicator.style.color = '#fbbf24';
                indicator.style.background = 'rgba(245, 158, 11, 0.15)';
                indicator.innerHTML = '<i class="fa-solid fa-wifi-slash"></i> Offline Mode (Device Storage)';
            }
        }
    }

    setInterval(checkConnectivity, 5000);
    checkConnectivity();

    window.goToStep = function(stepNum) {
        const hasStepBoxes = document.getElementById('step-box-1') || document.getElementById('step-box-2');
        if (hasStepBoxes) {
            for (let i = 1; i <= 10; i++) {
                const box = document.getElementById('step-box-' + i) || document.getElementById('step-' + i);
                const st = document.getElementById('st-' + i) || document.querySelector(`.step-indicator[data-step="${i}"]`);
                if (box) {
                    if (i === stepNum) {
                        box.classList.add('active-step');
                        box.classList.add('active');
                        box.style.display = 'block';
                    } else {
                        box.classList.remove('active-step');
                        box.classList.remove('active');
                        box.style.display = 'none';
                    }
                }
                if (st) {
                    if (i === stepNum) {
                        st.classList.add('active');
                        st.classList.remove('completed');
                    } else if (i < stepNum) {
                        st.classList.remove('active');
                        st.classList.add('completed');
                    } else {
                        st.classList.remove('active');
                        st.classList.remove('completed');
                    }
                }
            }
        } else {
            const panels = document.querySelectorAll('.step-panel');
            panels.forEach((p, idx) => {
                if (idx + 1 === stepNum) {
                    p.classList.add('active');
                    p.style.display = 'block';
                } else {
                    p.classList.remove('active');
                    p.style.display = 'none';
                }
            });
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };



    

    // INITIALIZE WIZARD ON PAGE LOAD
    if (stepPanels.length > 0) {
        goToStep(1);
    }

    if (btnNextStep) {
        btnNextStep.addEventListener('click', () => {
            goToStep(currentStep + 1);
        });
    }

    if (btnPrevStep) {
        btnPrevStep.addEventListener('click', () => {
            goToStep(currentStep - 1);
        });
    }

    stepIndicators.forEach(ind => {
        ind.addEventListener('click', () => {
            const targetStep = parseInt(ind.getAttribute('data-step'));
            goToStep(targetStep);
        });
    });

    // Routine Tests Definition
    const defaultRoutineTests = [
        { num: '1.', name: 'Input Supply Voltage (+/-10%)', spec: '230 V AC', act: '229.4 V AC' },
        { num: '2.', name: 'Derived DC Voltages (+/-5%)', spec: '+24 V DC', act: '+24.1 V DC' },
        { num: '3.', name: 'Display and Keypad Functionality', spec: 'OK', act: 'OK Verified' },
        { num: '4.', name: 'Belt Load as specified in G.A. or MPL', spec: '150.0 Kg/m', act: '149.6 Kg/m' },
        { num: '5.', name: 'Belt Speed as specified in G.A. or MPL', spec: '2.0 m/s', act: '2.0 m/s' },
        { num: '6.', name: 'Number of PF Contacts', spec: '4 Contacts', act: '4 Contacts Passed' },
        { num: '7.', name: 'Communication Output (Specify)', spec: 'RS485 Modbus', act: 'Connected 9600-8-N-1' },
        { num: '8.', name: 'Analog Output (Specify number)', spec: '4-20 mA', act: '4.02 mA to 19.98 mA' },
        { num: '9.', name: 'Wiring, TB and Component Layout', spec: 'OK Drawing', act: 'OK Checked' }
    ];

    // Initialize Routine Tests Table
    const routineTableBody = document.getElementById('routineTestsBody');
    if (routineTableBody) {
        routineTableBody.innerHTML = defaultRoutineTests.map((t, idx) => `
            <tr>
                <td><strong>${t.num}</strong></td>
                <td>${t.name}</td>
                <td><input type="text" id="t_spec_${idx}" value="${t.spec}" placeholder="Specified"></td>
                <td><input type="text" id="t_act_${idx}" value="${t.act}" placeholder="Actual"></td>
            </tr>
        `).join('');
    }

    // Initialize 11-Row Measurement Grid Table
    const gridTableBody = document.getElementById('gridMatrixBody');
    if (gridTableBody) {
        let rowsHtml = '';
        for (let i = 0; i < 11; i++) {
            rowsHtml += `
                <tr id="grid_row_${i}">
                    <td><input type="text" id="g_${i}_0" placeholder="Load kg"></td>
                    <td><input type="text" id="g_${i}_1" placeholder="Belt Kg/m"></td>
                    <td><input type="text" id="g_${i}_2" placeholder="Speed m/s"></td>
                    <td><input type="text" id="g_${i}_3" placeholder="Rate tph"></td>
                    <td><input type="text" id="g_${i}_4" placeholder="Totalizer Tonnes"></td>
                    <td><input type="text" id="g_${i}_5" placeholder="O/p mA"></td>
                </tr>
            `;
        }
        gridTableBody.innerHTML = rowsHtml;
    }

    // Dynamic Readings Row Visibility Handler
    function updateReadingsVisibility() {
        const count = parseInt(numReadingsSelect ? numReadingsSelect.value : 5);
        for (let i = 0; i < 11; i++) {
            const rowElem = document.getElementById(`grid_row_${i}`);
            if (!rowElem) continue;

            const inputs = rowElem.querySelectorAll('input');
            if (i < count) {
                rowElem.style.opacity = '1';
                rowElem.style.pointerEvents = 'auto';
                inputs.forEach(inp => inp.disabled = false);
            } else {
                rowElem.style.opacity = '0.25';
                rowElem.style.pointerEvents = 'none';
                inputs.forEach(inp => {
                    inp.disabled = true;
                    inp.value = '';
                });
            }
        }
    }

    if (numReadingsSelect) {
        numReadingsSelect.addEventListener('change', updateReadingsVisibility);
    }
    updateReadingsVisibility();

    // Set Default Date to Today
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    // Auto calculate RPM when Speed (S) and Wheel Dia (D) change
    const speedInput = document.getElementById('tacho_belt_speed');
    const diaInput = document.getElementById('tacho_wheel_dia');
    const rpmInput = document.getElementById('tacho_rpm');

    function calcRpm() {
        if (!speedInput || !diaInput || !rpmInput) return;
        const S = parseFloat(speedInput.value);
        const D = parseFloat(diaInput.value);
        if (!isNaN(S) && !isNaN(D) && D > 0) {
            const rpm = (S / (3.14159 * D)) * 60;
            rpmInput.value = rpm.toFixed(1) + ' RPM';
        }
    }
    if (speedInput) speedInput.addEventListener('input', calcRpm);
    if (diaInput) diaInput.addEventListener('input', calcRpm);

    // DEMO AUTO-FILL DATA FUNCTION
    function fillDemoData() {
        const setVal = (idOrName, val) => {
            if (val === undefined || val === null) return;
            const el = document.getElementById(idOrName) || document.querySelector(`[name="${idOrName}"]`);
            if (el) {
                el.value = val;
                try { el.dispatchEvent(new Event('change')); } catch(e){}
            }
        };

        const names = ['Alex River', 'Sam Taylor', 'Jordan Lee', 'Chris Morgan', 'Morgan Vance', 'David Chen'];
        const customers = ['Titan Cement Ltd', 'UltraTech Minerals', 'JSW Steel Plant', 'Tata Steel Mining', 'Adani Power Thermal'];
        const randCust = customers[Math.floor(Math.random() * customers.length)];
        const randJobNum = Math.floor(100 + Math.random() * 900);
        const randCap = [1000, 1200, 1500, 2000][Math.floor(Math.random() * 4)];
        const randSpeed = (1.5 + Math.random() * 1.5).toFixed(2);
        const dia = 0.318;
        const rpm = ((parseFloat(randSpeed) / (3.14159 * dia)) * 60).toFixed(1);

        // Step 1
        setVal('job_no', `JOB-2026-${randJobNum}`);
        setVal('customer', randCust);
        setVal('conveyor_no', `CV-${Math.floor(10 + Math.random() * 90)}B`);
        setVal('capacity', randCap.toString());
        setVal('belt_speed', randSpeed + " m/s");
        setVal('tacho_belt_speed', randSpeed);
        setVal('date', new Date().toISOString().split('T')[0]);

        // Step 2
        setVal('bs_model', `BS-MODEL-${randJobNum}`);
        setVal('bs_serial', `SN-BS-${7000 + randJobNum}`);
        setVal('remote_model', `RM-UNIT-01`);
        setVal('remote_serial', `SN-RM-${5000 + randJobNum}`);

        setVal('sensor_model', `LC-${randCap / 4}KG`);
        setVal('s1', `LC1-00${randJobNum % 10}`);
        setVal('s2', `LC2-00${randJobNum % 10}`);
        setVal('s3', `LC3-00${randJobNum % 10}`);
        setVal('s4', `LC4-00${randJobNum % 10}`);

        setVal('tacho_model', `TACHO-SENS-PRO`);
        setVal('tacho_serial', `TS-${8000 + randJobNum}`);
        setVal('pulley_diameter', '0.16');
        setVal('tacho_wheel_dia', dia.toString());
        setVal('tacho_rpm', `${rpm} RPM`);

        setVal('angle_sensor_model', `AS-300-TILT`);
        setVal('angle_sensor_serial', `SN-AS-${9000 + randJobNum}`);

        setVal('jbox_model1', `JBOX-IP67`);
        setVal('jbox_serial1', `JB-SN-${100 + randJobNum}`);
        setVal('jbox_model2', `JBOX-IP67`);
        setVal('jbox_serial2', `JB-SN-${200 + randJobNum}`);
        setVal('jbox_model3', `JBOX-IP67`);
        setVal('jbox_serial3', `JB-SN-${300 + randJobNum}`);

        // Step 3 Resolution Rules & Routine Tests
        const calcResRule = (v) => {
            const num = Math.abs(parseFloat(v) || 0);
            if (num <= 99) return { str: '0.01', dec: 2 };
            if (num <= 999) return { str: '0.1', dec: 1 };
            return { str: '1', dec: 0 };
        };
        const demoFullLoad = (randCap * 1000.0) / (3600.0 * parseFloat(randSpeed || 1.0));
        const resL = calcResRule(demoFullLoad);
        const resR = calcResRule(randCap);
        const resS = { str: '0.01', dec: 2 };
        const resT = { str: '0.1', dec: 1 };

        setVal('short_check', `OK (Checked Line/Neutral, Neutral/Earth, Line/Earth)`);
        setVal('res_l', resL.str);
        setVal('res_s', resS.str);
        setVal('res_r', resR.str);
        setVal('res_t', resT.str);

        const routineDefaults = [
            { spec: '230V', act: '230V' },
            { spec: '24V', act: '24V' },
            { spec: 'OK', act: 'OK' },
            { spec: demoFullLoad.toFixed(resL.dec) + " kg/m", act: demoFullLoad.toFixed(resL.dec) + " kg/m" },
            { spec: parseFloat(randSpeed).toFixed(resS.dec) + " m/s", act: parseFloat(randSpeed).toFixed(resS.dec) + " m/s" },
            { spec: '4', act: '4' },
            { spec: 'RS-485', act: 'RS-485' },
            { spec: '4-20mA', act: '4-20mA' },
            { spec: 'OK', act: 'OK' }
        ];

        for (let i = 1; i <= 9; i++) {
            setVal(`spec_${i}`, routineDefaults[i-1].spec);
            setVal(`act_${i}`, routineDefaults[i-1].act);
        }

        // Step 4 Calibration Matrix Grid (Rows 1 to 6)
        for (let r = 1; r <= 6; r++) {
            const stepRatio = (r - 1) / 5.0; // 0%, 20%, 40%, 60%, 80%, 100%
            const loadKg = (3.0 + stepRatio * 2.0).toFixed(2);
            const beltKgM = (stepRatio * demoFullLoad).toFixed(resL.dec);
            const rateTph = (stepRatio * randCap).toFixed(resR.dec);
            const totT = (stepRatio * (randCap / 10.0)).toFixed(resT.dec);
            const mA = (4.0 + stepRatio * 16.0).toFixed(2);

            setVal(`g${r}_0`, loadKg);
            setVal(`g${r}_1`, beltKgM);
            setVal(`g${r}_2`, parseFloat(randSpeed).toFixed(resS.dec));
            setVal(`g${r}_3`, rateTph);
            setVal(`g${r}_4`, totT);
            setVal(`g${r}_5`, mA);
            setVal(`g${r}_5_ao1`, mA);
            setVal(`g${r}_5_ao2`, mA);
        }

        setVal('instrument_used', `Fluke 87V Digital Multimeter & 50kg Calibrated Class F Weights`);
        setVal('tested_by', 'Alex River');
        setVal('approved_by', 'HOD-PDN');

        showToast(`⚡ Demo Test Data Filled Successfully!`, 'success');
    }

    window.fillDemoData = fillDemoData;

    
// Auto-highlight key technical specifications & hardware models (Load Cell Model, Indicator Model, Tag No, etc.)
function applyKeySpecHighlights() {
    const keyPatterns = [
        /load\s*cell\s*model/i,
        /sensor.*model/i,
        /digital\s*indicator\s*model/i,
        /indicator\s*model/i,
        /di[_\s]*model/i,
        /lc[_\s]*model/i,
        /conveyor\s*no/i,
        /tag\s*no/i,
        /crane\s*id/i,
        /tracking\s*no/i,
        /scale\s*no/i,
        /capacity/i,
        /job\s*no/i,
        /customer/i,
        /junction\s*box\s*model/i,
        /jbox\s*model/i,
        /firmware\s*sw\s*version/i
    ];
    const keyFieldNames = ['lc_model', 'di_model', 'capacity', 'job_no', 'customer', 'conveyor_no', 'crane_id', 'tracking_no', 'jbox_model', 'sw_version'];

    document.querySelectorAll('.input-group, .form-group').forEach(group => {
        let isMatch = false;
        const label = group.querySelector('label');
        if (label) {
            const txt = label.textContent.trim();
            isMatch = keyPatterns.some(rx => rx.test(txt));
        }
        if (!isMatch) {
            const input = group.querySelector('input, select');
            if (input) {
                const name = (input.name || '').toLowerCase();
                const id = (input.id || '').toLowerCase();
                if (keyFieldNames.includes(name) || keyFieldNames.includes(id)) {
                    isMatch = true;
                }
            }
        }
        if (isMatch) {
            group.setAttribute('data-key-highlight', 'true');
            group.classList.add('highlight-spec');
        }
    });
}
window.applyKeySpecHighlights = applyKeySpecHighlights;

document.addEventListener('DOMContentLoaded', () => {
    applyKeySpecHighlights();
        document.querySelectorAll('.btnFillDemoDataGlobal, #btnAutoFillHeader, #btnFillSampleData').forEach(btn => {
            btn.addEventListener('click', fillDemoData);
        });
    });

    document.addEventListener('click', (e) => {
        const btn = e.target.closest('#btnAutoFillHeader, #btnFillSampleData, .btnFillDemoDataGlobal');
        if (btn) {
            e.preventDefault();
            fillDemoData();
        }
    });

    // Tab Navigation Logic
    // ARCHIVE TOGGLE
    const btnToggleArchive = document.getElementById('btnToggleArchive');
    const btnCloseHistoryView = document.getElementById('btnCloseHistoryView');
    const generatorTab = document.getElementById('generatorTab');
    const historyTab = document.getElementById('historyTab');

    // INDUSTRIAL HUB NAVIGATION
    const hubView = document.getElementById('hubView');
    const btnLaunchBeltScale = document.getElementById('btnLaunchBeltScale');
    const cardModuleBeltScale = document.getElementById('cardModuleBeltScale');
    const btnBackToHub = document.getElementById('btnBackToHub');

    function openBeltScaleModule() {
        if (hubView) hubView.classList.remove('active');
        if (generatorTab) generatorTab.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function backToHub() {
        if (generatorTab) generatorTab.classList.remove('active');
        if (hubView) hubView.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    if (btnLaunchBeltScale) btnLaunchBeltScale.addEventListener('click', openBeltScaleModule);
    if (cardModuleBeltScale) cardModuleBeltScale.addEventListener('click', (e) => {
        if (e.target.id !== 'btnLaunchBeltScale') openBeltScaleModule();
    });
    if (btnBackToHub) btnBackToHub.addEventListener('click', backToHub);

    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-tab');
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetElem = document.getElementById(target);
            if (targetElem) targetElem.classList.add('active');

            if (target === 'historyTab') {
                loadHistory();
            }
        });
    });

    // FORM SUBMISSION: ONLINE SERVER SUBMIT OR OFFLINE LOCALSTORAGE SAVE!
    const form = document.getElementById('recordForm');
    if (form) {
        
    const btnPreview = document.getElementById('btnPreviewForm');
    if (btnPreview) {
        btnPreview.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopImmediatePropagation();
            const btnPrev = document.getElementById('btnPreviewForm');
            const origHTML = btnPrev.innerHTML;
            btnPrev.disabled = true;
            btnPrev.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Preparing...';
            
            // Build full payload just like submit
            const formData = new FormData(form);
            const payload = Object.fromEntries(formData.entries());
            
            if (typeof extractGridData === "function") {
                payload.grid_data = extractGridData();
            } else {
                payload.grid_data = [];
                for (let i = 1; i <= 11; i++) {
                    const rowVals = [];
                    for (let j = 0; j < 6; j++) {
                        const el = document.getElementById(`g${i}_${j}`) || 
                                   document.getElementById(`g_${i-1}_${j}`) || 
                                   document.getElementById(`g${i}_5_ao1`) || 
                                   document.querySelector(`[name="g${i}_${j}"]`);
                        if (el) rowVals.push(el.value || '');
                    }
                    if (rowVals.length > 0) payload.grid_data.push(rowVals);
                }
            }
            if (typeof extractRoutineTests === "function") {
                payload.routine_tests = extractRoutineTests();
            } else {
                payload.routine_tests = [];
                for (let i = 1; i <= 9; i++) {
                    const t = document.getElementById(`spec_${i}`) || 
                              document.querySelector(`[name="spec_${i}"]`) || 
                              document.getElementById(`t_spec_${i-1}`);
                    const a = document.getElementById(`act_${i}`) || 
                              document.querySelector(`[name="act_${i}"]`) || 
                              document.getElementById(`t_act_${i-1}`);
                    if (t || a) payload.routine_tests.push({ spec: t ? t.value : '', actual: a ? a.value : '' });
                }
            }

            payload.timestamp = new Date().toISOString();
            
            try {
                const res = await fetch(`${getServerBaseUrl()}/api/submit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                btnPrev.disabled = false;
                btnPrev.innerHTML = origHTML;
                
                const dlUrl = result.pdf_download_url || result.docx_download_url;
                const dlFilename = result.pdf_filename || result.docx_filename || "Document.docx";

                if (result.status === 'success' && dlUrl) {
                    if (typeof showPdfPreview === "function") {
                        showPdfPreview(dlUrl, dlFilename);
                    } else {
                        const modal = document.getElementById("pdfPreviewModal");
                        if (modal) {
                            document.getElementById("modalPreviewTitle").textContent = dlFilename;
                            const iframe = document.getElementById("pdfPreviewIframe");
                            if (/Android/i.test(navigator.userAgent) || dlFilename.endsWith('.docx')) {
                                iframe.style.display = 'none';
                                let msg = document.getElementById('androidFixMsg');
                                if(!msg) {
                                    msg = document.createElement('div');
                                    msg.id = 'androidFixMsg';
                                    msg.style.padding = '40px';
                                    msg.style.textAlign = 'center';
                                    msg.style.color = '#fff';
                                    msg.innerHTML = `<i class="fa-solid fa-file-word" style="font-size:48px; color:#38bdf8; margin-bottom:16px;"></i><br><h3>Document Generated Successfully!</h3><p>Please tap the <b>Download</b> button above to save your file (${dlFilename}).</p>`;
                                    iframe.parentNode.appendChild(msg);
                                }
                            } else {
                                iframe.src = dlUrl;
                            }
                            document.getElementById("btnModalDownloadPDF").href = dlUrl;
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

        const submitFormHandler = async (e) => {
            if (e) e.preventDefault();
            if (form && form.dataset.submitting === "true") return;
            if (form) form.dataset.submitting = "true";

            if (btnSubmitPDF) {
                btnSubmitPDF.disabled = true;
                btnSubmitPDF.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Document...';
            }

            try {
                const formData = form ? new FormData(form) : new FormData();
                const payload = {};
                formData.forEach((value, key) => { payload[key] = value; });

                // Gather Routine Tests (spec_1..9, act_1..9)
                payload.routine_tests = [];
                for (let i = 1; i <= 9; i++) {
                    const specElem = document.getElementById(`spec_${i}`) || document.querySelector(`[name="spec_${i}"]`);
                    const actElem = document.getElementById(`act_${i}`) || document.querySelector(`[name="act_${i}"]`);
                    const specVal = specElem ? specElem.value : (payload[`spec_${i}`] || '');
                    const actVal = actElem ? actElem.value : (payload[`act_${i}`] || '');
                    payload[`spec_${i}`] = specVal;
                    payload[`act_${i}`] = actVal;
                    payload.routine_tests.push({ spec: specVal, act: actVal });
                }

                // Gather Measurement Grid (g1_0..g11_5)
                const numReadingsSelect = document.getElementById('num_readings_select');
                const activeCount = parseInt(numReadingsSelect ? numReadingsSelect.value : 11);
                payload.grid_data = [];
                for (let r = 1; r <= 11; r++) {
                    const rowVals = [];
                    for (let c = 0; c < 6; c++) {
                        let elem = document.getElementById(`g${r}_${c}`);
                        if (!elem && c === 5) {
                            elem = document.getElementById(`g${r}_5_ao1`) || document.querySelector(`[name="g${r}_5_ao1"]`);
                        }
                        if (!elem) {
                            elem = document.querySelector(`[name="g${r}_${c}"]`);
                        }
                        const cellVal = elem ? elem.value : (payload[`g${r}_${c}`] || '');
                        rowVals.push(cellVal);
                    }
                    payload.grid_data.push(rowVals);
                }

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000);

                const response = await fetch(`${getServerBaseUrl()}/api/submit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                const result = await response.json();

                if (result.status === 'success') {
                    isServerOnline = true;
                    updateNetworkStatusIndicator();
                    showToast('Report Generated Successfully!', 'success');

                    const docxUrl = result.docx_download_url || (result.docx_filename ? `${getServerBaseUrl()}/download/${result.docx_filename}` : null);
                    const docxFilename = result.docx_filename || "Report.docx";
                    
                    const pdfUrl = result.pdf_download_url || (result.pdf_filename ? `${getServerBaseUrl()}/download/${result.pdf_filename}` : null);
                    const pdfFilename = result.pdf_filename || "Report.pdf";

                    const mainDlUrl = pdfUrl || docxUrl;
                    const mainFilename = pdfFilename || docxFilename;

                    if (mainDlUrl) {
                        // 1. Update Download Banner
                        const banner = document.getElementById("downloadBanner");
                        const bannerFile = document.getElementById("downloadFilename");
                        const btnDlPDF = document.getElementById("btnDownloadPDF");
                        const btnDlDOCX = document.getElementById("btnDownloadDOCX");
                        const btnBannerPreview = document.getElementById("btnBannerPreviewPDF");

                        if (banner) {
                            banner.classList.add("show-banner");
                            banner.style.setProperty("display", "flex", "important");
                            if (bannerFile) bannerFile.textContent = mainFilename;

                            // Ensure dismiss/close button exists and works
                            let closeBtn = banner.querySelector(".btn-banner-close");
                            if (!closeBtn) {
                                closeBtn = document.createElement("button");
                                closeBtn.type = "button";
                                closeBtn.className = "btn-banner-close";
                                closeBtn.innerHTML = '<i class="fa-solid fa-xmark"></i>';
                                closeBtn.title = "Dismiss";
                                closeBtn.onclick = () => window.closeDownloadBanner();
                                banner.appendChild(closeBtn);
                            } else {
                                closeBtn.onclick = () => window.closeDownloadBanner();
                            }

                            if (btnDlPDF && pdfUrl) {
                                btnDlPDF.href = pdfUrl;
                                btnDlPDF.setAttribute("download", pdfFilename);
                            }
                            if (btnDlDOCX && docxUrl) {
                                btnDlDOCX.href = docxUrl;
                                btnDlDOCX.setAttribute("download", docxFilename);
                            }
                            if (btnBannerPreview) {
                                btnBannerPreview.onclick = (e) => {
                                    e.preventDefault();
                                    const modal = document.getElementById("pdfPreviewModal");
                                    if (modal && pdfUrl) {
                                        const titleEl = document.getElementById("modalPreviewTitle");
                                        if (titleEl) titleEl.textContent = pdfFilename;
                                        const iframe = document.getElementById("pdfPreviewIframe");
                                        if (iframe) iframe.src = pdfUrl;
                                        const dlBtn = document.getElementById("btnModalDownloadPDF");
                                        if (dlBtn) dlBtn.href = pdfUrl;
                                        modal.style.display = "flex";
                                    }
                                };
                            }
                            try {
                                banner.scrollIntoView({ behavior: "smooth", block: "center" });
                            } catch (e) {}
                        }

                        // 2. Trigger automatic direct download for Word (.docx) & PDF (.pdf)
                        try {
                            if (docxUrl) downloadWithSaveAsPrompt(docxUrl, docxFilename);
                        } catch (e) { console.error("DOCX Auto-download error:", e); }

                        try {
                            if (pdfUrl) {
                                setTimeout(() => {
                                    try { downloadWithSaveAsPrompt(pdfUrl, pdfFilename); } catch (e) {}
                                }, 300);
                            }
                        } catch (e) { console.error("PDF Auto-download error:", e); }
                    }

                    await loadHistory();
                    return;

                } else {
                    showToast('Submit Error: ' + (result.message || 'Unknown server error'), 'error');
                }
            } catch (err) {
                console.error('Submit error:', err);
                showToast('Submit Error: ' + (err.message || err), 'error');
            } finally {
                if (form) form.dataset.submitting = "false";
                if (btnSubmitPDF) {
                    btnSubmitPDF.disabled = false;
                    btnSubmitPDF.innerHTML = '<i class="fa-solid fa-file-export"></i> Submit Report';
                }
            }
        };

        if (form) {
            form.addEventListener('submit', submitFormHandler);
        }
        if (btnSubmitPDF) {
            btnSubmitPDF.addEventListener('click', (e) => {
                e.preventDefault();
                submitFormHandler(e);
            });
        }
        window.executeBeltScaleSubmit = submitFormHandler;
        window.submitBeltScaleForm = submitFormHandler;
    }

    // Load History Function (Server Records + Local Offline Queue)
    async function loadHistory() {
        const historyBody = document.getElementById('historyTableBody');
        if (!historyBody) return;

        let serverRecords = [];
        try {
            const res = await fetch(`${getServerBaseUrl()}/api/records`);
            const data = await res.json();
            if (data.status === 'success' && data.records) {
                serverRecords = data.records;
            }
        } catch (e) {}

        const offlineRecords = getOfflineRecords();
        updateOfflineBadge();

        if (serverRecords.length === 0 && offlineRecords.length === 0) {
            historyBody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 24px; color:var(--text-muted);">No PDF documents created yet. Fill data and click Save & Generate PDF!</td></tr>';
            return;
        }

        let html = '';

        // Render Pending Offline Records first
        if (offlineRecords.length > 0) {
            html += offlineRecords.map(r => `
                <tr style="background: rgba(245, 158, 11, 0.12); border-left: 4px solid #f59e0b;">
                    <td><code style="background:rgba(245, 158, 11, 0.25); color:#fbbf24; padding:4px 8px; border-radius:6px; font-weight:800;">${r.job_no}</code></td>
                    <td><strong>${r.customer || '-'}</strong></td>
                    <td>${r.conveyor_no || '-'}</td>
                    <td><i class="fa-solid fa-user-circle" style="color:#fbbf24;"></i> ${r.user_name}</td>
                    <td><span style="color:#fbbf24; font-weight:700;">⚡ Offline (${r._created_at})</span></td>
                    <td style="text-align: center;">
                        <span style="background:rgba(245, 158, 11, 0.2); color:#fbbf24; border:1px solid rgba(245, 158, 11, 0.5); padding:4px 12px; border-radius:14px; font-size:12px; font-weight:700;">
                            Pending Server Sync
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        // Render Server Records
        if (serverRecords.length > 0) {
            html += serverRecords.map(r => `
                <tr>
                    <td><code style="background:rgba(56, 189, 248, 0.15); color:#38bdf8; padding:4px 8px; border-radius:6px; font-weight:800;">${r.job_no}</code></td>
                    <td><strong>${r.customer || '-'}</strong></td>
                    <td>${r.conveyor_no || '-'}</td>
                    <td><i class="fa-solid fa-user-circle" style="color:#38bdf8;"></i> ${r.user_name}</td>
                    <td>${r.created_at}</td>
                    <td style="text-align: center; display: flex; gap: 8px; justify-content: center;">
                        <a href="${getServerBaseUrl()}/download/${r.pdf_filename || r.docx_filename.replace('.docx', '.pdf')}" target="_blank" class="btn-secondary" style="font-size:12px; padding:6px 12px; border-color:rgba(56, 189, 248, 0.4); color:#38bdf8;">
                            <i class="fa-solid fa-eye"></i> View PDF
                        </a>
                        <a href="${getServerBaseUrl()}/download/${r.pdf_filename || r.docx_filename.replace('.docx', '.pdf')}?download=1" class="btn-download" download>
                            <i class="fa-solid fa-download"></i> Download
                        </a>
                    </td>
                </tr>
            `).join('');
        }

        historyBody.innerHTML = html;
    }

    const btnRefreshHistoryList = document.getElementById('btnRefreshHistoryList');
    if (btnRefreshHistoryList) btnRefreshHistoryList.addEventListener('click', loadHistory);

    loadHistory();

    // Toast Function
    function showToast(msg, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMsg = document.getElementById('toastMsg');
        const toastIcon = document.getElementById('toastIcon');

        if (!toast || !toastMsg) return;

        toastMsg.innerText = msg;
        if (type === 'error') {
            toastIcon.className = 'fa-solid fa-circle-exclamation';
            toast.style.borderColor = '#f43f5e';
        } else if (type === 'warning') {
            toastIcon.className = 'fa-solid fa-triangle-exclamation';
            toast.style.borderColor = '#f59e0b';
        } else {
            toastIcon.className = 'fa-solid fa-circle-check';
            toast.style.borderColor = '#10b981';
        }

        toast.classList.remove('hidden');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 4000);
    }

    // INTERACTIVE REGION SELECTION SNIPPING TOOL & RULES LOGGING ENGINE
    function initScreenshotCapture() {
        if (!window.html2canvas) {
            const script = document.createElement('script');
            script.src = '/static/js/html2canvas.min.js';
            document.head.appendChild(script);
        }

        const floatBtn = document.createElement('button');
        floatBtn.id = 'btnFloatingScreenshot';
        floatBtn.title = 'Select Region Screenshot & Log Rule (Ctrl+Shift+S or Ctrl+Shift+I)';
        floatBtn.innerHTML = '<i class="fa-solid fa-crop-simple"></i>';
        floatBtn.style.cssText = `
            position: fixed;
            bottom: 80px;
            right: 24px;
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0284c7, #0ea5e9);
            color: #ffffff;
            border: 2px solid rgba(255, 255, 255, 0.4);
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 8px 24px rgba(2, 132, 199, 0.4);
            z-index: 9999;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        floatBtn.onmouseover = () => floatBtn.style.transform = 'scale(1.1)';
        floatBtn.onmouseout = () => floatBtn.style.transform = 'scale(1.0)';
        floatBtn.onclick = startRegionSnipping;
        document.body.appendChild(floatBtn);

        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey && e.shiftKey && (e.key === 'S' || e.key === 's')) || 
                (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i'))) {
                e.preventDefault();
                startRegionSnipping();
            }
        });

        async function captureFullScreen() {
            try {
                showToast('Capturing screen...', 'warning');
                floatBtn.style.display = 'none';
                const canvas = await html2canvas(document.body, {
                    useCORS: true,
                    logging: false,
                    scale: window.devicePixelRatio || 1
                });
                floatBtn.style.display = 'flex';
                const imageData = canvas.toDataURL('image/png');
                showScreenshotModal(imageData);
            } catch(err) {
                floatBtn.style.display = 'flex';
                showToast('Failed to capture screen: ' + err.message, 'error');
            }
        }

        function startRegionSnipping() {
            if (!window.html2canvas) {
                showToast('Loading snipping engine...', 'warning');
                setTimeout(startRegionSnipping, 800);
                return;
            }

            let existingOverlay = document.getElementById('snippingOverlay');
            if (existingOverlay) existingOverlay.remove();

            const overlay = document.createElement('div');
            overlay.id = 'snippingOverlay';
            overlay.style.cssText = `
                position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.35);
                cursor: crosshair; z-index: 100000; user-select: none;
                touch-action: none;
            `;

            const banner = document.createElement('div');
            banner.style.cssText = `
                position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
                background: #1e293b; color: #38bdf8; border: 1.5px solid rgba(56, 189, 248, 0.5);
                padding: 12px 28px; border-radius: 30px; font-family: 'Outfit', sans-serif;
                font-size: 14px; font-weight: 700; box-shadow: 0 8px 24px rgba(0,0,0,0.6);
                pointer-events: none; display: flex; align-items: center; gap: 10px;
                max-width: 90vw; text-align: center;
            `;
            banner.innerHTML = '<i class="fa-solid fa-crop-simple"></i> Drag region or tap screen to capture';
            overlay.appendChild(banner);

            const selectionBox = document.createElement('div');
            selectionBox.style.cssText = `
                position: absolute; border: 2px dashed #0ea5e9; background: rgba(14, 165, 233, 0.2);
                box-shadow: 0 0 0 9999px rgba(15, 23, 42, 0.45); display: none; pointer-events: none;
            `;
            overlay.appendChild(selectionBox);

            let startX = 0, startY = 0, isDragging = false;

            const handleStart = (clientX, clientY) => {
                startX = clientX;
                startY = clientY;
                isDragging = true;
                selectionBox.style.left = `${startX}px`;
                selectionBox.style.top = `${startY}px`;
                selectionBox.style.width = '0px';
                selectionBox.style.height = '0px';
                selectionBox.style.display = 'block';
            };

            const handleMove = (clientX, clientY) => {
                if (!isDragging) return;
                const rectLeft = Math.min(startX, clientX);
                const rectTop = Math.min(startY, clientY);
                const rectWidth = Math.abs(clientX - startX);
                const rectHeight = Math.abs(clientY - startY);

                selectionBox.style.left = `${rectLeft}px`;
                selectionBox.style.top = `${rectTop}px`;
                selectionBox.style.width = `${rectWidth}px`;
                selectionBox.style.height = `${rectHeight}px`;
            };

            overlay.onmousedown = (e) => handleStart(e.clientX, e.clientY);
            overlay.onmousemove = (e) => handleMove(e.clientX, e.clientY);
            
            overlay.ontouchstart = (e) => {
                if (e.touches && e.touches.length > 0) {
                    handleStart(e.touches[0].clientX, e.touches[0].clientY);
                }
            };
            overlay.ontouchmove = (e) => {
                if (e.touches && e.touches.length > 0) {
                    handleMove(e.touches[0].clientX, e.touches[0].clientY);
                }
            };

            const cancelSnipping = (e) => {
                if (e.key === 'Escape') {
                    overlay.remove();
                    document.removeEventListener('keydown', cancelSnipping);
                }
            };
            document.addEventListener('keydown', cancelSnipping);

            overlay.onmouseup = (e) => endDrag(e.clientX, e.clientY);
            overlay.ontouchend = (e) => {
                if (e.changedTouches && e.changedTouches.length > 0) {
                    endDrag(e.changedTouches[0].clientX, e.changedTouches[0].clientY);
                } else {
                    endDrag(startX, startY);
                }
            };

            const endDrag = async (clientX, clientY) => {
                if (!isDragging) return;
                isDragging = false;
                document.removeEventListener('keydown', cancelSnipping);

                const currentX = clientX;
                const currentY = clientY;
                const rectLeft = Math.min(startX, currentX);
                const rectTop = Math.min(startY, currentY);
                const rectWidth = Math.abs(currentX - startX);
                const rectHeight = Math.abs(currentY - startY);

                overlay.remove();

                if (rectWidth < 15 || rectHeight < 15) {
                    captureFullScreen();
                    return;
                }

                floatBtn.style.display = 'none';

                try {
                    showToast('Capturing selected region...', 'warning');
                    
                    const fullCanvas = await html2canvas(document.body, {
                        useCORS: true,
                        logging: false,
                        scale: window.devicePixelRatio || 1
                    });
                    
                    floatBtn.style.display = 'flex';

                    const scale = window.devicePixelRatio || 1;
                    const cropCanvas = document.createElement('canvas');
                    cropCanvas.width = rectWidth * scale;
                    cropCanvas.height = rectHeight * scale;
                    const ctx = cropCanvas.getContext('2d');

                    const scrollX = window.scrollX || window.pageXOffset;
                    const scrollY = window.scrollY || window.pageYOffset;

                    ctx.drawImage(
                        fullCanvas,
                        (rectLeft + scrollX) * scale,
                        (rectTop + scrollY) * scale,
                        rectWidth * scale,
                        rectHeight * scale,
                        0,
                        0,
                        rectWidth * scale,
                        rectHeight * scale
                    );

                    const croppedImageData = cropCanvas.toDataURL('image/png');
                    showScreenshotModal(croppedImageData);

                } catch(err) {
                    floatBtn.style.display = 'flex';
                    showToast('Failed to capture region: ' + err.message, 'error');
                }
            };

            document.body.appendChild(overlay);
        }

        function showScreenshotModal(imageData) {
            let modal = document.getElementById('screenshotModal');
            if (modal) modal.remove();

            modal = document.createElement('div');
            modal.id = 'screenshotModal';
            modal.style.cssText = `
                position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(8px);
                z-index: 100000; display: flex; align-items: center; justify-content: center; padding: 20px;
            `;

            modal.innerHTML = `
                <div style="background: #1e293b; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 20px; max-width: 580px; width: 100%; padding: 28px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); color: #ffffff;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                        <h3 style="font-family: 'Outfit', sans-serif; font-size: 20px; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 10px; margin: 0;">
                            <i class="fa-solid fa-crop-simple"></i> Selected Region Screenshot & Rule Note
                        </h3>
                        <button id="closeScreenshotModal" style="background: none; border: none; color: #94a3b8; font-size: 20px; cursor: pointer;">&times;</button>
                    </div>

                    <div style="margin-bottom: 20px; text-align: center; background: #0f172a; padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
                        <img src="${imageData}" style="max-width: 100%; max-height: 240px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);" />
                    </div>

                    <div style="margin-bottom: 20px;">
                        <label style="display: block; font-size: 13px; font-weight: 700; margin-bottom: 8px; color: #cbd5e1;">Rule Note / Feedback Directive:</label>
                        <textarea id="screenshotNoteInput" placeholder="Enter rule note or UI feedback directive for this region..." style="width: 100%; height: 80px; background: #0f172a; border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 12px; color: #ffffff; font-family: inherit; font-size: 14px; resize: vertical; box-sizing: border-box;"></textarea>
                    </div>

                    <div style="display: flex; gap: 12px; justify-content: flex-end;">
                        <button id="cancelScreenshotModal" style="background: #334155; color: #ffffff; border: none; padding: 10px 20px; border-radius: 10px; font-weight: 700; cursor: pointer;">Cancel</button>
                        <button id="saveScreenshotModal" style="background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; border: none; padding: 10px 22px; border-radius: 10px; font-weight: 700; cursor: pointer; box-shadow: 0 4px 14px rgba(16,185,129,0.3);">
                            <i class="fa-solid fa-cloud-arrow-up"></i> Save & Log Rule
                        </button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            document.getElementById('closeScreenshotModal').onclick = () => modal.remove();
            document.getElementById('cancelScreenshotModal').onclick = () => modal.remove();

            document.getElementById('saveScreenshotModal').onclick = async () => {
                const note = document.getElementById('screenshotNoteInput').value;
                const saveBtn = document.getElementById('saveScreenshotModal');
                saveBtn.disabled = true;
                saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

                try {
                    const res = await fetch(`${getServerBaseUrl()}/api/capture_screenshot`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            image_data: imageData,
                            note: note,
                            page_url: window.location.pathname
                        })
                    });
                    const data = await res.json();
                    if (data.status === 'success') {
                        modal.remove();
                        showToast('Region saved to LIVE TESTING/ & SCREENSHOTS/ and logged to RULES.md!', 'success');
                    } else {
                        showToast(data.message || 'Failed to save region screenshot', 'error');
                        saveBtn.disabled = false;
                        saveBtn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Save & Log Rule';
                    }
                } catch(e) {
                    showToast('Error saving screenshot to server', 'error');
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Save & Log Rule';
                }
            };
        }
    }

    initScreenshotCapture();
});

// ====== CUSTOM BUSINESS RULES ENGINE ======

// Auto-highlight key technical specifications & hardware models (Load Cell Model, Indicator Model, Tag No, etc.)
function applyKeySpecHighlights() {
    const keyPatterns = [
        /load\s*cell\s*model/i,
        /sensor.*model/i,
        /digital\s*indicator\s*model/i,
        /indicator\s*model/i,
        /di[_\s]*model/i,
        /lc[_\s]*model/i,
        /conveyor\s*no/i,
        /tag\s*no/i,
        /crane\s*id/i,
        /tracking\s*no/i,
        /scale\s*no/i,
        /capacity/i,
        /job\s*no/i,
        /customer/i,
        /junction\s*box\s*model/i,
        /jbox\s*model/i,
        /firmware\s*sw\s*version/i
    ];
    const keyFieldNames = ['lc_model', 'di_model', 'capacity', 'job_no', 'customer', 'conveyor_no', 'crane_id', 'tracking_no', 'jbox_model', 'sw_version'];

    document.querySelectorAll('.input-group, .form-group').forEach(group => {
        let isMatch = false;
        const label = group.querySelector('label');
        if (label) {
            const txt = label.textContent.trim();
            isMatch = keyPatterns.some(rx => rx.test(txt));
        }
        if (!isMatch) {
            const input = group.querySelector('input, select');
            if (input) {
                const name = (input.name || '').toLowerCase();
                const id = (input.id || '').toLowerCase();
                if (keyFieldNames.includes(name) || keyFieldNames.includes(id)) {
                    isMatch = true;
                }
            }
        }
        if (isMatch) {
            group.setAttribute('data-key-highlight', 'true');
            group.classList.add('highlight-spec');
        }
    });
}
window.applyKeySpecHighlights = applyKeySpecHighlights;

document.addEventListener('DOMContentLoaded', () => {
    applyKeySpecHighlights();
    const path = window.location.pathname.toLowerCase();

    const num = (val) => {
        let parsed = parseFloat(String(val).replace(/[^0-9.]/g, ''));
        return isNaN(parsed) ? 0 : parsed;
    };

    // 1. Weigh Feeder / Screwfeeder / Loss In Weigh Feeder
    if (path.includes('weigh_feeder') || path.includes('screwfeeder')) {
        const applyWeighFeederRules = () => {
            const speedEl = document.getElementById('belt_speed') || document.querySelector('[name="belt_speed"]');
            const rateEl = document.getElementById('capacity') || document.querySelector('[name="capacity"]');
            
            let s = 1.0;
            if (speedEl && speedEl.value) {
                let speedVal = String(speedEl.value).toLowerCase();
                s = num(speedVal);
                if (speedVal.includes('min')) s = s / 60.0;
                
                let sDec = s >= 0.1 ? 3 : 4;
                speedEl.value = s.toFixed(sDec) + " m/s";
                
                const resSpeedEl = document.getElementById('res_speed') || document.querySelector('[name="res_speed"]');
                if (resSpeedEl) resSpeedEl.value = (1 / Math.pow(10, sDec)).toFixed(sDec) + " m/s";
            }
            
            if (rateEl && rateEl.value) {
                let r = num(rateEl.value);
                let rDec = 2;
                if (r >= 100 && r <= 999) rDec = 1;
                if (r > 999) rDec = 0;
                rateEl.value = r.toFixed(rDec) + (String(rateEl.value).toLowerCase().includes('tph') ? ' TPH' : '');
                
                const resRateEl = document.getElementById('res_rate') || document.querySelector('[name="res_rate"]');
                if (resRateEl) resRateEl.value = (1 / Math.pow(10, rDec)).toFixed(rDec) + " tph";
                
                // belt load
                if (s > 0) {
                    let bl = r / (3.6 * s);
                    let blDec = 3;
                    if (bl >= 10) blDec = 2;
                    
                    const resLoadEl = document.getElementById('res_load') || document.querySelector('[name="res_load"]');
                    if (resLoadEl) resLoadEl.value = (1 / Math.pow(10, blDec)).toFixed(blDec) + " kg/m";
                    
                    const beltLoadEl = document.getElementById('belt_load') || document.querySelector('[name="belt_load"]');
                    if (beltLoadEl) beltLoadEl.value = bl.toFixed(blDec) + " kg/m";
                }
                
                // totaliser
                const resTotEl = document.getElementById('res_tot') || document.querySelector('[name="res_tot"]') || document.querySelector('[name="totaliser"]');
                if (resTotEl) resTotEl.value = (r / 10).toFixed(rDec);
            }
        };

        // Removed unwanted periodic setInterval. Rules trigger only on user input/change:
        document.body.addEventListener('change', (e) => {
            if (e.target.name === 'belt_speed' || e.target.name === 'capacity') {
                applyWeighFeederRules();
            }
        });
    }

    // 2. Belt Scale
    if (path.includes('belt_scale')) {
        const applyBeltScaleRules = () => {
            const speedEl = document.getElementById('belt_speed') || document.querySelector('[name="belt_speed"]');
            const rateEl = document.getElementById('capacity') || document.querySelector('[name="capacity"]');
            if (!speedEl || !rateEl || !speedEl.value || !rateEl.value) return;
            
            let speedNum = parseFloat(String(speedEl.value).replace(/[^0-9.]/g, '')) || 0;
            let rateNum = parseFloat(String(rateEl.value).replace(/[^0-9.]/g, '')) || 0;
            if (speedNum <= 0 || rateNum <= 0) return;

            const calcResRule = (v) => {
                const num = Math.abs(parseFloat(v) || 0);
                if (num <= 99) return { str: '0.01', dec: 2 };
                if (num <= 999) return { str: '0.1', dec: 1 };
                return { str: '1', dec: 0 };
            };

            let fullLoad = (rateNum * 1000.0) / (3600.0 * speedNum);
            let resL = calcResRule(fullLoad);
            let resR = calcResRule(rateNum);
            let resS = { str: '0.01', dec: 2 };
            let resT = { str: '0.1', dec: 1 };

            const resLEl = document.getElementById('res_l') || document.querySelector('[name="res_l"]');
            if (resLEl && !resLEl.value) resLEl.value = resL.str;
            const resREl = document.getElementById('res_r') || document.querySelector('[name="res_r"]');
            if (resREl && !resREl.value) resREl.value = resR.str;
            const resSEl = document.getElementById('res_s') || document.querySelector('[name="res_s"]');
            if (resSEl && !resSEl.value) resSEl.value = resS.str;
            const resTEl = document.getElementById('res_t') || document.querySelector('[name="res_t"]');
            if (resTEl && !resTEl.value) resTEl.value = resT.str;

            const beltLoadEl = document.getElementById('belt_load') || document.querySelector('[name="belt_load"]');
            if (beltLoadEl && !beltLoadEl.value) beltLoadEl.value = fullLoad.toFixed(resL.dec) + " kg/m";
        };

        // Removed periodic setInterval. Trigger only on user input/change:
        document.body.addEventListener('change', (e) => {
            if (e.target.name === 'belt_speed' || e.target.name === 'capacity') {
                applyBeltScaleRules();
            }
        });
    }

    // 3. CWS (Crane Scale)
    if (path.includes('crane_scale') || path.includes('cws')) {
        const calcMvSteps = () => {
            const finalMvEl = document.getElementById('final_mv_output') || document.querySelector('[name="final_mv_output"]');
            const lcEl = document.getElementById('capacity') || document.querySelector('[name="capacity"]');
            if (!finalMvEl || !finalMvEl.value) return;
            
            let finalMv = num(finalMvEl.value);
            let lc = num(lcEl ? lcEl.value : "100");
            
            let steps = [0.0, 0.25, 0.50, 0.75, 1.0];
            steps.forEach((pct, idx) => {
                let stepMv = (finalMv * pct).toFixed(3);
                let stepLoad = (lc * pct).toFixed(1);
                
                let mvField = document.getElementById(`step_${idx}_mv`) || document.querySelector(`[name="step_${idx}_mv"]`);
                if (mvField) mvField.value = stepMv + " mV";
                
                let ldField = document.getElementById(`step_${idx}_load`) || document.querySelector(`[name="step_${idx}_load"]`);
                if (ldField) ldField.value = stepLoad + " t";
            });
        };
        
        // Removed periodic setInterval. Trigger only on user input/change:
        document.body.addEventListener('input', (e) => {
            if (e.target.id === 'final_mv_output' || e.target.name === 'final_mv_output' || e.target.name === 'capacity') {
                calcMvSteps();
            }
        });
    }
});

// Global handler to close PDF Preview Modal

// Auto-highlight key technical specifications & hardware models (Load Cell Model, Indicator Model, Tag No, etc.)
function applyKeySpecHighlights() {
    const keyPatterns = [
        /load\s*cell\s*model/i,
        /sensor.*model/i,
        /digital\s*indicator\s*model/i,
        /indicator\s*model/i,
        /di[_\s]*model/i,
        /lc[_\s]*model/i,
        /conveyor\s*no/i,
        /tag\s*no/i,
        /crane\s*id/i,
        /tracking\s*no/i,
        /scale\s*no/i,
        /capacity/i,
        /job\s*no/i,
        /customer/i,
        /junction\s*box\s*model/i,
        /jbox\s*model/i,
        /firmware\s*sw\s*version/i
    ];
    const keyFieldNames = ['lc_model', 'di_model', 'capacity', 'job_no', 'customer', 'conveyor_no', 'crane_id', 'tracking_no', 'jbox_model', 'sw_version'];

    document.querySelectorAll('.input-group, .form-group').forEach(group => {
        let isMatch = false;
        const label = group.querySelector('label');
        if (label) {
            const txt = label.textContent.trim();
            isMatch = keyPatterns.some(rx => rx.test(txt));
        }
        if (!isMatch) {
            const input = group.querySelector('input, select');
            if (input) {
                const name = (input.name || '').toLowerCase();
                const id = (input.id || '').toLowerCase();
                if (keyFieldNames.includes(name) || keyFieldNames.includes(id)) {
                    isMatch = true;
                }
            }
        }
        if (isMatch) {
            group.setAttribute('data-key-highlight', 'true');
            group.classList.add('highlight-spec');
        }
    });
}
window.applyKeySpecHighlights = applyKeySpecHighlights;

document.addEventListener('DOMContentLoaded', () => {
    applyKeySpecHighlights();
    const attachModalCloseListeners = () => {
        const btnClose = document.getElementById('btnClosePreviewModal');
        const modal = document.getElementById('pdfPreviewModal');
        
        const closeModal = () => {
            if (modal) modal.style.display = 'none';
        };

        if (btnClose) {
            btnClose.addEventListener('click', closeModal);
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal || e.target.id === 'pdfPreviewModal') {
                    closeModal();
                }
            });
        }
    };

    // Attach immediately
    attachModalCloseListeners();
    // And also attach on body clicks in case modal is dynamically injected
    document.body.addEventListener('click', (e) => {
        if (e.target.closest('#btnClosePreviewModal')) {
            const m = document.getElementById('pdfPreviewModal');
            if (m) m.style.display = 'none';
        }
        if (e.target.id === 'pdfPreviewModal') {
            e.target.style.display = 'none';
        }
    });
});


// Universal Auto-fill when typing Job No and pressing Enter, or moving to next field (blur / change)

// Auto-highlight key technical specifications & hardware models (Load Cell Model, Indicator Model, Tag No, etc.)
function applyKeySpecHighlights() {
    const keyPatterns = [
        /load\s*cell\s*model/i,
        /sensor.*model/i,
        /digital\s*indicator\s*model/i,
        /indicator\s*model/i,
        /di[_\s]*model/i,
        /lc[_\s]*model/i,
        /conveyor\s*no/i,
        /tag\s*no/i,
        /crane\s*id/i,
        /tracking\s*no/i,
        /scale\s*no/i,
        /capacity/i,
        /job\s*no/i,
        /customer/i,
        /junction\s*box\s*model/i,
        /jbox\s*model/i,
        /firmware\s*sw\s*version/i
    ];
    const keyFieldNames = ['lc_model', 'di_model', 'capacity', 'job_no', 'customer', 'conveyor_no', 'crane_id', 'tracking_no', 'jbox_model', 'sw_version'];

    document.querySelectorAll('.input-group, .form-group').forEach(group => {
        let isMatch = false;
        const label = group.querySelector('label');
        if (label) {
            const txt = label.textContent.trim();
            isMatch = keyPatterns.some(rx => rx.test(txt));
        }
        if (!isMatch) {
            const input = group.querySelector('input, select');
            if (input) {
                const name = (input.name || '').toLowerCase();
                const id = (input.id || '').toLowerCase();
                if (keyFieldNames.includes(name) || keyFieldNames.includes(id)) {
                    isMatch = true;
                }
            }
        }
        if (isMatch) {
            group.setAttribute('data-key-highlight', 'true');
            group.classList.add('highlight-spec');
        }
    });
}
window.applyKeySpecHighlights = applyKeySpecHighlights;

document.addEventListener('DOMContentLoaded', () => {
    applyKeySpecHighlights();
    const jobInputSelector = 'input[name="job_no"], input[name="job_number"], input[id="job_no"], input[id="job_number"]';
    const jobNoInputs = document.querySelectorAll(jobInputSelector);
    
    jobNoInputs.forEach(input => {
        let lastAutoFetched = '';
        const triggerJobFetch = () => {
            const val = input.value.trim();
            if (val && val !== lastAutoFetched) {
                lastAutoFetched = val;
                if (typeof window.fetchJobNoData === 'function') {
                    window.fetchJobNoData();
                } else if (typeof window.fetchExcelData === 'function') {
                    window.fetchExcelData();
                }
            }
        };

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                triggerJobFetch();
            }
        });

        input.addEventListener('blur', () => {
            triggerJobFetch();
        });

        input.addEventListener('change', () => {
            triggerJobFetch();
        });
    });
});

// Universal Multi-System Selector Component for DWGs with Multiple Systems (e.g. SYSTEM 1, SYSTEM 2, SYSTEM 3)
window.renderMultiSystemSelector = function(multiSystems, onSelect) {
    if (!multiSystems || typeof multiSystems !== 'object') return;
    const sysNames = Object.keys(multiSystems);
    if (sysNames.length <= 1) return;

    let container = document.getElementById('multiSystemSelectorContainer');
    if (!container) {
        const step1 = document.getElementById('step-box-1') || document.getElementById('step-1') || document.querySelector('.step-panel') || document.querySelector('.section-box') || document.querySelector('form');
        if (step1) {
            container = document.createElement('div');
            container.id = 'multiSystemSelectorContainer';
            container.style.cssText = 'background: linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 100%); border: 1.5px solid #0284c7; border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.08); animation: fadeIn 0.3s ease;';
            const titleEl = step1.querySelector('.section-box-title') || step1.firstElementChild;
            if (titleEl && titleEl.nextSibling) {
                step1.insertBefore(container, titleEl.nextSibling);
            } else {
                step1.insertBefore(container, step1.firstChild);
            }
        }
    }
    if (!container) return;

    container.style.display = 'block';
    container.innerHTML = `
        <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="background: #0284c7; color: #fff; font-size: 11px; font-weight: 800; padding: 5px 12px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px;">
                    <i class="fa-solid fa-layer-group" style="margin-right: 5px;"></i> ${sysNames.length} Systems Detected
                </span>
                <span style="font-weight: 700; color: #0f172a; font-size: 13.5px;">Select System to Auto-Fill:</span>
            </div>
            <div id="multiSystemButtons" style="display: flex; gap: 8px; flex-wrap: wrap;">
                ${sysNames.map((sName, idx) => `
                    <button type="button" class="btn-multi-sys" data-sys="${sName}" style="padding: 7px 16px; border-radius: 8px; font-weight: 700; font-size: 13px; cursor: pointer; border: 1.5px solid #0284c7; transition: all 0.2s ease; ${idx === 0 ? 'background: #0284c7; color: #fff; box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3);' : 'background: #fff; color: #0284c7;'}">
                        ${sName}
                    </button>
                `).join('')}
            </div>
        </div>
    `;

    container.querySelectorAll('.btn-multi-sys').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            container.querySelectorAll('.btn-multi-sys').forEach(b => {
                b.style.background = '#fff';
                b.style.color = '#0284c7';
                b.style.boxShadow = 'none';
            });
            btn.style.background = '#0284c7';
            btn.style.color = '#fff';
            btn.style.boxShadow = '0 2px 6px rgba(2, 132, 199, 0.3)';
            const selName = btn.getAttribute('data-sys');
            const data = multiSystems[selName];
            if (data && typeof onSelect === 'function') {
                onSelect(data, selName);
            }
        });
    });
};
