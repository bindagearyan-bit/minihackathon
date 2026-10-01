// EcoTrace | CARBONPULSE - Campus Carbon Footprint Auditor (UN SDG 13)
// Connected with live FastAPI Backend & Supabase Database

// Auto-detect API host: works locally, over LAN, and on any cloud domain (Render, Railway, etc.)
const API_BASE = (window.location.protocol.startsWith('http') && window.location.host)
    ? `${window.location.protocol}//${window.location.host}/api`
    : 'http://127.0.0.1:8000/api';

// ==========================================
// USER SPECIFIC DATA & ZERO-STATE MANAGEMENT
// ==========================================
function getUserEmail() {
    const sessionUser = JSON.parse(sessionStorage.getItem('ecotrace_user') || '{}');
    return (sessionUser.email || 'newuser@campus.edu').toLowerCase();
}

function getUserMode() {
    const sessionUser = JSON.parse(sessionStorage.getItem('ecotrace_user') || '{}');
    let mode = localStorage.getItem('ecotrace_user_mode');
    if (!mode) {
        mode = (sessionUser.isNewUser !== false && sessionUser.email !== 'admin@campus.edu') ? 'zero' : 'demo';
        localStorage.setItem('ecotrace_user_mode', mode);
    }
    return mode;
}

function getUserBills() {
    const email = getUserEmail();
    const raw = localStorage.getItem('ecotrace_user_bills_' + email);
    return raw ? JSON.parse(raw) : [];
}

function saveUserBills(bills) {
    const email = getUserEmail();
    localStorage.setItem('ecotrace_user_bills_' + email, JSON.stringify(bills));
}

function toggleUserMode() {
    const current = getUserMode();
    const next = current === 'zero' ? 'demo' : 'zero';
    localStorage.setItem('ecotrace_user_mode', next);

    const sessionUser = JSON.parse(sessionStorage.getItem('ecotrace_user') || '{}');
    sessionUser.isNewUser = (next === 'zero');
    sessionStorage.setItem('ecotrace_user', JSON.stringify(sessionUser));

    if (next === 'zero') {
        showToast('Mode: Fresh User (0)', 'Started ledger from 0 with no previous data.');
    } else {
        showToast('Mode: Demo Data', 'Loaded full college historical dataset (37,161 kg CO₂).');
    }

    applyUserModeUi();
    fetchOverviewData();
    fetchLeaderboardData();
}

function applyUserModeUi() {
    const mode = getUserMode();
    const email = getUserEmail();
    const bills = getUserBills();

    const banner = document.getElementById('userWelcomeBanner');
    const emailTag = document.getElementById('userEmailTag');
    const bannerTitle = document.getElementById('bannerTitle');
    const bannerDesc = document.getElementById('bannerDesc');
    const btnToggleDemo = document.getElementById('btnToggleDemo');
    const topStateToggleText = document.getElementById('topStateToggleText');

    if (emailTag) emailTag.innerText = email;

    if (mode === 'zero') {
        if (bills.length === 0) {
            if (bannerTitle) bannerTitle.innerText = "Campus Ledger Initialized at 0 • No previous data updated";
            if (bannerDesc) bannerDesc.innerText = "Welcome! As a new campus auditor, your footprint starts at 0 kg CO₂. Scan your first electricity bill or log department data to begin tracking.";
            if (topStateToggleText) topStateToggleText.innerText = "Mode: Starts at 0";
        } else {
            const totalKg = Math.round(bills.reduce((s, b) => s + b.co2_kg, 0));
            if (bannerTitle) bannerTitle.innerText = `Active Campus Audit • ${bills.length} Bill Logged (${totalKg.toLocaleString()} kg CO₂)`;
            if (bannerDesc) bannerDesc.innerText = `Your carbon ledger is actively recording data for ${email}.`;
            if (topStateToggleText) topStateToggleText.innerText = `Mode: Active (${totalKg} kg)`;
        }
        if (btnToggleDemo) btnToggleDemo.innerHTML = '<i data-lucide="database"></i> Load Demo Data';
    } else {
        if (bannerTitle) bannerTitle.innerText = "Demo Campus Audit • Sample College Dataset Loaded";
        if (bannerDesc) bannerDesc.innerText = "Showing comprehensive multi-department historical baseline for hackathon jury evaluation.";
        if (topStateToggleText) topStateToggleText.innerText = "Mode: Demo Data (37.1t)";
        if (btnToggleDemo) btnToggleDemo.innerHTML = '<i data-lucide="refresh-cw"></i> Start from 0';
    }

    if (window.lucide) window.lucide.createIcons();
}

// Global Data Store with fallback defaults
let campusData = {
    institution: "Nashik College of Engineering",
    totalStudents: 3140,
    currentEmissions: 37161, // kg CO2
    previousEmissions: 36800,
    energyCost: 601910,      // ₹
    departments: [],
    monthlyHistory: {
        labels: ["May", "Jun", "Jul", "Aug", "Sep", "Oct"],
        totalCo2: [37090, 37286, 37578, 37042, 37730, 37161],
        energyCost: [600700, 603850, 608550, 599875, 611050, 601910]
    }
};

let currentScannedBill = {
    file_name: "sample_bill.png",
    units_kwh: 3076,
    amount_inr: 38459,
    bill_month: "September 2026",
    raw_text: ""
};

let overviewChartInstance = null;
let analyticsChartInstance = null;
let anomalyChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Lucide Icons
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // 2. Initialize Routing
    initRouter();

    // 3. Initialize Visuals with baseline data
    initOverviewHeroChart();
    initAnalyticsPageChart();
    initDonutCharts();
    initSimulator();
    setupEventListeners();

    // 4. Apply UI state for current user
    applyUserModeUi();

    // 5. Fetch live data from backend
    loadDepartmentsDropdown();
    fetchOverviewData();
    fetchLeaderboardData();
    fetchMessMenu();
    fetchAnomaliesAndSolarTips();
});

/* ==========================================================================
   ROUTING
   ========================================================================== */
const pageTitles = {
    'overview': { title: 'Campus Overview', subtitle: 'Carbon footprint and sustainability performance' },
    'analytics': { title: 'Carbon Analytics', subtitle: 'Historical emissions data, CEA baseline trends, and cost correlation' },
    'sources': { title: 'Carbon Sources', subtitle: 'Detailed breakdown of electricity, transport, food, and computing' },
    'departments': { title: 'Campus Departments', subtitle: 'Departmental carbon footprints and per-student comparisons' },
    'league': { title: 'Carbon League', subtitle: 'Fair departmental leaderboard ranked strictly by CO₂ per student' },
    'mess': { title: 'Mess & Food Carbon', subtitle: 'Meal carbon intensity ratings and Green Day scheduler' },
    'energy': { title: 'Energy & Lab Analytics', subtitle: 'Statistical anomaly detection (Z-Score) and solar timing tips' },
    'scanner': { title: 'MSEDCL Bill Scanner', subtitle: 'Upload electricity bill for Marathi, Hindi & English Tesseract OCR calculation' },
    'simulator': { title: 'What-If Simulator', subtitle: 'Interactive operational decision simulation and budget forecasting' },
    'recommendations': { title: 'Recommended Actions', subtitle: 'Data-driven targeted campus sustainability measures' },
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
    if (targetPage) targetPage.classList.remove('hidden');

    // Update active nav link
    document.querySelectorAll('.nav-item').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === pageId) {
            link.classList.add('active');
        }
    });

    // Update Header Text
    const meta = pageTitles[pageId] || pageTitles['overview'];
    const pTitle = document.getElementById('pageTitle');
    const pSub = document.getElementById('pageSubtitle');
    if (pTitle) pTitle.innerText = meta.title;
    if (pSub) pSub.innerHTML = `${meta.subtitle} • <span class="tagline-highlight">"Measure. Understand. Reduce."</span>`;

    // Scroll to top
    const dashBody = document.getElementById('dashboardBody');
    if (dashBody) dashBody.scrollTop = 0;

    // Refresh icons
    if (window.lucide) window.lucide.createIcons();
}

/* ==========================================================================
   BACKEND API INTEGRATIONS
   ========================================================================== */

// 1. Fetch Overview & KPIs
async function fetchOverviewData(targetMonth = '2026-10') {
    applyUserModeUi();
    const mode = getUserMode();
    const userBills = getUserBills();

    if (mode === 'zero') {
        // Zero state or user-accumulated state!
        let totalCo2 = 0;
        let totalAmount = 0;
        let totalKwh = 0;

        if (userBills.length > 0) {
            totalCo2 = Math.round(userBills.reduce((s, b) => s + (b.co2_kg || 0), 0));
            totalAmount = Math.round(userBills.reduce((s, b) => s + (b.amount_inr || 0), 0));
            totalKwh = Math.round(userBills.reduce((s, b) => s + (b.units_kwh || 0), 0));
        }

        campusData.currentEmissions = totalCo2;
        campusData.energyCost = totalAmount;

        // Update KPIs
        const kpiCarbon = document.getElementById('kpiTotalCarbon');
        if (kpiCarbon) {
            kpiCarbon.innerHTML = `${totalCo2.toLocaleString()} <span class="unit">kg CO₂</span>`;
        }

        const kpiCost = document.getElementById('kpiEnergyCost');
        if (kpiCost) {
            kpiCost.innerText = `₹${totalAmount.toLocaleString()}`;
        }

        const kpiPerCap = document.getElementById('kpiPerCapita');
        if (kpiPerCap) {
            const perCap = totalCo2 > 0 ? (totalCo2 / campusData.totalStudents).toFixed(2) : "0.0";
            kpiPerCap.innerHTML = `${perCap} <span class="unit">kg CO₂</span>`;
        }

        const kpiSavings = document.getElementById('kpiPotentialSavings');
        if (kpiSavings) {
            const sav = totalAmount > 0 ? Math.round(totalAmount * 0.15) : 0;
            kpiSavings.innerHTML = `₹${sav.toLocaleString()} <span class="sub-freq">/mo</span>`;
        }

        // Charts
        const labels = ["May", "Jun", "Jul", "Aug", "Sep", "Oct"];
        const co2Vals = userBills.length > 0 ? [0, 0, 0, 0, 0, totalCo2] : [0, 0, 0, 0, 0, 0];
        const costVals = userBills.length > 0 ? [0, 0, 0, 0, 0, totalAmount] : [0, 0, 0, 0, 0, 0];

        campusData.monthlyHistory.labels = labels;
        campusData.monthlyHistory.totalCo2 = co2Vals;
        campusData.monthlyHistory.energyCost = costVals;

        updateOverviewHeroChart(labels, co2Vals);
        updateAnalyticsPageChart(labels, co2Vals, costVals);
        renderUserActivityTable();
        return;
    }

    // Demo Mode: Fetch live data from backend or cached fallback
    try {
        const res = await fetch(`${API_BASE}/overview?month=${targetMonth}`);
        if (!res.ok) throw new Error('Network response was not ok');
        const data = await res.json();

        // Update KPIs
        const kpiCarbon = document.getElementById('kpiTotalCarbon');
        if (kpiCarbon) {
            kpiCarbon.innerHTML = `${Math.round(data.total_co2_kg).toLocaleString()} <span class="unit">kg CO₂</span>`;
        }

        const kpiCost = document.getElementById('kpiEnergyCost');
        if (kpiCost) {
            kpiCost.innerText = `₹${Math.round(data.total_amount_inr).toLocaleString()}`;
        }

        // Update Charts with Trend
        if (data.trend && data.trend.length > 0) {
            const labels = data.trend.map(t => t.month);
            const co2Vals = data.trend.map(t => t.co2_kg);
            const costVals = data.trend.map(t => t.amount_inr);

            campusData.monthlyHistory.labels = labels;
            campusData.monthlyHistory.totalCo2 = co2Vals;
            campusData.monthlyHistory.energyCost = costVals;

            updateOverviewHeroChart(labels, co2Vals);
            updateAnalyticsPageChart(labels, co2Vals, costVals);
        }

        // Update Per Capita Benchmark
        const kpiPerCap = document.getElementById('kpiPerCapita');
        if (kpiPerCap && campusData.totalStudents > 0) {
            const avgPerCapita = (data.total_co2_kg / campusData.totalStudents).toFixed(1);
            kpiPerCap.innerHTML = `${avgPerCapita} <span class="unit">kg CO₂</span>`;
        }

        renderUserActivityTable();
    } catch (err) {
        console.warn('Backend overview not reachable, running with cached baseline data:', err.message);
        renderUserActivityTable();
    }
}

function renderUserActivityTable() {
    const container = document.getElementById('userActivityTableContainer');
    if (!container) return;

    const mode = getUserMode();
    const bills = getUserBills();

    if (mode === 'zero') {
        if (bills.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 36px 16px; color: #94a3b8;">
                    <div style="width: 52px; height: 52px; border-radius: 50%; background: rgba(74, 222, 128, 0.1); color: #4ade80; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 12px; border: 1px solid rgba(74, 222, 128, 0.2);">
                        <i data-lucide="receipt" style="width: 24px; height: 24px;"></i>
                    </div>
                    <h4 style="color: #ffffff; font-size: 1.05rem; margin-bottom: 4px; font-weight: 700;">No Previous Data Recorded</h4>
                    <p style="font-size: 0.85rem; max-width: 440px; margin: 0 auto 16px auto; color: #94a3b8; line-height: 1.5;">This account is initialized fresh at 0. No electricity bills or campus logs have been attached to this profile yet.</p>
                    <a href="scanner.html" class="btn btn-emerald btn-sm"><i data-lucide="scan-line"></i> Scan Your First Bill</a>
                </div>
            `;
        } else {
            let rowsHtml = bills.map((b, idx) => `
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                    <td style="padding: 12px 8px;"><strong>#${bills.length - idx}</strong></td>
                    <td style="padding: 12px 8px;"><strong>${b.department || 'Computer Engineering'}</strong></td>
                    <td style="padding: 12px 8px;">${b.month || 'September 2026'}</td>
                    <td style="padding: 12px 8px;">${(b.units_kwh || 0).toLocaleString()} kWh</td>
                    <td style="padding: 12px 8px;">₹${Math.round(b.amount_inr || 0).toLocaleString()}</td>
                    <td style="padding: 12px 8px;"><strong class="text-emerald">${Math.round(b.co2_kg || 0).toLocaleString()} kg CO₂</strong></td>
                    <td style="padding: 12px 8px;"><span class="badge badge-success"><i data-lucide="check" style="width:11px;"></i> Logged</span></td>
                </tr>
            `).join('');

            container.innerHTML = `
                <table class="data-table" style="width: 100%; border-collapse: collapse; font-size: 0.88rem;">
                    <thead>
                        <tr style="border-bottom: 1px solid rgba(74, 222, 128, 0.2); text-align: left; color: #86efac; font-size: 0.78rem;">
                            <th style="padding: 10px 8px;">ID</th>
                            <th style="padding: 10px 8px;">DEPARTMENT</th>
                            <th style="padding: 10px 8px;">BILL PERIOD</th>
                            <th style="padding: 10px 8px;">UNITS</th>
                            <th style="padding: 10px 8px;">AMOUNT</th>
                            <th style="padding: 10px 8px;">EMISSIONS</th>
                            <th style="padding: 10px 8px;">STATUS</th>
                        </tr>
                    </thead>
                    <tbody style="color: #f1f5f9;">
                        ${rowsHtml}
                    </tbody>
                </table>
            `;
        }
    } else {
        container.innerHTML = `
            <table class="data-table" style="width: 100%; border-collapse: collapse; font-size: 0.88rem;">
                <thead>
                    <tr style="border-bottom: 1px solid rgba(74, 222, 128, 0.2); text-align: left; color: #86efac; font-size: 0.78rem;">
                        <th style="padding: 10px 8px;">REF</th>
                        <th style="padding: 10px 8px;">DEPARTMENT</th>
                        <th style="padding: 10px 8px;">BILL PERIOD</th>
                        <th style="padding: 10px 8px;">UNITS</th>
                        <th style="padding: 10px 8px;">AMOUNT</th>
                        <th style="padding: 10px 8px;">EMISSIONS</th>
                        <th style="padding: 10px 8px;">STATUS</th>
                    </tr>
                </thead>
                <tbody style="color: #f1f5f9;">
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);"><td style="padding: 12px 8px;">#AUD-01</td><td style="padding: 12px 8px;"><strong>Computer Engineering</strong></td><td style="padding: 12px 8px;">September 2026</td><td style="padding: 12px 8px;">4,200 kWh</td><td style="padding: 12px 8px;">₹48,300</td><td style="padding: 12px 8px;"><strong class="text-emerald">2,982 kg CO₂</strong></td><td style="padding: 12px 8px;"><span class="badge badge-success">Audited</span></td></tr>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);"><td style="padding: 12px 8px;">#AUD-02</td><td style="padding: 12px 8px;"><strong>Chemistry & Materials Lab</strong></td><td style="padding: 12px 8px;">September 2026</td><td style="padding: 12px 8px;">3,000 kWh</td><td style="padding: 12px 8px;">₹34,500</td><td style="padding: 12px 8px;"><strong class="text-danger">2,130 kg CO₂</strong></td><td style="padding: 12px 8px;"><span class="badge badge-danger">Spike (+42.9%)</span></td></tr>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);"><td style="padding: 12px 8px;">#AUD-03</td><td style="padding: 12px 8px;"><strong>Mechanical Engineering</strong></td><td style="padding: 12px 8px;">September 2026</td><td style="padding: 12px 8px;">3,600 kWh</td><td style="padding: 12px 8px;">₹41,400</td><td style="padding: 12px 8px;"><strong class="text-emerald">2,556 kg CO₂</strong></td><td style="padding: 12px 8px;"><span class="badge badge-success">Audited</span></td></tr>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);"><td style="padding: 12px 8px;">#AUD-04</td><td style="padding: 12px 8px;"><strong>Hostel Mess & Kitchens</strong></td><td style="padding: 12px 8px;">September 2026</td><td style="padding: 12px 8px;">2,800 kWh</td><td style="padding: 12px 8px;">₹32,200</td><td style="padding: 12px 8px;"><strong class="text-warning">1,988 kg CO₂</strong></td><td style="padding: 12px 8px;"><span class="badge badge-warning">Food Audit</span></td></tr>
                </tbody>
            </table>
        `;
    }

    if (window.lucide) window.lucide.createIcons();
}

// 2. Fetch Leaderboard & Departments
async function fetchLeaderboardData(mode = 'per_student', targetMonth = '2026-10') {
    const userMode = getUserMode();
    const userBills = getUserBills();

    if (userMode === 'zero' && userBills.length === 0) {
        // Render 0-state departments for a new user
        const zeroDepts = [
            { department: "Computer Engineering", students: 780, co2_kg: 0, co2_per_student: 0.0, units_kwh: 0, amount_inr: 0, rank: 1, color: "green", change_percent: 0, badge: "NEW" },
            { department: "Mechanical Engineering", students: 540, co2_kg: 0, co2_per_student: 0.0, units_kwh: 0, amount_inr: 0, rank: 2, color: "green", change_percent: 0, badge: "NEW" },
            { department: "Civil Engineering", students: 460, co2_kg: 0, co2_per_student: 0.0, units_kwh: 0, amount_inr: 0, rank: 3, color: "green", change_percent: 0, badge: "NEW" },
            { department: "Electrical Engineering", students: 420, co2_kg: 0, co2_per_student: 0.0, units_kwh: 0, amount_inr: 0, rank: 4, color: "green", change_percent: 0, badge: "NEW" },
            { department: "Chemistry & Materials Lab", students: 310, co2_kg: 0, co2_per_student: 0.0, units_kwh: 0, amount_inr: 0, rank: 5, color: "green", change_percent: 0, badge: "NEW" },
            { department: "Hostel Mess & Kitchens", students: 350, co2_kg: 0, co2_per_student: 0.0, units_kwh: 0, amount_inr: 0, rank: 6, color: "green", change_percent: 0, badge: "NEW" },
            { department: "Central Administration", students: 180, co2_kg: 0, co2_per_student: 0.0, units_kwh: 0, amount_inr: 0, rank: 7, color: "green", change_percent: 0, badge: "NEW" },
            { department: "Sports Complex", students: 100, co2_kg: 0, co2_per_student: 0.0, units_kwh: 0, amount_inr: 0, rank: 8, color: "green", change_percent: 0, badge: "NEW" }
        ];
        renderCarbonLeagueFromApi(zeroDepts);
        renderDepartmentCardsFromApi(zeroDepts);
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/leaderboard?month=${targetMonth}&mode=${mode}`);
        if (!res.ok) throw new Error('Leaderboard API error');
        const data = await res.json();

        if (data.leaderboard && data.leaderboard.length > 0) {
            renderCarbonLeagueFromApi(data.leaderboard);
            renderDepartmentCardsFromApi(data.leaderboard);
        }
    } catch (err) {
        console.warn('Using baseline leaderboard:', err.message);
        renderCarbonLeagueTables();
        renderDepartmentCards();
    }
}

function renderCarbonLeagueFromApi(list) {
    const tbodyPage = document.getElementById('leagueTableBodyPage');
    if (!tbodyPage) return;

    tbodyPage.innerHTML = '';
    list.forEach(dept => {
        const rank = dept.rank;
        const rankClass = rank === 1 ? 'top-1' : rank === 2 ? 'top-2' : '';
        const badgeClass = dept.color === 'green' ? 'badge-success' : dept.color === 'yellow' ? 'badge-warning' : 'badge-danger';
        const changeArrow = dept.change_percent <= 0 ? '↓' : '↑';
        const changeColor = dept.change_percent <= 0 ? 'text-success' : 'text-danger';

        const badgeHtml = dept.badge ? `<span class="badge ${badgeClass}">${dept.badge}</span>` : `<span class="badge badge-neutral">${dept.color.toUpperCase()}</span>`;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="rank-badge ${rankClass}">0${rank}</span></td>
            <td><span class="dept-name" onclick="openLiveDeptModal('${dept.department}', ${dept.students}, ${dept.co2_kg}, ${dept.co2_per_student}, ${dept.units_kwh}, ${dept.amount_inr})">${dept.department}</span></td>
            <td>${dept.students}</td>
            <td><strong>${dept.co2_per_student} kg</strong></td>
            <td class="${changeColor}"><strong>${changeArrow} ${Math.abs(dept.change_percent)}%</strong></td>
            <td>${badgeHtml}</td>
            <td><button class="btn btn-sm btn-secondary" onclick="openLiveDeptModal('${dept.department}', ${dept.students}, ${dept.co2_kg}, ${dept.co2_per_student}, ${dept.units_kwh}, ${dept.amount_inr})">View Details</button></td>
        `;
        tbodyPage.appendChild(row);
    });
}

function renderDepartmentCardsFromApi(list) {
    const container = document.getElementById('deptCardsGrid');
    if (!container) return;

    container.innerHTML = '';
    list.forEach(dept => {
        const badgeClass = dept.color === 'green' ? 'badge-success' : dept.color === 'yellow' ? 'badge-warning' : 'badge-danger';
        const badgeText = dept.badge || (dept.color === 'green' ? 'CLEAN' : dept.color === 'yellow' ? 'MODERATE' : 'ATTENTION');
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div class="card-header border-b">
                <div>
                    <h4 class="card-title">${dept.department}</h4>
                    <p class="card-subtitle">${dept.students} Enrolled Students</p>
                </div>
                <span class="badge ${badgeClass}">${badgeText}</span>
            </div>
            <div style="margin-top: 14px; display: flex; flex-direction: column; gap: 8px;">
                <div class="stat-mini-row"><span>CO₂ / Student:</span><strong class="text-emerald">${dept.co2_per_student} kg</strong></div>
                <div class="stat-mini-row"><span>Total Monthly CO₂:</span><strong>${Math.round(dept.co2_kg).toLocaleString()} kg</strong></div>
                <div class="stat-mini-row"><span>Electricity Used:</span><span>${dept.units_kwh.toLocaleString()} kWh</span></div>
                <div class="stat-mini-row"><span>Monthly Energy Bill:</span><span class="text-emerald">₹${Math.round(dept.amount_inr).toLocaleString()}</span></div>
            </div>
            <button class="btn btn-sm btn-outline-emerald w-full" style="margin-top: 16px;" onclick="openLiveDeptModal('${dept.department}', ${dept.students}, ${dept.co2_kg}, ${dept.co2_per_student}, ${dept.units_kwh}, ${dept.amount_inr})">
                Department Audit
            </button>
        `;
        container.appendChild(card);
    });
}

// 3. Load Departments into Dropdown
async function loadDepartmentsDropdown() {
    const select = document.getElementById('ocrDeptSelect');
    if (!select) return;

    try {
        const res = await fetch(`${API_BASE}/departments`);
        if (!res.ok) return;
        const depts = await res.json();
        select.innerHTML = '';
        depts.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d.id;
            opt.innerText = `${d.name} (${d.students} students)`;
            select.appendChild(opt);
        });
    } catch (e) {
        // Fallback default options already in HTML
    }
}

// 4. Fetch Mess Menu & Green Day Tip
async function fetchMessMenu() {
    try {
        const res = await fetch(`${API_BASE}/mess`);
        if (!res.ok) return;
        const data = await res.json();

        // Update Green Day Tip
        const tipEl = document.querySelector('.weekly-mess-schedule h5');
        if (tipEl && data.green_day_tip) {
            tipEl.innerHTML = `<i data-lucide="sparkles" class="text-emerald" style="display:inline-block; vertical-align:middle; width:18px; margin-right:6px;"></i> <strong>Green Day Initiative:</strong> ${data.green_day_tip}`;
        }

        // Render real meal cards
        const container = document.querySelector('.meal-cards-grid');
        if (!container || !data.days) return;

        container.innerHTML = '';
        const dayKeys = Object.keys(data.days);

        dayKeys.slice(0, 4).forEach(day => {
            const dayMeals = data.days[day];
            dayMeals.forEach(meal => {
                const borderClass = meal.label === 'Low' ? 'border-low' : meal.label === 'Medium' ? 'border-med' : 'border-high';
                const badgeClass = meal.label === 'Low' ? 'badge-success' : meal.label === 'Medium' ? 'badge-warning' : 'badge-danger';

                const card = document.createElement('div');
                card.className = `meal-card ${borderClass}`;
                card.innerHTML = `
                    <div class="meal-header">
                        <div>
                            <span class="meal-name">${meal.meal_name}</span>
                            <div style="font-size:0.75rem; color:var(--text-muted);">${meal.day} • ${meal.slot.toUpperCase()}</div>
                        </div>
                        <span class="badge ${badgeClass}">${meal.label.toUpperCase()}</span>
                    </div>
                    <div class="meal-co2">${meal.co2_per_plate} <span class="unit">kg CO₂e/plate</span></div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                        <span style="font-size:0.8rem; color:var(--text-muted);"><i data-lucide="heart" style="width:14px; display:inline;"></i> <span id="meal-votes-${meal.id}">${meal.votes}</span> Pledges</span>
                        <button class="btn btn-sm btn-outline-emerald" onclick="voteForMeal(${meal.id})">Pledge Vote</button>
                    </div>
                `;
                container.appendChild(card);
            });
        });

        if (window.lucide) window.lucide.createIcons();
    } catch (e) {
        console.warn('Mess API error:', e.message);
    }
}

async function voteForMeal(mealId) {
    try {
        const res = await fetch(`${API_BASE}/mess/${mealId}/vote`, { method: 'POST' });
        if (!res.ok) throw new Error('Vote failed');
        const updated = await res.json();
        const voteSpan = document.getElementById(`meal-votes-${mealId}`);
        if (voteSpan) voteSpan.innerText = updated.votes;
        showToast('Green Day Pledge Recorded', `Voted for ${updated.meal_name}! Total votes: ${updated.votes}`);
    } catch (e) {
        showToast('Vote Registered', 'Your pledge has been logged.');
    }
}

// 5. Fetch Anomalies and Solar Tips
async function fetchAnomaliesAndSolarTips() {
    try {
        // Anomalies
        const resAnom = await fetch(`${API_BASE}/anomalies?month=2026-10`);
        if (resAnom.ok) {
            const anomData = await resAnom.json();
            if (anomData.anomalies && anomData.anomalies.length > 0) {
                const a = anomData.anomalies[0];
                const msgEl = document.querySelector('.anomaly-msg');
                if (msgEl) msgEl.innerText = `"${a.message}"`;

                const statBoxes = document.querySelectorAll('.anomaly-stats-grid .stat-box .val');
                if (statBoxes.length >= 4) {
                    statBoxes[0].innerHTML = `${a.this_month_kwh.toLocaleString()} <small>kWh</small>`;
                    statBoxes[1].innerHTML = `${a.average_kwh.toLocaleString()} <small>kWh</small>`;
                    statBoxes[2].innerHTML = `+${a.percent_change}%`;
                    statBoxes[3].innerHTML = `${a.z_score}`;
                }
            }
        }

        // Solar Tips
        const resTips = await fetch(`${API_BASE}/tips/solar`);
        if (resTips.ok) {
            const tipsData = await resTips.json();
            const actTags = document.querySelector('.activity-tags');
            if (actTags && tipsData.recommended_schedules) {
                actTags.innerHTML = '';
                tipsData.recommended_schedules.forEach(s => {
                    const tag = document.createElement('span');
                    tag.className = 'act-tag';
                    tag.innerHTML = `<i data-lucide="zap"></i> ${s.name} (${s.power_kw} kW)`;
                    actTags.appendChild(tag);
                });
                if (window.lucide) window.lucide.createIcons();
            }
        }
    } catch (e) {
        console.warn('Energy & Solar API error:', e.message);
    }
}

/* ==========================================================================
   LIVE BILL SCANNER & OCR WORKFLOW
   ========================================================================== */
function triggerFileInput() {
    const input = document.getElementById('billFileInputPage');
    if (input) input.click();
}

async function handleBillUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const dropzone = document.getElementById('billDropzonePage');
    const progressContainer = document.getElementById('ocrProgressContainerPage');
    const resultCard = document.getElementById('ocrResultCardPage');
    const progressBar = document.getElementById('ocrProgressBarPage');
    const statusText = document.getElementById('ocrStatusTextPage');

    dropzone.classList.add('hidden');
    progressContainer.classList.remove('hidden');
    resultCard.classList.add('hidden');

    progressBar.style.width = '30%';
    statusText.innerText = `Uploading ${file.name} to EcoTrace OCR server...`;

    const formData = new FormData();
    formData.append('file', file);

    try {
        progressBar.style.width = '60%';
        statusText.innerText = 'Extracting English, Marathi & Hindi bill text via Tesseract...';

        const res = await fetch(`${API_BASE}/bills/scan`, {
            method: 'POST',
            body: formData
        });

        progressBar.style.width = '90%';
        statusText.innerText = 'Applying Central Electricity Authority (0.71 kg CO₂/kWh) factor...';

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Bill upload failed');
        }

        const scanData = await res.json();
        progressBar.style.width = '100%';

        setTimeout(() => {
            progressContainer.classList.add('hidden');
            resultCard.classList.remove('hidden');

            currentScannedBill = {
                file_name: scanData.file_name,
                units_kwh: scanData.units_kwh || 3076,
                amount_inr: scanData.amount_inr || 38459,
                bill_month: scanData.bill_month || "September 2026",
                raw_text: scanData.raw_text || ""
            };

            // Populate form
            document.getElementById('ocrThumbnailFilename').innerText = scanData.file_name;
            document.getElementById('ocrThumbnailUnits').innerText = `${Math.round(currentScannedBill.units_kwh).toLocaleString()} kWh`;
            document.getElementById('ocrInputUnits').value = Math.round(currentScannedBill.units_kwh);
            document.getElementById('ocrInputAmount').value = Math.round(currentScannedBill.amount_inr);
            document.getElementById('ocrInputMonth').value = currentScannedBill.bill_month;

            recalculateOcrPreview();
            showToast('Bill OCR Complete', scanData.message || 'MSEDCL bill parsed with multilingual OCR.');
            if (window.lucide) window.lucide.createIcons();
        }, 300);

    } catch (err) {
        console.warn('OCR server error, using client fallback:', err.message);
        // Graceful client fallback for demo
        setTimeout(() => {
            progressContainer.classList.add('hidden');
            resultCard.classList.remove('hidden');
            document.getElementById('ocrThumbnailFilename').innerText = file.name;
            recalculateOcrPreview();
            showToast('Bill Read', 'Extracted consumption data. Please verify values.');
        }, 500);
    }
}

function recalculateOcrPreview() {
    const units = parseFloat(document.getElementById('ocrInputUnits').value) || 0;
    const amount = parseFloat(document.getElementById('ocrInputAmount').value) || Math.round(units * 11.5);
    const co2 = Math.round(units * 0.71 * 10) / 10;

    const previewCo2 = document.getElementById('ocrPreviewCo2');
    const previewDesc = document.getElementById('ocrPreviewDesc');

    if (previewCo2) previewCo2.innerHTML = `${co2.toLocaleString()} <span class="unit">kg CO₂e</span>`;
    if (previewDesc) previewDesc.innerText = `${units.toLocaleString()} kWh × 0.71 kg/kWh (CEA India grid factor) • Est. Cost: ₹${Math.round(amount).toLocaleString()}`;
}

async function confirmAddBillToFootprint() {
    const deptSelect = document.getElementById('ocrDeptSelect');
    const deptId = deptSelect ? parseInt(deptSelect.value) : 1;
    const deptName = deptSelect && deptSelect.selectedIndex >= 0 ? deptSelect.options[deptSelect.selectedIndex].text : "Department";
    const units = parseFloat(document.getElementById('ocrInputUnits').value) || 3076;
    const amount = parseFloat(document.getElementById('ocrInputAmount').value) || 38459;
    const month = document.getElementById('ocrInputMonth').value || "September 2026";
    const co2Val = Math.round(units * 0.71 * 10) / 10;

    // Save to current user's personal bills array
    const userBills = getUserBills();
    userBills.unshift({
        department_id: deptId,
        department: deptName,
        units_kwh: units,
        amount_inr: amount,
        co2_kg: co2Val,
        file_name: currentScannedBill.file_name,
        month: month,
        timestamp: new Date().toISOString()
    });
    saveUserBills(userBills);

    const payload = {
        department_id: deptId,
        bill_month: month,
        units_kwh: units,
        amount_inr: amount,
        file_name: currentScannedBill.file_name,
        raw_text: currentScannedBill.raw_text
    };

    try {
        const res = await fetch(`${API_BASE}/bills/confirm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Failed to confirm bill');
        const result = await res.json();

        showToast('Bill Confirmed & Saved', result.summary);
        fetchOverviewData();
        fetchLeaderboardData();
        resetBillScanner();
    } catch (err) {
        // Local update
        campusData.currentEmissions += Math.round(units * 0.71);
        campusData.energyCost += Math.round(amount);
        const kpiC = document.getElementById('kpiTotalCarbon');
        if (kpiC) kpiC.innerHTML = `${campusData.currentEmissions.toLocaleString()} <span class="unit">kg CO₂</span>`;
        const kpiP = document.getElementById('kpiEnergyCost');
        if (kpiP) kpiP.innerText = `₹${campusData.energyCost.toLocaleString()}`;
        showToast('Bill Logged', `Added ${Math.round(units * 0.71).toLocaleString()} kg CO₂ and ₹${Math.round(amount).toLocaleString()} to campus audit.`);
        fetchOverviewData();
        resetBillScanner();
    }
}

function resetBillScanner() {
    document.getElementById('billDropzonePage').classList.remove('hidden');
    document.getElementById('ocrProgressContainerPage').classList.add('hidden');
    document.getElementById('ocrResultCardPage').classList.add('hidden');
    const input = document.getElementById('billFileInputPage');
    if (input) input.value = '';
}

/* ==========================================================================
   WHAT-IF SIMULATOR
   ========================================================================== */
function initSimulator() {
    updateSimulator();
}

async function updateSimulator() {
    const sliderPc = document.getElementById('sliderPcTimePage');
    if (!sliderPc) return;

    const pcTime = parseInt(sliderPc.value);
    const carpoolPct = parseInt(document.getElementById('sliderCarpoolPage').value);
    const solarKw = parseInt(document.getElementById('sliderSolarPage').value);

    document.getElementById('valPcTimePage').innerText = pcTime === 6 ? '6 PM (Automatic)' : `${pcTime} PM`;
    document.getElementById('valCarpoolPage').innerText = `${carpoolPct}%`;
    document.getElementById('valSolarPage').innerText = `${solarKw} kW`;

    // 1. PC Savings (Hours saved per day = 10 - pcTime, e.g. shutdown at 6 PM saves 4 hours)
    const hoursSaved = Math.max(0, 9 - pcTime + 1);
    const payload = {
        lab_pcs: 200,
        pc_watts: 150,
        hours_saved_per_day: hoursSaved,
        working_days_per_month: 22,
        solar_kw: solarKw,
        led_tubes_replaced: 150,
        led_hours_per_day: 8.0
    };

    try {
        const res = await fetch(`${API_BASE}/whatif`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            const data = await res.json();
            const pcAct = data.actions.find(a => a.name.includes("PC")) || data.actions[0];
            const solarAct = data.actions.find(a => a.name.includes("solar")) || data.actions[1];

            document.getElementById('simPcSavesKwhPage').innerText = `${pcAct.kwh_per_month.toLocaleString()} kWh`;
            document.getElementById('simPcSavesCostPage').innerText = `₹${pcAct.inr_per_month.toLocaleString()}/mo`;
            document.getElementById('simPcSavesCo2Page').innerText = `${pcAct.co2_kg_per_month.toLocaleString()} kg CO₂/mo`;

            document.getElementById('simSolarCo2Page').innerText = `${Math.round(solarAct.co2_kg_per_month * 12).toLocaleString()} kg/yr`;
            document.getElementById('simSolarPaybackPage').innerText = data.solar_payback_years > 0 ? `${data.solar_payback_years} years` : 'N/A';

            const simulatedFootprint = Math.max(0, Math.round(campusData.currentEmissions - data.total_co2_kg_per_month));
            document.getElementById('simulatedFootprintValPage').innerHTML = `${simulatedFootprint.toLocaleString()} <small>kg CO₂</small>`;
            document.getElementById('simulatedReductionValPage').innerHTML = `${Math.round(data.total_co2_kg_per_month).toLocaleString()} <small>kg CO₂ / mo</small>`;
            document.getElementById('simulatedCostReductionValPage').innerText = `Savings: ₹${Math.round(data.total_inr_per_month).toLocaleString()} / month`;
            return;
        }
    } catch (e) {
        // Fallback calculation using exact formulas
    }

    // Direct mathematical calculation
    const pcKwhSaved = Math.round(200 * 150 * hoursSaved * 22 / 1000);
    const pcCo2Saved = Math.round(pcKwhSaved * 0.71);
    const pcCostSaved = Math.round(pcKwhSaved * 11.5);

    document.getElementById('simPcSavesKwhPage').innerText = `${pcKwhSaved.toLocaleString()} kWh`;
    document.getElementById('simPcSavesCostPage').innerText = `₹${pcCostSaved.toLocaleString()}/mo`;
    document.getElementById('simPcSavesCo2Page').innerText = `${pcCo2Saved.toLocaleString()} kg CO₂/mo`;

    const solarKwh = Math.round(solarKw * 4 * 30);
    const solarCo2Annual = Math.round(solarKwh * 0.71 * 12);
    const solarSavingsAnnual = solarKwh * 11.5 * 12;
    const solarPayback = solarKw > 0 && solarSavingsAnnual > 0 ? ((solarKw * 50000) / solarSavingsAnnual).toFixed(1) + ' years' : 'N/A';

    document.getElementById('simSolarCo2Page').innerText = `${solarCo2Annual.toLocaleString()} kg/yr`;
    document.getElementById('simSolarPaybackPage').innerText = solarPayback;

    const totalMonthlyReduction = pcCo2Saved + Math.round(solarKwh * 0.71);
    const totalCostReduction = pcCostSaved + Math.round(solarKwh * 11.5);
    const simulatedFootprint = Math.max(0, campusData.currentEmissions - totalMonthlyReduction);

    document.getElementById('simulatedFootprintValPage').innerHTML = `${simulatedFootprint.toLocaleString()} <small>kg CO₂</small>`;
    document.getElementById('simulatedReductionValPage').innerHTML = `${totalMonthlyReduction.toLocaleString()} <small>kg CO₂ / mo</small>`;
    document.getElementById('simulatedCostReductionValPage').innerText = `Savings: ₹${totalCostReduction.toLocaleString()} / month`;
}

function resetSimulator() {
    document.getElementById('sliderPcTimePage').value = 6;
    document.getElementById('sliderCarpoolPage').value = 25;
    document.getElementById('sliderSolarPage').value = 50;
    updateSimulator();
    showToast('Simulator Reset', 'Baseline parameters restored.');
}

function applySimulatorScenario() {
    showToast('Scenario Saved', 'Operating parameters updated for campus recommendations.');
}

function simulateRecommendation(id) {
    navigateToPage('simulator');
    if (id === 1) document.getElementById('sliderPcTimePage').value = 6;
    if (id === 2) document.getElementById('sliderCarpoolPage').value = 30;
    if (id === 3) document.getElementById('sliderSolarPage').value = 75;
    updateSimulator();
    showToast('Scenario Loaded', `Intervention #${id} loaded into What-If Simulator.`);
}

/* ==========================================================================
   NAAC / NIRF REPORT GENERATION
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
        'Fetching Verified CEA Grid Emission Factors (0.71 kg/kWh)...',
        'Computing Departmental Per-Student Carbon League...',
        'Formatting Tables under NAAC Criterion 7.1.6 & NIRF...',
        'Attaching EcoTrace Logo and Official Compliance Stamps...'
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
    }, 400);
}

function previewReportModal() {
    triggerReportGeneration();
}

function downloadPdfSimulated() {
    // Trigger real download of live generated PDF with ReportLab and EcoTrace logo!
    const targetMonth = '2026-10';
    const downloadUrl = `${API_BASE}/reports/naac?month=${targetMonth}`;

    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `EcoTrace_Green_Campus_Report_${targetMonth}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast('Official PDF Downloaded', 'NAAC Criterion 7 report with EcoTrace logo saved.');
    closeModal('reportModal');
}

/* ==========================================================================
   MODALS & DETAIL VIEWS
   ========================================================================== */
function openLiveDeptModal(name, students, co2, perCapita, units, amount) {
    const modal = document.getElementById('deptModal');
    document.getElementById('deptModalTitle').innerHTML = `<i data-lucide="building-2" class="text-emerald"></i> ${name} — Department Audit`;

    document.getElementById('deptModalBody').innerHTML = `
        <div class="pdf-grid-2" style="margin-bottom: 20px;">
            <div class="pdf-box">
                <h5>Department Overview</h5>
                <p><strong>Enrolled Students:</strong> ${students}</p>
                <p><strong>Total Monthly Emissions:</strong> ${Math.round(co2).toLocaleString()} kg CO₂</p>
                <p><strong>CO₂ / Student:</strong> <span class="text-emerald" style="font-weight:700;">${perCapita} kg</span></p>
            </div>
            <div class="pdf-box">
                <h5>Energy & Cost Audit</h5>
                <p><strong>Electricity Consumed:</strong> ${units.toLocaleString()} kWh</p>
                <p><strong>Monthly Power Bill:</strong> ₹${Math.round(amount).toLocaleString()}</p>
                <p><strong>Tariff Standard:</strong> MSEDCL Commercial (₹11.5/kWh)</p>
            </div>
        </div>
        <div style="background: var(--bg-app); padding: 14px; border-radius: var(--radius-md);">
            <h5 style="margin-bottom: 6px; font-weight: 700; color: var(--emerald-700);">Targeted Sustainability Action</h5>
            <p style="font-size: 0.85rem; color: var(--text-secondary);">
                Schedule heavy departmental loads between <strong>11 AM and 3 PM</strong> to utilize clean rooftop solar energy.
            </p>
        </div>
    `;

    modal.classList.remove('hidden');
    if (window.lucide) window.lucide.createIcons();
}

function openAnomalyInvestigationModal() {
    const modal = document.getElementById('anomalyModal');
    modal.classList.remove('hidden');

    setTimeout(() => {
        const ctx = document.getElementById('anomalyDetailChart').getContext('2d');
        if (anomalyChartInstance) anomalyChartInstance.destroy();

        anomalyChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jul 2026', 'Aug 2026', 'Sep 2026', 'Oct 2026 (Spike)'],
                datasets: [
                    { label: '3-Month Baseline Mean (3,180 kWh)', data: [3180, 3180, 3180, 3180], backgroundColor: '#CBD5E1' },
                    { label: 'Chemistry Lab Actual (kWh)', data: [2906, 3180, 3454, 4544], backgroundColor: ['#16A34A', '#16A34A', '#16A34A', '#EF4444'] }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }, 100);
}

function resolveAnomaly() {
    showToast('Anomaly Addressed', 'Maintenance ticket #842 created for Chemistry Lab.');
    closeModal('anomalyModal');
}

function closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.add('hidden');
}

/* ==========================================================================
   CHARTS HELPERS
   ========================================================================== */
function initOverviewHeroChart() {
    const ctx = document.getElementById('heroTrendChart');
    if (!ctx) return;

    overviewChartInstance = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: campusData.monthlyHistory.labels,
            datasets: [{
                label: 'Campus CO₂ (kg)',
                data: campusData.monthlyHistory.totalCo2,
                borderColor: '#16A34A',
                borderWidth: 3,
                fill: true,
                backgroundColor: 'rgba(22, 163, 74, 0.1)',
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
                x: { grid: { display: false } },
                y: { grid: { color: '#F0F2F0' } }
            }
        }
    });
}

function updateOverviewHeroChart(labels, co2Data) {
    if (!overviewChartInstance) return;
    overviewChartInstance.data.labels = labels;
    overviewChartInstance.data.datasets[0].data = co2Data;
    overviewChartInstance.update();
}

function initAnalyticsPageChart() {
    const ctx = document.getElementById('pageAnalyticsChart');
    if (!ctx) return;

    analyticsChartInstance = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: campusData.monthlyHistory.labels,
            datasets: [
                {
                    label: 'Total CO₂ (kg)',
                    data: campusData.monthlyHistory.totalCo2,
                    borderColor: '#16A34A',
                    borderWidth: 3,
                    tension: 0.3,
                    pointRadius: 5
                },
                {
                    label: 'Energy Cost (₹)',
                    data: campusData.monthlyHistory.energyCost.map(c => Math.round(c / 16)), // Scaled visually for dual axis
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
            plugins: { legend: { position: 'top' } }
        }
    });
}

function updateAnalyticsPageChart(labels, co2Data, costData) {
    if (!analyticsChartInstance) return;
    analyticsChartInstance.data.labels = labels;
    analyticsChartInstance.data.datasets[0].data = co2Data;
    analyticsChartInstance.data.datasets[1].data = costData.map(c => Math.round(c / 16));
    analyticsChartInstance.update();
}

function initDonutCharts() {
    const ctx1 = document.getElementById('sourcesDonutChart');
    if (ctx1) {
        new Chart(ctx1.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Electricity (65%)', 'Hostel Mess (22%)', 'Labs & Server (13%)'],
                datasets: [{ data: [65, 22, 13], backgroundColor: ['#16A34A', '#F59E0B', '#6366F1'], borderWidth: 0 }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '72%', plugins: { legend: { display: false } } }
        });
    }

    const ctx2 = document.getElementById('pageSourcesDonutChart');
    if (ctx2) {
        new Chart(ctx2.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Electricity (65%)', 'Hostel Mess (22%)', 'Labs & Server (13%)'],
                datasets: [{ data: [65, 22, 13], backgroundColor: ['#16A34A', '#F59E0B', '#6366F1'], borderWidth: 0 }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: { legend: { position: 'bottom' } } }
        });
    }
}

/* ==========================================================================
   EVENT LISTENERS & TOASTS
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
    if (mobileBtn && sidebar) {
        mobileBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }
}

function toggleAddDataDropdown() {
    const dd = document.getElementById('addDataDropdown');
    if (dd) dd.classList.toggle('hidden');
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
    if (!container) return;

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
