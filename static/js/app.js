document.addEventListener('DOMContentLoaded', () => {
    
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

    function getServerBaseUrl() {
        if (window.location.protocol.startsWith('http')) {
            return window.location.origin;
        }
        const savedServerIp = localStorage.getItem('apex_wifi_server_ip') || '10.199.141.77:5000';
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

    function goToStep(step) {
        if (step < 1 || step > totalSteps) return;

        // Validate Step 1 before proceeding
        if (currentStep === 1 && step > 1) {
            const jobNo = document.getElementById('job_no')?.value.trim();
            const customer = document.getElementById('customer')?.value.trim();
            if (!jobNo || !customer) {
                showToast('Please fill required fields: Job Number and Customer Name.', 'error');
                return;
            }
        }

        currentStep = step;

        // Update Panels
        stepPanels.forEach((panel, idx) => {
            if (idx + 1 === currentStep) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });

        // Update Indicators & Progress Bar
        const fillPercent = (currentStep / totalSteps) * 100;
        if (progressFill) progressFill.style.width = `${fillPercent}%`;

        stepIndicators.forEach(ind => {
            const sNum = parseInt(ind.getAttribute('data-step'));
            ind.classList.remove('active');
            if (sNum === currentStep) {
                ind.classList.add('active');
            } else if (sNum < currentStep) {
                ind.classList.add('completed');
            } else {
                ind.classList.remove('completed');
            }
        });

        // Update Buttons
        
        
        

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    

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
        const names = ['Alex River', 'Sam Taylor', 'Jordan Lee', 'Chris Morgan', 'Morgan Vance', 'David Chen'];
        const customers = ['Titan Cement Ltd', 'UltraTech Minerals', 'JSW Steel Plant', 'Tata Steel Mining', 'Adani Power Thermal'];
        const randName = names[Math.floor(Math.random() * names.length)];
        const randCust = customers[Math.floor(Math.random() * customers.length)];
        const randJobNum = Math.floor(100 + Math.random() * 900);
        const randCap = [1000, 1200, 1500, 2000][Math.floor(Math.random() * 4)];
        const randSpeed = (1.5 + Math.random() * 1.5).toFixed(2);
        const dia = 0.318;
        const rpm = ((parseFloat(randSpeed) / (3.14159 * dia)) * 60).toFixed(1);

        // Step 1
        if (document.getElementById('job_no')) document.getElementById('job_no').value = `JOB-2026-${randJobNum}`;
        if (document.getElementById('customer')) document.getElementById('customer').value = randCust;
        if (document.getElementById('conveyor_no')) document.getElementById('conveyor_no').value = `CV-${Math.floor(10 + Math.random() * 90)}B`;
        if (document.getElementById('capacity')) document.getElementById('capacity').value = randCap.toString();
        if (document.getElementById('date')) document.getElementById('date').value = new Date().toISOString().split('T')[0];

        // Step 2
        if (document.getElementById('bs_model')) document.getElementById('bs_model').value = `BS-MODEL-${randJobNum}`;
        if (document.getElementById('bs_serial')) document.getElementById('bs_serial').value = `SN-BS-${7000 + randJobNum}`;
        if (document.getElementById('remote_model')) document.getElementById('remote_model').value = `RM-UNIT-01`;
        if (document.getElementById('remote_serial')) document.getElementById('remote_serial').value = `SN-RM-${5000 + randJobNum}`;

        if (document.getElementById('sensor_model')) document.getElementById('sensor_model').value = `LC-${randCap / 4}KG`;
        if (document.getElementById('sensor_s1')) document.getElementById('sensor_s1').value = `LC1-00${randJobNum % 10}`;
        if (document.getElementById('sensor_s2')) document.getElementById('sensor_s2').value = `LC2-00${randJobNum % 10}`;
        if (document.getElementById('sensor_s3')) document.getElementById('sensor_s3').value = `LC3-00${randJobNum % 10}`;
        if (document.getElementById('sensor_s4')) document.getElementById('sensor_s4').value = `LC4-00${randJobNum % 10}`;

        if (document.getElementById('tacho_model')) document.getElementById('tacho_model').value = `TACHO-SENS-PRO`;
        if (document.getElementById('tacho_serial')) document.getElementById('tacho_serial').value = `TS-${8000 + randJobNum}`;
        if (speedInput) speedInput.value = randSpeed;
        if (diaInput) diaInput.value = dia.toString();
        if (rpmInput) rpmInput.value = `${rpm} RPM`;

        if (document.getElementById('jbox_model1')) document.getElementById('jbox_model1').value = `JBOX-IP67`;
        if (document.getElementById('jbox_serial1')) document.getElementById('jbox_serial1').value = `JB-SN-${100 + randJobNum}`;

        // Step 3
        if (document.getElementById('short_check')) document.getElementById('short_check').value = `OK (Checked Line/Neutral, Neutral/Earth, Line/Earth)`;
        if (document.getElementById('res_l')) document.getElementById('res_l').value = `0.01`;
        if (document.getElementById('res_s')) document.getElementById('res_s').value = `0.001`;
        if (document.getElementById('res_r')) document.getElementById('res_r').value = `0.1`;
        if (document.getElementById('res_t')) document.getElementById('res_t').value = `0.001`;

        // Step 4 Routine Tests
        for (let i = 0; i < 9; i++) {
            const specElem = document.getElementById(`t_spec_${i}`);
            const actElem = document.getElementById(`t_act_${i}`);
            if (specElem && !specElem.value) specElem.value = defaultRoutineTests[i].spec;
            if (actElem) actElem.value = defaultRoutineTests[i].act;
        }

        // Step 5 Measurement Grid
        const activeCount = parseInt(numReadingsSelect ? numReadingsSelect.value : 5);
        const capNum = parseFloat(randCap);
        
        for (let i = 0; i < 11; i++) {
            if (i < activeCount) {
                const stepRatio = activeCount > 1 ? (i / (activeCount - 1.0)) : 0;
                const loadKg = (stepRatio * (capNum / 10.0)).toFixed(1);
                const beltKgM = (stepRatio * (capNum / 100.0) * 4.5).toFixed(1);
                const rateTph = (stepRatio * capNum).toFixed(1);
                const totT = (stepRatio * (capNum / 100.0) * 0.4).toFixed(3);
                const mA = (4.0 + stepRatio * 16.0).toFixed(2);

                if (document.getElementById(`g_${i}_0`)) document.getElementById(`g_${i}_0`).value = loadKg;
                if (document.getElementById(`g_${i}_1`)) document.getElementById(`g_${i}_1`).value = beltKgM;
                if (document.getElementById(`g_${i}_2`)) document.getElementById(`g_${i}_2`).value = randSpeed;
                if (document.getElementById(`g_${i}_3`)) document.getElementById(`g_${i}_3`).value = rateTph;
                if (document.getElementById(`g_${i}_4`)) document.getElementById(`g_${i}_4`).value = totT;
                if (document.getElementById(`g_${i}_5`)) document.getElementById(`g_${i}_5`).value = mA;
            } else {
                for (let c = 0; c < 6; c++) {
                    if (document.getElementById(`g_${i}_${c}`)) document.getElementById(`g_${i}_${c}`).value = '';
                }
            }
        }

        if (document.getElementById('instrument_used')) document.getElementById('instrument_used').value = `Fluke 87V Digital Multimeter & 50kg Calibrated Class F Weights`;

        showToast(`⚡ Demo Test Data Filled Successfully!`, 'success');
    }

    if (btnTopAutoFill) {
        btnTopAutoFill.addEventListener('click', fillDemoData);
    }
    document.querySelectorAll('.btnFillDemoDataGlobal').forEach(btn => {
        btn.addEventListener('click', fillDemoData);
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
                                    msg.innerHTML = '<i class="fa-solid fa-file-pdf" style="font-size:48px; color:#38bdf8; margin-bottom:16px;"></i><br><h3>PDF Generated Successfully!</h3><p>Android WebView does not support inline PDF previews.</p><p>Please tap the <b>Download</b> button above to view your document.</p>';
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

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (btnSubmitPDF) {
                btnSubmitPDF.disabled = true;
                btnSubmitPDF.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Document...';
            }

            const formData = new FormData(form);
            const payload = {};
            formData.forEach((value, key) => { payload[key] = value; });

            // Gather Routine Tests
            payload.routine_tests = [];
            for (let i = 0; i < 9; i++) {
                const specVal = document.getElementById(`t_spec_${i}`) ? document.getElementById(`t_spec_${i}`).value : '';
                const actVal = document.getElementById(`t_act_${i}`) ? document.getElementById(`t_act_${i}`).value : '';
                payload.routine_tests.push({ spec: specVal, act: actVal });
            }

            // Gather Measurement Grid
            const activeCount = parseInt(numReadingsSelect ? numReadingsSelect.value : 5);
            payload.grid_data = [];
            for (let i = 0; i < 11; i++) {
                const rowVals = [];
                for (let c = 0; c < 6; c++) {
                    const cellVal = (i < activeCount && document.getElementById(`g_${i}_${c}`)) ? document.getElementById(`g_${i}_${c}`).value : '';
                    rowVals.push(cellVal);
                }
                payload.grid_data.push(rowVals);
            }

            // ALWAYS TRY DIRECT SERVER SUBMIT FIRST OVER WI-FI IP OR LOCALHOST
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 6000);

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
                    showToast('Report Saved to Database & Document Generated!', 'success');
                    
                    const pdfUrl = result.pdf_download_url || `${getServerBaseUrl()}/download/${result.pdf_filename}`;
                    if (pdfUrl) {
                        // Instead of direct download, show the preview modal if it exists
                        if (typeof showPdfPreview === "function") {
                            showPdfPreview(pdfUrl, result.pdf_filename);
                        } else {
                            const modal = document.getElementById("pdfPreviewModal");
                            if (modal) {
                                document.getElementById("modalPreviewTitle").textContent = result.pdf_filename || "Document";
                                document.getElementById("pdfPreviewIframe").src = pdfUrl;
                                document.getElementById("btnModalDownloadPDF").href = pdfUrl;
                                modal.style.display = "flex";
                            }
                        }
                    }

                    await loadHistory();
                    goToStep(1);
                    return;
                } else {
                    showToast('Error: ' + result.message, 'error');
                    return;
                }
            } catch (err) {
                // Server network unreachable -> fallback to local storage save!
                console.log('Server unreachable, saving locally:', err);
                isServerOnline = false;
                updateNetworkStatusIndicator();
                saveOfflineRecord(payload);
                goToStep(1);
            } finally {
                if (btnSubmitPDF) {
                    btnSubmitPDF.disabled = false;
                    btnSubmitPDF.innerHTML = '<i class="fa-solid fa-file-pdf"></i> Submit & Generate Report';
                }
            }
        });
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
