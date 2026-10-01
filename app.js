// EcoTrace | CARBONPULSE - Multi-Page Routing & Interactive Script

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // Initialize Routing & Charts
    initRouter();
    initOverviewHeroChart();
    initAnalyticsPageChart();
    initDonutCharts();
    renderCarbonLeagueTables();
    renderDepartmentCards();
    initSimulator();
    setupEventListeners();
});

/* ==========================================================================
   1. GLOBAL DEMO DATA STORE
   ========================================================================== */
const campusData = {
    institution: "D. Y. Patil College of Engineering",
    totalStudents: 1350,
    currentEmissions: 24850, // kg CO2e
    previousEmissions: 27130,
    energyCost: 124850, // ₹

    departments: [
        { name: "AIML Department", code: "AIML", students: 280, totalCo2: 3976, perCapita: 14.2, change: -12.4, status: "GREEN", electricity: 2100, transport: 1200, food: 450, computing: 226 },
        { name: "Computer Science", code: "CSE", students: 420, totalCo2: 7056, perCapita: 16.8, change: -8.7, status: "GREEN", electricity: 3800, transport: 1800, food: 956, computing: 500 },
        { name: "E&TC Engineering", code: "E&TC", students: 250, totalCo2: 4850, perCapita: 19.4, change: 3.2, status: "YELLOW", electricity: 2600, transport: 1150, food: 700, computing: 400 },
        { name: "Mechanical Engg.", code: "Mechanical", students: 220, totalCo2: 5302, perCapita: 24.1, change: 9.8, status: "RED", electricity: 3200, transport: 1300, food: 602, computing: 200 },
        { name: "Civil Engineering", code: "Civil", students: 180, totalCo2: 5130, perCapita: 28.5, change: 4.1, status: "RED", electricity: 2900, transport: 1250, food: 780, computing: 200 }
    ],

    monthlyHistory: {
        labels: ["Apr", "May", "Jun", "Jul", "Aug", "Sep"],
        totalCo2: [31200, 29800, 28500, 27600, 27130, 24850],
        perCapita: [23.1, 22.0, 21.1, 20.4, 20.1, 18.4],
        energyCost: [156000, 149000, 142500, 138000, 133100, 124850]
    }
};

/* ==========================================================================
   2. MULTI-PAGE ROUTER LOGIC
   ========================================================================== */
const pageTitles = {
    'overview': { title: 'Campus Overview', subtitle: 'Carbon footprint and sustainability performance' },
    'analytics': { title: 'Carbon Analytics', subtitle: 'Historical emissions data, Scope 1-3 trends, and cost correlation' },
    'sources': { title: 'Carbon Sources', subtitle: 'Detailed breakdown of electricity, transport, food, and computing' },
    'departments': { title: 'Campus Departments', subtitle: 'Departmental carbon footprints and per-student comparisons' },
    'league': { title: 'Carbon League', subtitle: 'Fair departmental leaderboard ranked strictly by CO₂e per student' },
    'mess': { title: 'Mess & Food Carbon', subtitle: 'Meal carbon intensity ratings and Green Day scheduler' },
    'energy': { title: 'Energy & Lab Analytics', subtitle: 'Statistical anomaly detection and solar timing tips' },
    'scanner': { title: 'MSEDCL Bill Scanner', subtitle: 'Upload electricity bill for Marathi & Hindi Tesseract OCR calculation' },
    'simulator': { title: 'What-If Simulator', subtitle: 'Interactive operational decision simulation and budget forecasting' },
    'recommendations': { title: 'Recommended Actions', subtitle: 'AI and analytics driven targeted sustainability measures' },
    'naac': { title: 'NAAC / NIRF Green Audit Report', subtitle: 'One-click institutional compliance report generator' }
};

function initRouter() {
    window.addEventListener('hashchange', handleHashChange);
    handleHashChange();
}

function handleHashChange() {
    let pageId = window.location.hash.replace('#', '');
    if (!pageId || !pageTitles[pageId]) {
        pageId = 'overview';
    }
    navigateToPage(pageId, false);
}

function navigateToPage(pageId, updateHash = true) {
    if (updateHash) {
        window.location.hash = pageId;
    }

    // Hide all page views
    document.querySelectorAll('.page-view').forEach(view => {
        view.classList.add('hidden');
    });

    // Show target page view
    const targetPage = document.getElementById(`page-${pageId}`) || document.getElementById('page-overview');
    targetPage.classList.remove('hidden');

    // Update active nav link
    document.querySelectorAll('.nav-item').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === pageId) {
            link.classList.add('active');
        }
    });

    // Update Header Text
    const meta = pageTitles[pageId] || pageTitles['overview'];
    document.getElementById('pageTitle').innerText = meta.title;
    document.getElementById('pageSubtitle').innerHTML = `${meta.subtitle} • <span class="tagline-highlight">"Measure. Understand. Reduce."</span>`;

    // Scroll to top of dashboard content
    document.getElementById('dashboardBody').scrollTop = 0;

    // Refresh icons
    if (window.lucide) window.lucide.createIcons();
}

/* ==========================================================================
   3. CHARTS INITIALIZATION (OVERVIEW & ANALYTICS PAGES)
   ========================================================================== */
let overviewChartInstance = null;
let analyticsChartInstance = null;

function initOverviewHeroChart() {
    const ctx = document.getElementById('heroTrendChart');
    if (!ctx) return;

    const chartCtx = ctx.getContext('2d');
    const gradient = chartCtx.createLinearGradient(0, 0, 0, 280);
    gradient.addColorStop(0, 'rgba(22, 163, 74, 0.35)');
    gradient.addColorStop(1, 'rgba(22, 163, 74, 0.01)');

    overviewChartInstance = new Chart(chartCtx, {
        type: 'line',
        data: {
            labels: campusData.monthlyHistory.labels,
            datasets: [{
                label: 'Total CO₂e (kg)',
                data: campusData.monthlyHistory.totalCo2,
                borderColor: '#16A34A',
                borderWidth: 3,
                backgroundColor: gradient,
                fill: true,
                tension: 0.35,
                pointBackgroundColor: '#FFFFFF',
                pointBorderColor: '#16A34A',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { color: '#6B756E', font: { family: 'Inter', weight: 600 } } },
                y: { grid: { color: '#F0F2F0' }, ticks: { color: '#6B756E' } }
            }
        }
    });
}

function initAnalyticsPageChart() {
    const ctx = document.getElementById('pageAnalyticsChart');
    if (!ctx) return;

    const chartCtx = ctx.getContext('2d');
    analyticsChartInstance = new Chart(chartCtx, {
        type: 'line',
        data: {
            labels: campusData.monthlyHistory.labels,
            datasets: [
                {
                    label: 'Total CO₂e (kg)',
                    data: campusData.monthlyHistory.totalCo2,
                    borderColor: '#16A34A',
                    borderWidth: 3,
                    tension: 0.3,
                    pointRadius: 5
                },
                {
                    label: 'Energy Cost (₹)',
                    data: campusData.monthlyHistory.energyCost.map(c => Math.round(c / 5)), // scaled for visual dual axis
                    borderColor: '#D97706',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.3,
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: {
                x: { grid: { display: false } },
                y: { grid: { color: '#F0F2F0' } }
            }
        }
    });
}

function initDonutCharts() {
    const ctx1 = document.getElementById('sourcesDonutChart');
    if (ctx1) {
        new Chart(ctx1.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Electricity', 'Transportation', 'Food / Mess', 'Computing'],
                datasets: [{ data: [48, 27, 17, 8], backgroundColor: ['#16A34A', '#0D9488', '#F59E0B', '#6366F1'], borderWidth: 0 }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '72%', plugins: { legend: { display: false } } }
        });
    }

    const ctx2 = document.getElementById('pageSourcesDonutChart');
    if (ctx2) {
        new Chart(ctx2.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Electricity (48%)', 'Transportation (27%)', 'Food (17%)', 'Computing (8%)'],
                datasets: [{ data: [48, 27, 17, 8], backgroundColor: ['#16A34A', '#0D9488', '#F59E0B', '#6366F1'], borderWidth: 0 }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: { legend: { position: 'bottom' } } }
        });
    }
}

/* ==========================================================================
   4. CARBON LEAGUE & DEPARTMENT CARDS
   ========================================================================== */
function renderCarbonLeagueTables() {
    const sortedDepts = [...campusData.departments].sort((a, b) => a.perCapita - b.perCapita);
    const tbodyPage = document.getElementById('leagueTableBodyPage');

    if (tbodyPage) {
        tbodyPage.innerHTML = '';
        sortedDepts.forEach((dept, idx) => {
            const rank = idx + 1;
            const rankClass = rank === 1 ? 'top-1' : rank === 2 ? 'top-2' : '';
            const badgeClass = dept.status === 'GREEN' ? 'badge-success' : dept.status === 'YELLOW' ? 'badge-warning' : 'badge-danger';
            const changeArrow = dept.change < 0 ? '↓' : '↑';
            const changeColor = dept.change < 0 ? 'text-success' : 'text-danger';

            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="rank-badge ${rankClass}">0${rank}</span></td>
                <td><span class="dept-name" onclick="openDeptModal('${dept.code}')">${dept.name}</span></td>
                <td>${dept.students}</td>
                <td><strong>${dept.perCapita} kg</strong></td>
                <td class="${changeColor}"><strong>${changeArrow} ${Math.abs(dept.change)}%</strong></td>
                <td><span class="badge ${badgeClass}">${dept.status}</span></td>
                <td><button class="btn btn-sm btn-secondary" onclick="openDeptModal('${dept.code}')">View Details</button></td>
            `;
            tbodyPage.appendChild(row);
        });
    }
}

function renderDepartmentCards() {
    const container = document.getElementById('deptCardsGrid');
    if (!container) return;

    container.innerHTML = '';
    campusData.departments.forEach(dept => {
        const badgeClass = dept.status === 'GREEN' ? 'badge-success' : dept.status === 'YELLOW' ? 'badge-warning' : 'badge-danger';
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div class="card-header border-b">
                <div>
                    <h4 class="card-title">${dept.name}</h4>
                    <p class="card-subtitle">${dept.students} Enrolled Students</p>
                </div>
                <span class="badge ${badgeClass}">${dept.status}</span>
            </div>
            <div style="margin-top: 14px; display: flex; flex-direction: column; gap: 8px;">
                <div class="stat-mini-row"><span>CO₂e / Student:</span><strong class="text-emerald">${dept.perCapita} kg</strong></div>
                <div class="stat-mini-row"><span>Total CO₂e:</span><strong>${dept.totalCo2.toLocaleString()} kg</strong></div>
                <div class="stat-mini-row"><span>Electricity:</span><span>${dept.electricity} kg</span></div>
                <div class="stat-mini-row"><span>Transportation:</span><span>${dept.transport} kg</span></div>
            </div>
            <button class="btn btn-sm btn-outline-emerald w-full" style="margin-top: 16px;" onclick="openDeptModal('${dept.code}')">
                Department Audit
            </button>
        `;
        container.appendChild(card);
    });
}

/* ==========================================================================
   5. BILL SCANNER & OCR WORKFLOW
   ========================================================================== */
let selectedOcrLang = 'en';

function triggerFileInput() {
    const input = document.getElementById('billFileInputPage');
    if (input) input.click();
}

function handleBillUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    document.getElementById('billDropzonePage').classList.add('hidden');
    document.getElementById('ocrProgressContainerPage').classList.remove('hidden');
    document.getElementById('ocrResultCardPage').classList.add('hidden');

    runOcrSimulation();
}

function runOcrSimulation() {
    const progressBar = document.getElementById('ocrProgressBarPage');
    const statusText = document.getElementById('ocrStatusTextPage');

    let progress = 0;
    const interval = setInterval(() => {
        progress += 25;
        if (progressBar) progressBar.style.width = `${progress}%`;

        if (progress === 25) {
            statusText.innerText = selectedOcrLang === 'mr' ? 'मराठी मजकूर वाचत आहे (Processing Marathi OCR)...' :
                selectedOcrLang === 'hi' ? 'हिन्दी पाठ संसाधित कर रहा है (Processing Hindi OCR)...' :
                    'Scanning MSEDCL bill text via Tesseract OCR...';
        } else if (progress === 50) {
            statusText.innerText = 'Extracting kWh Units: 12,500 kWh detected.';
        } else if (progress === 75) {
            statusText.innerText = 'Applying Maharashtra Grid Emission Factor (0.71 kg/kWh)...';
        } else if (progress >= 100) {
            clearInterval(interval);
            setTimeout(() => {
                document.getElementById('ocrProgressContainerPage').classList.add('hidden');
                document.getElementById('ocrResultCardPage').classList.remove('hidden');
                showToast('Bill OCR Complete', 'Extracted 12,500 kWh with Marathi/Hindi OCR model.');
            }, 400);
        }
    }, 450);
}

function confirmAddBillToFootprint() {
    campusData.currentEmissions += 8875;
    document.getElementById('kpiTotalCarbon').innerHTML = `${campusData.currentEmissions.toLocaleString()} <span class="unit">kg CO₂e</span>`;
    showToast('Campus Footprint Updated', '8,875 kg CO₂e added to campus footprint.');
    resetBillScanner();
}

function resetBillScanner() {
    document.getElementById('billDropzonePage').classList.remove('hidden');
    document.getElementById('ocrProgressContainerPage').classList.add('hidden');
    document.getElementById('ocrResultCardPage').classList.add('hidden');
    const input = document.getElementById('billFileInputPage');
    if (input) input.value = '';
}

/* ==========================================================================
   6. WHAT-IF SIMULATOR CALCULATIONS
   ========================================================================== */
function initSimulator() {
    updateSimulator();
}

function updateSimulator() {
    const sliderPc = document.getElementById('sliderPcTimePage');
    if (!sliderPc) return;

    const pcTime = parseInt(sliderPc.value);
    const carpoolPct = parseInt(document.getElementById('sliderCarpoolPage').value);
    const solarKw = parseInt(document.getElementById('sliderSolarPage').value);

    document.getElementById('valPcTimePage').innerText = pcTime === 6 ? '6 PM (Automatic)' : `${pcTime} PM`;
    document.getElementById('valCarpoolPage').innerText = `${carpoolPct}%`;
    document.getElementById('valSolarPage').innerText = `${solarKw} kW`;

    const pcHoursSaved = (10 - pcTime);
    const pcKwhSaved = pcHoursSaved * 450;
    const pcCostSaved = pcKwhSaved * 8;
    const pcCo2Saved = Math.round(pcKwhSaved * 0.71);

    document.getElementById('simPcSavesKwhPage').innerText = `${pcKwhSaved.toLocaleString()} kWh`;
    document.getElementById('simPcSavesCostPage').innerText = `₹${pcCostSaved.toLocaleString()}/mo`;
    document.getElementById('simPcSavesCo2Page').innerText = `${pcCo2Saved.toLocaleString()} kg CO₂e/mo`;

    const carpoolCo2Saved = Math.round((carpoolPct / 25) * 1250);
    const carpoolCostSaved = Math.round((carpoolPct / 25) * 12500);

    document.getElementById('simCarpoolCo2Page').innerText = `${carpoolCo2Saved.toLocaleString()} kg/mo`;
    document.getElementById('simCarpoolCostPage').innerText = `₹${carpoolCostSaved.toLocaleString()}/mo`;

    const solarCo2Annual = solarKw * 300;
    const solarPayback = solarKw === 0 ? 'N/A' : (4.0 - (solarKw / 100) * 1.5).toFixed(1) + ' years';

    document.getElementById('simSolarCo2Page').innerText = `${solarCo2Annual.toLocaleString()} kg/yr`;
    document.getElementById('simSolarPaybackPage').innerText = solarPayback;

    const totalMonthlyReduction = pcCo2Saved + carpoolCo2Saved + Math.round(solarCo2Annual / 12);
    const totalCostReduction = pcCostSaved + carpoolCostSaved + Math.round((solarKw * 1500) / 12);
    const simulatedFootprint = Math.max(0, campusData.currentEmissions - totalMonthlyReduction);

    document.getElementById('simulatedFootprintValPage').innerHTML = `${simulatedFootprint.toLocaleString()} <small>kg CO₂e</small>`;
    document.getElementById('simulatedReductionValPage').innerHTML = `${totalMonthlyReduction.toLocaleString()} <small>kg CO₂e / mo</small>`;
    document.getElementById('simulatedCostReductionValPage').innerText = `Savings: ₹${totalCostReduction.toLocaleString()} / month`;
}

function resetSimulator() {
    document.getElementById('sliderPcTimePage').value = 6;
    document.getElementById('sliderCarpoolPage').value = 25;
    document.getElementById('sliderSolarPage').value = 50;
    updateSimulator();
    showToast('Simulator Reset', 'Restored baseline parameters.');
}

function applySimulatorScenario() {
    showToast('Scenario Applied', 'Simulated operational parameters saved.');
}

function simulateRecommendation(id) {
    navigateToPage('simulator');
    if (id === 1) document.getElementById('sliderPcTimePage').value = 6;
    if (id === 2) document.getElementById('sliderCarpoolPage').value = 30;
    if (id === 3) document.getElementById('sliderSolarPage').value = 75;
    updateSimulator();
    showToast('Recommendation Loaded', `Scenario #${id} loaded into What-If Simulator.`);
}

/* ==========================================================================
   7. REPORT GENERATOR & MODALS
   ========================================================================== */
function triggerReportGeneration() {
    const modal = document.getElementById('reportModal');
    const loadingState = document.getElementById('reportLoadingState');
    const previewState = document.getElementById('reportPreviewState');
    const downloadBtn = document.getElementById('downloadPdfBtn');

    modal.classList.remove('hidden');
    loadingState.classList.remove('hidden');
    previewState.classList.add('hidden');
    downloadBtn.disabled = true;

    const stepText = document.getElementById('reportStepText');
    const steps = [
        'Compiling Scope 1, 2 & 3 Emissions Data...',
        'Calculating Departmental Per-Student Benchmarks...',
        'Structuring Tables under NAAC Criterion 7.1.6...',
        'Finalizing NIRF Sustainability Accreditation Audit...'
    ];

    let i = 0;
    const interval = setInterval(() => {
        if (i < steps.length) {
            stepText.innerText = steps[i];
            i++;
        } else {
            clearInterval(interval);
            loadingState.classList.add('hidden');
            previewState.classList.remove('hidden');
            downloadBtn.disabled = false;
        }
    }, 450);
}

function previewReportModal() { triggerReportGeneration(); }

function downloadPdfSimulated() {
    showToast('PDF Downloaded', 'NAAC_NIRF_Green_Audit_Report_2026.pdf generated.');
    closeModal('reportModal');
}

let anomalyChartInstance = null;
function openAnomalyInvestigationModal() {
    const modal = document.getElementById('anomalyModal');
    modal.classList.remove('hidden');

    setTimeout(() => {
        const ctx = document.getElementById('anomalyDetailChart').getContext('2d');
        if (anomalyChartInstance) anomalyChartInstance.destroy();

        anomalyChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jun', 'Jul', 'Aug', 'Sep (Current)'],
                datasets: [
                    { label: 'Historical Baseline (kWh)', data: [10200, 9900, 10000, 10000], backgroundColor: '#CBD5E1' },
                    { label: 'Chemistry Lab Actual (kWh)', data: [10100, 9950, 10050, 14200], backgroundColor: ['#16A34A', '#16A34A', '#16A34A', '#F59E0B'] }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }, 100);
}

function resolveAnomaly() {
    showToast('Anomaly Flagged', 'Chemistry Lab maintenance ticket generated.');
    closeModal('anomalyModal');
}

function openDeptModal(deptCode) {
    const dept = campusData.departments.find(d => d.code === deptCode);
    if (!dept) return;

    const modal = document.getElementById('deptModal');
    document.getElementById('deptModalTitle').innerText = `${dept.name} — Sustainability Audit`;

    document.getElementById('deptModalBody').innerHTML = `
        <div class="pdf-grid-2" style="margin-bottom: 20px;">
            <div class="pdf-box">
                <h5>Department Overview</h5>
                <p><strong>Total Students:</strong> ${dept.students}</p>
                <p><strong>Total Monthly Emissions:</strong> ${dept.totalCo2.toLocaleString()} kg CO₂e</p>
                <p><strong>CO₂e / Student:</strong> ${dept.perCapita} kg (Ranked by per-capita)</p>
            </div>
            <div class="pdf-box">
                <h5>Source Breakdown</h5>
                <p><strong>Electricity:</strong> ${dept.electricity} kg CO₂e</p>
                <p><strong>Transportation:</strong> ${dept.transport} kg CO₂e</p>
                <p><strong>Food / Mess:</strong> ${dept.food} kg CO₂e</p>
                <p><strong>Computing:</strong> ${dept.computing} kg CO₂e</p>
            </div>
        </div>
        <div style="background: var(--bg-app); padding: 14px; border-radius: var(--radius-md);">
            <h5 style="margin-bottom: 6px; font-weight: 700; color: var(--emerald-700);">Recommended Action for ${dept.name}</h5>
            <p style="font-size: 0.85rem; color: var(--text-secondary);">Enforce auto shutdown policy in lab PCs after 6 PM to reduce footprint by ~8.5%.</p>
        </div>
    `;

    modal.classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

/* ==========================================================================
   8. EVENT LISTENERS & TOASTS
   ========================================================================== */
function setupEventListeners() {
    document.querySelectorAll('.nav-item').forEach(link => {
        link.addEventListener('click', (e) => {
            const pageId = e.currentTarget.getAttribute('data-page');
            navigateToPage(pageId);
        });
    });

    const mobileBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.querySelector('.sidebar');
    if (mobileBtn) {
        mobileBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }
}

function toggleAddDataDropdown() {
    document.getElementById('addDataDropdown').classList.toggle('hidden');
}

function openManualInputModal(type) {
    showToast('Manual Entry Logged', `Logged manual entry for ${type}.`);
    toggleAddDataDropdown();
}

function toggleGreenDay() {
    showToast('Green Day Initiative', 'Wednesdays marked as vegetarian Green Day across campus canteens.');
}

function showToast(title, message) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <i data-lucide="check-circle-2"></i>
        <div>
            <strong>${title}</strong>
            <p style="font-size: 0.76rem; color: var(--text-muted);">${message}</p>
        </div>
    `;
    container.appendChild(toast);
    if (window.lucide) window.lucide.createIcons();

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}
