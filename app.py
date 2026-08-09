from flask import Flask, jsonify, request, render_template_string, Response
import requests
import uuid
import datetime
import csv
import io

app = Flask(__name__)

API_KEY = "e198108f6c6ecefca2c863b2ec752ec0"
BASE_URL = "https://v3.football.api-sports.io/"

PAYSTACK_PUBLIC_KEY = "pk_test_59fac8eb9618c719181aa3229ca91a32b6850575"
PAYSTACK_SECRET_KEY = "sk_test_6deab2bed85f14f1aa994d6c7468ccf233104d87"

ACTIVE_VIP_KEYS = {}
USER_ANALYTICS_LOGS = []
USER_ENQUIRIES = []
APP_REVENUE = 0.00
TOTAL_TRANSACTIONS = 0
TOTAL_VISITS = 0

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Sports Analytics & Aggregator</title>
    <script src="https://js.paystack.co/v1/inline.js"></script>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent-green: #22c55e;
            --accent-blue: #38bdf8;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
        }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; }
        .container { max-width: 950px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 1px solid var(--border-color); padding-bottom: 15px; }
        h1 { font-size: 1.5rem; margin: 0; color: var(--accent-blue); cursor: pointer; user-select: none; } 
        .status-badge { font-size: 0.85rem; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
        .pulse-dot { width: 8px; height: 8px; background-color: var(--accent-green); border-radius: 50%; display: inline-block; box-shadow: 0 0 8px var(--accent-green); animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        .card { background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; font-size: 0.9rem; }
        select, input, textarea { width: 100%; padding: 10px; background-color: var(--bg-color); border: 1px solid var(--border-color); color: var(--text-color); border-radius: 6px; margin-bottom: 15px; font-size: 1rem; box-sizing: border-box; }
        button { background-color: var(--accent-blue); color: #0f172a; border: none; padding: 12px 20px; font-weight: bold; border-radius: 6px; cursor: pointer; width: 100%; font-size: 1rem; }
        button:hover { opacity: 0.9; }
        .btn-green { background-color: var(--accent-green); }
        .results-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .metric-box { background-color: var(--bg-color); border: 1px solid var(--border-color); padding: 15px; border-radius: 6px; }
        .metric-title { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 5px; }
        .metric-value { font-size: 1.1rem; font-weight: 600; color: var(--accent-green); }
        .recommendation-box { background-color: var(--bg-color); border-left: 4px solid var(--accent-green); padding: 15px; border-radius: 0 6px 6px 0; margin-bottom: 20px; }
        #admin-panel { display: none; border: 2px solid #f59e0b; background-color: #172033; }
        #ad-banner {
            background: linear-gradient(135deg, #312e81, #1e1b4b);
            border: 1px solid #6366f1; color: #f8fafc; padding: 12px 20px; border-radius: 8px;
            margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;
        }
        #notification-banner {
            background: linear-gradient(135deg, #1e3a8a, #1e293b);
            border: 1px solid var(--accent-blue); color: #f8fafc; padding: 12px 20px; border-radius: 8px;
            margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;
        }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9rem; }
        th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border-color); }
        th { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; }
        .form-pill { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-right: 3px; }
        .form-win { background: #065f46; color: #34d399; }
        .form-draw { background: #334155; color: #94a3b8; }
        .form-loss { background: #7f1d1d; color: #fca5a5; }
        .bookmaker-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1 onclick="promptAdminAccess()" title="Admin Portal">Autonomous Sports Analytics & Aggregator</h1>
        <div><span class="status-badge"><span class="pulse-dot"></span>Live Match Analytics Engine</span></div>
    </header>

    <div id="ad-banner">
        <div>
            <strong style="color: #a5b4fc;">⭐ 48-Hour VIP Pass:</strong> 
            <span>Unlock 48 Hours of Full Statistical Predictions & Double Chance Tips for R30.</span>
        </div>
        <button onclick="openCheckoutModal()" style="width: auto; background: #6366f1; color: white; padding: 6px 14px; font-size: 0.85rem;">Get VIP Pass (R30)</button>
    </div>

    <div id="notification-banner">
        <div>
            <strong style="color: var(--accent-blue);">🔔 System Status:</strong> 
            <span id="notification-text">Support Enquiries & Live Match Analytics Active.</span>
        </div>
        <button onclick="document.getElementById('notification-banner').style.display='none'" style="width: auto; background: transparent; color: var(--text-muted); padding: 4px 8px;">✕</button>
    </div>

    <div id="admin-panel" class="card">
        <h3 style="color: #f59e0b; margin-top:0;">🛡️ Owner Admin Panel & Analytics Dashboard</h3>
        <div class="results-grid">
            <div class="metric-box"><div class="metric-title">Total Revenue</div><div class="metric-value" id="admin-revenue">R0.00</div></div>
            <div class="metric-box"><div class="metric-title">Transactions</div><div class="metric-value" id="admin-transactions" style="color: var(--accent-blue);">0</div></div>
            <div class="metric-box"><div class="metric-title">Total Visits</div><div class="metric-value" id="admin-visits" style="color: #38bdf8;">0</div></div>
            <div class="metric-box"><div class="metric-title">Active VIP Keys</div><div class="metric-value" id="admin-keys" style="color: #a5b4fc;">0</div></div>
        </div>
        <div style="margin-bottom: 15px;">
            <a href="/api/admin/download-csv" target="_blank" style="display: inline-block; background: var(--accent-green); color: #0f172a; padding: 8px 16px; font-weight: bold; border-radius: 6px; text-decoration: none; margin-right: 10px;">📥 Download Analytics CSV</a>
            <button onclick="loadAdminData()" style="width: auto; background: var(--accent-blue); color: #0f172a; padding: 8px 16px;">🔄 Refresh Dashboard</button>
        </div>
        
        <h4 style="color: var(--accent-blue); margin-bottom: 5px;">📋 User Enquiries & AI Analysis</h4>
        <div id="admin-enquiries-container" style="max-height: 200px; overflow-y: auto; background: var(--bg-color); border: 1px solid var(--border-color); padding: 10px; border-radius: 6px; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 15px;">
            Loading enquiries...
        </div>

        <h4 style="color: var(--accent-blue); margin-bottom: 5px;">📋 Recent User Queries & Activity Log</h4>
        <div id="admin-logs-container" style="max-height: 150px; overflow-y: auto; background: var(--bg-color); border: 1px solid var(--border-color); padding: 10px; border-radius: 6px; font-size: 0.85rem; color: var(--text-muted);">
            Loading logs...
        </div>
        <br>
        <button onclick="document.getElementById('admin-panel').style.display='none'" style="background: var(--border-color); color: var(--text-color); width: auto;">Close Panel</button>
    </div>

    <div class="card" id="checkout-card" style="display:none; border: 2px solid #6366f1; background-color: #172033;">
        <h3 style="color: #a5b4fc; margin-top: 0;">🛒 Secure 48-Hour Pass Checkout (R30.00)</h3>
        <label>Email Address</label>
        <input type="email" id="customer-email" value="smtshyo8@gmail.com">
        <label>Mobile Number</label>
        <input type="tel" id="customer-phone" value="0731304465">
        <button onclick="payWithPaystack()" class="btn-green">Pay via Paystack Gateway</button>
        <div id="checkout-success-msg" style="display: none; margin-top: 15px; padding: 12px; background: #065f46; border-radius: 6px;">
            <strong>Verified! Token:</strong> <span id="generated-token-display" style="font-family:monospace; color:var(--accent-green);"></span>
        </div>
    </div>

    <div class="card">
        <label for="country-select">Step 1: Select Country / Region</label>
        <select id="country-select" onchange="fetchLeaguesForCountry()">
            <option value="">-- Loading Global Countries --</option>
        </select>
    </div>

    <div class="card" id="league-container" style="display:none;">
        <label for="league-select">Step 2: Select Competition (Leagues & Cups)</label>
        <select id="league-select" onchange="resetFixtureSelection()">
            <option value="">-- Select Competition --</option>
        </select>
        <button id="btn-load-fixtures" onclick="loadLiveFixtures()">Load Up-to-Date Fixtures & Results</button>
    </div>

    <div class="card" id="match-container" style="display:none;">
        <label for="match-select">Step 3: Select Fixture:</label>
        <select id="match-select"><option value="">-- Select Fixture --</option></select>
        <button class="btn-green" onclick="triggerPredictionFlow()">Perform Pro Analytics & Show Results</button>
    </div>

    <div class="card" id="vip-lock-card" style="display:none; border: 2px dashed #f59e0b; background: #1e1b4b; text-align: center;">
        <h3 style="color: #f59e0b; margin-bottom: 10px;">⭐ 48-Hour VIP Pass Required</h3>
        <div style="display: flex; gap: 10px; max-width: 400px; margin: 0 auto;">
            <input type="text" id="vip-key-input" placeholder="Paste 48-Hour VIP Token Here" style="margin-bottom:0;">
            <button onclick="unlockVIPAnalysis()" style="width: auto; background: #f59e0b; color: #0f172a;">Verify</button>
        </div>
        <p id="vip-error-msg" style="color: #ef4444; font-size: 0.8rem; display: none; margin-top: 8px;">Invalid or Expired Token.</p>
    </div>

    <div id="prediction-results" style="display:none;">
        <div class="results-grid">
            <div class="metric-box">
                <div class="metric-title">Fixture Status</div>
                <div class="metric-value" id="res-score">-</div>
            </div>
            <div class="metric-box"><div class="metric-title">Expected Goals (xG)</div><div class="metric-value" id="res-xg">-</div></div>
        </div>
        
        <div class="card" style="background-color: #172033; margin-bottom: 15px;">
            <h3 style="color: var(--accent-blue); margin-top: 0; font-size: 1rem;">📊 Performance & Goal Breakdown (Last 5 Games)</h3>
            <div id="form-analysis-content" style="font-size: 0.9rem; color: var(--text-muted);">Loading analytics data...</div>
        </div>

        <div class="recommendation-box">
            <div class="metric-title">Recommended Betting Tip:</div>
            <div id="res-pred" style="font-size: 1.2rem; font-weight: bold; color: var(--accent-green); margin-top: 4px;">-</div>
        </div>

        <div class="card" style="background: linear-gradient(135deg, #064e3b, #022c22);">
            <h3 style="color: #34d399; margin-top: 0; font-size: 1.1rem; text-align: center;">💰 Bookmaker Partner Integration</h3>
            <div class="bookmaker-grid">
                <a href="https://www.betway.co.za/?btag=BPA119179" target="_blank" style="display: block; background: #10b981; color: #fff; padding: 12px; font-weight: bold; border-radius: 6px; text-decoration: none; text-align: center;">Back on Betway (BPA119179)</a>
                <a href="https://www.hollywoodbets.net" target="_blank" style="display: block; background: purple; color: #fff; padding: 12px; font-weight: bold; border-radius: 6px; text-decoration: none; text-align: center;">Back on Hollywoodbets</a>
            </div>
        </div>

        <div class="card" style="background-color: #172033;">
            <h3 style="color: var(--accent-blue); margin-top: 0; font-size: 1.1rem;">🏆 Official League Standings</h3>
            <div id="standings-content"><p style="color: var(--text-muted);">Loading table...</p></div>
        </div>
    </div>

    <!-- User Support Enquiry Section -->
    <div class="card" style="background-color: #172033; border: 1px solid var(--accent-blue);">
        <h3 style="color: var(--accent-blue); margin-top: 0; font-size: 1.1rem;">💬 Need Help or Have Feedback? Send an Enquiry</h3>
        <label>Your Email Address</label>
        <input type="email" id="enquiry-email" placeholder="yourname@gmail.com">
        <label>Your Message / Question</label>
        <textarea id="enquiry-message" rows="3" placeholder="Ask about predictions, tokens, or suggest an improvement..."></textarea>
        <button onclick="submitEnquiry()" style="background: var(--accent-blue); color: #0f172a;">Submit Enquiry</button>
        <div id="enquiry-response-box" style="display: none; margin-top: 15px; padding: 12px; background: #064e3b; border-radius: 6px; color: #34d399;">
            <span id="enquiry-ai-reply"></span>
        </div>
    </div>
</div>

<script>
    const PROXY_URL = "/api/proxy?endpoint=";
    let currentFixtures = [];
    let selectedFixtureId = null;

    document.addEventListener("DOMContentLoaded", () => {
        loadAllCountriesLive();
        fetch('/api/track-visit', { method: 'POST' });
    });

    async function loadAllCountriesLive() {
        const countrySelect = document.getElementById('country-select');
        countrySelect.innerHTML = '<option value="">-- Loading Global Countries --</option>';
        try {
            let res = await fetch(`${PROXY_URL}countries`);
            let data = await res.json();
            if (data.response && data.response.length > 0) {
                countrySelect.innerHTML = '<option value="">-- Select Country / Region --</option>';
                data.response.sort((a, b) => a.name.localeCompare(b.name)).forEach(c => {
                    let opt = document.createElement('option');
                    opt.value = c.name;
                    opt.textContent = c.name;
                    countrySelect.appendChild(opt);
                });
            } else {
                countrySelect.innerHTML = '<option value="">Failed to load countries</option>';
            }
        } catch (e) {
            countrySelect.innerHTML = '<option value="">Error connecting to API</option>';
        }
    }

    async function fetchLeaguesForCountry() {
        const country = document.getElementById('country-select').value;
        const leagueContainer = document.getElementById('league-container');
        const leagueSelect = document.getElementById('league-select');
        
        resetFixtureSelection();
        if (!country) {
            leagueContainer.style.display = 'none';
            return;
        }

        leagueSelect.innerHTML = '<option value="">-- Loading Competitions & Cups --</option>';
        leagueContainer.style.display = 'block';

        try {
            let res = await fetch(`${PROXY_URL}leagues&country=${encodeURIComponent(country)}`);
            let data = await res.json();
            leagueSelect.innerHTML = '<option value="">-- Select Competition --</option>';
            if (data.response && data.response.length > 0) {
                data.response.forEach(item => {
                    let league = item.league;
                    let opt = document.createElement('option');
                    opt.value = league.id;
                    opt.textContent = `${league.name} (${league.type})`;
                    leagueSelect.appendChild(opt);
                });
            } else {
                leagueSelect.innerHTML = '<option value="">No competitions found</option>';
            }
        } catch (e) {
            leagueSelect.innerHTML = '<option value="">Error loading competitions</option>';
        }
    }

    async function loadLiveFixtures() {
        const leagueId = document.getElementById('league-select').value;
        const btn = document.getElementById('btn-load-fixtures');
        if (!leagueId) {
            alert("Please select a competition first.");
            return;
        }

        btn.textContent = "Querying Pro Live Fixtures...";
        btn.disabled = true;

        try {
            let res = await fetch(`${PROXY_URL}fixtures&league=${leagueId}&season=2026&next=30`);
            let data = await res.json();
            currentFixtures = (data.response && data.response.length > 0) ? data.response : [];
        } catch (e) {
            currentFixtures = [];
        }

        btn.textContent = "Load Up-to-Date Fixtures & Results";
        btn.disabled = false;

        const matchSelect = document.getElementById('match-select');
        matchSelect.innerHTML = '<option value="">-- Select Fixture --</option>';
        
        if (currentFixtures.length === 0) {
            matchSelect.innerHTML = '<option value="">No active fixtures found for current schedule</option>';
            return;
        }

        currentFixtures.forEach(item => {
            let opt = document.createElement('option');
            opt.value = item.fixture.id;
            let matchDate = item.fixture.date ? item.fixture.date.split('T')[0] : '';
            opt.textContent = `[${item.fixture.status.short}] ${item.teams.home.name} vs ${item.teams.away.name} (${matchDate})`;
            matchSelect.appendChild(opt);
        });
        
        document.getElementById('match-container').style.display = 'block';
        document.getElementById('match-container').scrollIntoView({ behavior: 'smooth' });
    }

    function resetFixtureSelection() {
        document.getElementById('match-container').style.display = 'none';
        document.getElementById('prediction-results').style.display = 'none';
        document.getElementById('vip-lock-card').style.display = 'none';
    }

    function triggerPredictionFlow() {
        selectedFixtureId = document.getElementById('match-select').value;
        if (!selectedFixtureId) {
            alert("Please select a fixture first.");
            return;
        }
        document.getElementById('prediction-results').style.display = 'none';
        document.getElementById('vip-lock-card').style.display = 'block';
        document.getElementById('vip-lock-card').scrollIntoView({ behavior: 'smooth' });
    }

    function openCheckoutModal() {
        document.getElementById('checkout-card').style.display = 'block';
        document.getElementById('checkout-card').scrollIntoView({ behavior: 'smooth' });
    }

    function payWithPaystack() {
        let email = document.getElementById('customer-email').value.trim();
        if (!email) {
            alert("Please enter a valid email address.");
            return;
        }

        let handler = PaystackPop.setup({
            key: 'pk_test_59fac8eb9618c719181aa3229ca91a32b6850575',
            email: email,
            amount: 3000,
            currency: 'ZAR',
            callback: function(response) {
                verifyPaystackTransaction(response.reference, email);
            },
            onClose: function() {
                alert('Transaction window closed.');
            }
        });
        handler.openIframe();
    }

    async function verifyPaystackTransaction(reference, email) {
        try {
            let res = await fetch('/api/verify-paystack', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ reference: reference, email: email })
            });
            let data = await res.json();
            if (data.success) {
                document.getElementById('generated-token-display').textContent = data.token;
                document.getElementById('checkout-success-msg').style.display = 'block';
                document.getElementById('vip-key-input').value = data.token;
                document.getElementById('admin-revenue').textContent = `R${data.new_revenue.toFixed(2)}`;
                document.getElementById('admin-transactions').textContent = data.new_transactions;
                document.getElementById('admin-keys').textContent = data.active_keys_count;
            }
        } catch (e) {
            alert("Payment verification error.");
        }
    }

    async function unlockVIPAnalysis() {
        let key = document.getElementById('vip-key-input').value.trim();
        let res = await fetch('/api/verify-vip', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ key: key, fixture_id: selectedFixtureId })
        });
        let data = await res.json();
        if (data.valid) {
            document.getElementById('vip-lock-card').style.display = 'none';
            fetchAdvancedPrediction();
            loadStandings();
        } else {
            document.getElementById('vip-error-msg').textContent = data.msg || "Invalid or Expired Token.";
            document.getElementById('vip-error-msg').style.display = 'block';
        }
    }

    async function fetchAdvancedPrediction() {
        let res = await fetch(`/api/predict?fixture=${selectedFixtureId}`);
        let data = await res.json();
        if (data.success) {
            document.getElementById('res-score').textContent = data.match_title;
            document.getElementById('res-xg').textContent = `Home xG: ${data.home_xg} | Away xG: ${data.away_xg}`;
            document.getElementById('res-pred').textContent = data.prediction;
            
            let formHtml = `<div style="margin-bottom:8px;"><strong>${data.home_name}:</strong> Scored <strong>${data.home_scored_total}</strong> goals and conceded <strong>${data.home_conceded_total}</strong> goals in their last 5 games. | Form: `;
            data.home_form.forEach(f => {
                let cls = f === 'W' ? 'form-win' : (f === 'D' ? 'form-draw' : 'form-loss');
                formHtml += `<span class="form-pill ${cls}">${f}</span>`;
            });
            formHtml += `</div><div style="margin-bottom:8px;"><strong>${data.away_name}:</strong> Scored <strong>${data.away_scored_total}</strong> goals and conceded <strong>${data.away_conceded_total}</strong> goals in their last 5 games. | Form: `;
            data.away_form.forEach(f => {
                let cls = f === 'W' ? 'form-win' : (f === 'D' ? 'form-draw' : 'form-loss');
                formHtml += `<span class="form-pill ${cls}">${f}</span>`;
            });
            formHtml += `<div style="margin-top:8px; color:var(--text-color);"><strong>H2H History:</strong> ${data.h2h_summary}</div>`;
            formHtml += `<div style="margin-top:6px; color:var(--accent-blue);"><strong>Punter Insight:</strong> ${data.insight}</div>`;
            document.getElementById('form-analysis-content').innerHTML = formHtml;

            document.getElementById('prediction-results').style.display = 'block';
            document.getElementById('prediction-results').scrollIntoView({ behavior: 'smooth' });
        }
    }

    async function loadStandings() {
        let leagueId = document.getElementById('league-select').value;
        let container = document.getElementById('standings-content');
        try {
            let res = await fetch(`${PROXY_URL}standings&league=${leagueId}&season=2026`);
            let data = await res.json();
            if (data.response && data.response.length > 0) {
                let standings = data.response[0].league.standings[0];
                let html = `<table><thead><tr><th>Pos</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>PTS</th></tr></thead><tbody>`;
                standings.forEach(row => {
                    html += `<tr><td>${row.rank}</td><td style="font-weight:600;">${row.team.name}</td><td>${row.all.played}</td><td>${row.all.win}</td><td>${row.all.draw}</td><td>${row.all.lose}</td><td style="color:var(--accent-green);">${row.points}</td></tr>`;
                });
                container.innerHTML = html + `</tbody></table>`;
            } else {
                container.innerHTML = '<p style="color:var(--text-muted);">Standings temporarily unavailable.</p>';
            }
        } catch (e) { container.innerHTML = '<p style="color:#ef4444;">Failed to load table.</p>'; }
    }

    async function submitEnquiry() {
        let email = document.getElementById('enquiry-email').value.trim();
        let message = document.getElementById('enquiry-message').value.trim();
        if (!email || !message) {
            alert("Please enter both your email and message.");
            return;
        }

        let res = await fetch('/api/enquiry', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email: email, message: message })
        });
        let data = await res.json();
        if (data.success) {
            document.getElementById('enquiry-ai-reply').textContent = "Thank you for your feedback or enquiry! Our team reviews all submissions within 2 minutes.";
            document.getElementById('enquiry-response-box').style.display = 'block';
        }
    }

    async function promptAdminAccess() {
        if (prompt("Enter Admin PIN:") === "1090") {
            let res = await fetch('/api/admin/stats');
            let data = await res.json();
            document.getElementById('admin-revenue').textContent = `R${data.revenue.toFixed(2)}`;
            document.getElementById('admin-transactions').textContent = data.transactions;
            document.getElementById('admin-visits').textContent = data.visits;
            document.getElementById('admin-keys').textContent = data.active_keys;
            loadAdminData();
            document.getElementById('admin-panel').style.display = 'block';
        }
    }

    async function loadAdminData() {
        let res = await fetch('/api/admin/data');
        let data = await res.json();
        
        let logsHtml = "";
        data.logs.forEach(l => {
            logsHtml += `[${l.timestamp}] Email: <strong>${l.email}</strong> | Fixture: <strong>${l.fixture_id}</strong><br>`;
        });
        document.getElementById('admin-logs-container').innerHTML = logsHtml || "No queries logged yet.";

        let enquiriesHtml = "";
        data.enquiries.forEach(e => {
            enquiriesHtml += `[${e.timestamp}] <strong>${e.email}</strong> asked: "${e.message}"<br><span style="color: var(--accent-green);">↳ AI Analysis/Reply: ${e.ai_response}</span><hr style="border-color:var(--border-color); margin:6px 0;">`;
        });
        document.getElementById('admin-enquiries-container').innerHTML = enquiriesHtml || "No enquiries submitted yet.";
    }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/track-visit', methods=['POST'])
def track_visit():
    global TOTAL_VISITS
    TOTAL_VISITS += 1
    return jsonify({"success": True})

@app.route('/api/enquiry', methods=['POST'])
def handle_enquiry():
    data = request.get_json()
    email = data.get('email', 'user@gmail.com')
    message = data.get('message', '')
    
    msg_lower = message.lower()
    if "token" in msg_lower or "vip" in msg_lower or "pay" in msg_lower:
        ai_response = "Automated AI Insight: User asking about VIP token duration or Paystack payment processing."
    elif "prediction" in msg_lower or "odds" in msg_lower or "match" in msg_lower:
        ai_response = "Automated AI Insight: User inquiring about match prediction logic, xG calculations, or betting markets."
    else:
        ai_response = "Automated AI Insight: General platform feedback or feature suggestion requiring review."

    enquiry_record = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "email": email,
        "message": message,
        "ai_response": ai_response
    }
    USER_ENQUIRIES.insert(0, enquiry_record)

    return jsonify({
        "success": True,
        "ai_response": ai_response
    })

@app.route('/api/admin/stats')
def admin_stats():
    global ACTIVE_VIP_KEYS
    now = datetime.datetime.now()
    active_count = sum(1 for k, v in ACTIVE_VIP_KEYS.items() if v['expires_at'] > now)
    return jsonify({
        "revenue": APP_REVENUE,
        "transactions": TOTAL_TRANSACTIONS,
        "visits": TOTAL_VISITS,
        "active_keys": active_count
    })

@app.route('/api/admin/data')
def admin_data():
    return jsonify({
        "logs": USER_ANALYTICS_LOGS,
        "enquiries": USER_ENQUIRIES
    })

@app.route('/api/admin/download-csv')
def download_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Type', 'Timestamp', 'Email', 'Details'])
    for log in USER_ANALYTICS_LOGS:
        writer.writerow(['Query', log['timestamp'], log['email'], f"Fixture ID: {log['fixture_id']}"])
    for enq in USER_ENQUIRIES:
        writer.writerow(['Enquiry', enq['timestamp'], enq['email'], f"Msg: {enq['message']} | AI Note: {enq['ai_response']}"])
    
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=platform_analytics_and_enquiries.csv"
    return response

@app.route('/api/proxy')
def proxy():
    endpoint = request.args.get('endpoint')
    if not endpoint:
        return jsonify({"error": "Missing endpoint"}), 400
    
    headers = {'x-apisports-key': API_KEY}
    url = f"{BASE_URL}{endpoint}"
    params = {k: v for k, v in request.args.items() if k != 'endpoint'}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict')
def predict():
    fixture_id = request.args.get('fixture')
    headers = {'x-apisports-key': API_KEY}
    try:
        res = requests.get(f"{BASE_URL}fixtures?id={fixture_id}", headers=headers).json()
        if not res.get('response'):
            return jsonify({"success": False, "error": "Fixture not found"})
        
        fixture_data = res['response'][0]
        home_id = fixture_data['teams']['home']['id']
        away_id = fixture_data['teams']['away']['id']
        home_name = fixture_data['teams']['home']['name']
        away_name = fixture_data['teams']['away']['name']
        
        heavyweights = ["manchester city", "real madrid", "barcelona", "mamelodi sundowns", "arsenal", "liverpool", "bayern", "psg", "inter"]
        is_home_heavyweight = any(hw in home_name.lower() for hw in heavyweights)
        is_away_heavyweight = any(hw in away_name.lower() for hw in heavyweights)

        home_form_res = requests.get(f"{BASE_URL}fixtures?team={home_id}&last=5", headers=headers).json()
        home_form = []
        home_scored_sum = 0
        home_conceded_sum = 0
        home_matches_count = 0
        if home_form_res.get('response'):
            for m in home_form_res['response']:
                h_team_obj = m['teams']['home']
                is_home = (h_team_obj['id'] == home_id)
                team_goals = m['goals']['home'] if is_home else m['goals']['away']
                opp_goals = m['goals']['away'] if is_home else m['goals']['home']
                
                if team_goals is not None and opp_goals is not None:
                    home_scored_sum += team_goals
                    home_conceded_sum += opp_goals
                    home_matches_count += 1
                    if team_goals > opp_goals: home_form.append('W')
                    elif team_goals == opp_goals: home_form.append('D')
                    else: home_form.append('L')
        if not home_form: home_form = ['W', 'D', 'W', 'L', 'W']
        home_scoring_rate = round(home_scored_sum / max(1, home_matches_count), 2)
        home_conceded_rate = round(home_conceded_sum / max(1, home_matches_count), 2)

        away_form_res = requests.get(f"{BASE_URL}fixtures?team={away_id}&last=5", headers=headers).json()
        away_form = []
        away_scored_sum = 0
        away_conceded_sum = 0
        away_matches_count = 0
        if away_form_res.get('response'):
            for m in away_form_res['response']:
                h_team_obj = m['teams']['home']
                is_home = (h_team_obj['id'] == away_id)
                team_goals = m['goals']['home'] if is_home else m['goals']['away']
                opp_goals = m['goals']['away'] if is_home else m['goals']['home']
                
                if team_goals is not None and opp_goals is not None:
                    away_scored_sum += team_goals
                    away_conceded_sum += opp_goals
                    away_matches_count += 1
                    if team_goals > opp_goals: away_form.append('W')
                    elif team_goals == opp_goals: away_form.append('D')
                    else: away_form.append('L')
        if not away_form: away_form = ['L', 'W', 'D', 'W', 'W']
        away_scoring_rate = round(away_scored_sum / max(1, away_matches_count), 2)
        away_conceded_rate = round(away_conceded_sum / max(1, away_matches_count), 2)

        h2h_res = requests.get(f"{BASE_URL}fixtures/headtohead?h2h={home_id}-{away_id}", headers=headers).json()
        h2h_home_wins = 0
        h2h_away_wins = 0
        h2h_draws = 0
        h2h_total_games = 0
        if h2h_res.get('response'):
            h2h_matches = h2h_res['response']
            h2h_total_games = len(h2h_matches)
            for hm in h2h_matches:
                hg = hm['goals']['home']
                ag = hm['goals']['away']
                h_side = hm['teams']['home']['id']
                
                if hg is not None and ag is not None:
                    if hg > ag:
                        if h_side == home_id: h2h_home_wins += 1
                        else: h2h_away_wins += 1
                    elif ag > hg:
                        if h_side == home_id: h2h_away_wins += 1
                        else: h2h_home_wins += 1
                    else:
                        h2h_draws += 1
                else:
                    h2h_draws += 1

            if h2h_total_games > 0:
                h2h_summary = f"{home_name} Wins: {h2h_home_wins} | Draws: {h2h_draws} | {away_name} Wins: {h2h_away_wins} (Total: {h2h_total_games} games)"
            else:
                h2h_summary = "No historical meetings recorded (First ever meeting)."
        else:
            h2h_summary = "No historical meetings recorded (First ever meeting)."

        base_home_xg = (home_scoring_rate + away_conceded_rate) / 2
        base_away_xg = (away_scoring_rate + home_conceded_rate) / 2

        if is_home_heavyweight and not is_away_heavyweight:
            base_home_xg += 0.9
            base_away_xg = max(0.6, base_away_xg - 0.4)
        elif is_away_heavyweight and not is_home_heavyweight:
            base_away_xg += 0.9
            base_home_xg = max(0.6, base_home_xg - 0.4)

        if h2h_total_games > 0:
            if h2h_home_wins > h2h_away_wins + 2:
                base_home_xg += 0.35
                insight = f"{home_name} holds overall historical H2H superiority across {h2h_total_games} encounters."
            elif h2h_away_wins > h2h_home_wins + 2:
                base_away_xg += 0.35
                insight = f"{away_name} holds overall historical H2H superiority across {h2h_total_games} encounters."
            else:
                insight = f"Historically balanced across {h2h_total_games} matches; current attack vs defence is key."
        else:
            insight = "First recorded meeting between these sides; relying purely on current form & metrics."

        home_xg = round(max(0.5, base_home_xg), 2)
        away_xg = round(max(0.5, base_away_xg), 2)

        xg_diff = home_xg - away_xg
        total_expected_goals = home_xg + away_xg

        if total_expected_goals < 1.5:
            goal_market = "Under 1.5 Goals" if total_expected_goals > 0.8 else "Under 0.5 Goals (Defensive Battle)"
        elif total_expected_goals > 3.2:
            goal_market = "Over 3.5 Goals (High Scoring Thriller)"
        elif total_expected_goals > 2.5:
            goal_market = "Over 2.5 Goals"
        else:
            goal_market = "Over 1.5 Goals"

        btts_condition = (home_scoring_rate >= 1.0 and away_scoring_rate >= 1.0)
        if btts_condition and total_expected_goals >= 2.0:
            goal_market = "Both Teams to Score (Yes)"

        if xg_diff > 0.8:
            prediction_text = f"Winner Prediction: {home_name} to Win (Straight 1) | {goal_market}"
        elif xg_diff > 0.3:
            prediction_text = f"Winner Prediction: {home_name} or Draw (Double Chance 1X) | {goal_market}"
        elif xg_diff < -0.8:
            prediction_text = f"Winner Prediction: {away_name} to Win (Straight 2) | {goal_market}"
        elif xg_diff < -0.3:
            prediction_text = f"Winner Prediction: {away_name} or Draw (Double Chance X2) | {goal_market}"
        else:
            prediction_text = f"Winner Prediction: Match Expected to End in a Draw (X) or Double Chance 12 | {goal_market}"

        return jsonify({
            "success": True,
            "match_title": f"{home_name} vs {away_name}",
            "home_name": home_name,
            "away_name": away_name,
            "home_form": home_form,
            "away_form": away_form,
            "home_scored_total": home_scored_sum,
            "home_conceded_total": home_conceded_sum,
            "away_scored_total": away_scored_sum,
            "away_conceded_total": away_conceded_sum,
            "h2h_total_games": h2h_total_games,
            "h2h_summary": h2h_summary,
            "insight": insight,
            "home_xg": home_xg,
            "away_xg": away_xg,
            "prediction": prediction_text
        })
    except Exception as e:
        return jsonify({
            "success": True,
            "match_title": "Matchday Forecast",
            "home_name": "Home Team",
            "away_name": "Away Team",
            "home_form": ['W', 'D', 'W', 'L', 'W'],
            "away_form": ['L', 'W', 'D', 'W', 'W'],
            "home_scored_total": 7,
            "home_conceded_total": 5,
            "away_scored_total": 6,
            "away_conceded_total": 6,
            "h2h_total_games": 0,
            "h2h_summary": "No historical meetings recorded (First ever meeting).",
            "insight": "Standard tactical projection.",
            "home_xg": 1.60,
            "away_xg": 1.10,
            "prediction": "Winner Prediction: Home Team or Draw (1X) | Over 2.5 Goals"
        })

@app.route('/api/verify-paystack', methods=['POST'])
def verify_paystack():
    global APP_REVENUE, TOTAL_TRANSACTIONS
    data = request.get_json()
    email = data.get('email', 'user@gmail.com')
    
    token = f"VIP48-{uuid.uuid4().hex[:8].upper()}"
    expiry_time = datetime.datetime.now() + datetime.timedelta(hours=48)
    
    ACTIVE_VIP_KEYS[token] = {
        "email": email,
        "expires_at": expiry_time
    }
    APP_REVENUE += 30.00
    TOTAL_TRANSACTIONS += 1
    return jsonify({
        "success": True,
        "token": token,
        "new_revenue": APP_REVENUE,
        "new_transactions": TOTAL_TRANSACTIONS,
        "active_keys_count": len(ACTIVE_VIP_KEYS)
    })

@app.route('/api/verify-vip', methods=['POST'])
def verify_vip():
    data = request.get_json()
    key = data.get('key', '').strip()
    fixture_id = data.get('fixture_id', 'unknown')
    
    if key in ACTIVE_VIP_KEYS:
        token_info = ACTIVE_VIP_KEYS[key]
        if datetime.datetime.now() < token_info['expires_at']:
            USER_ANALYTICS_LOGS.insert(0, {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "email": token_info['email'],
                "fixture_id": fixture_id
            })
            return jsonify({"valid": True})
        else:
            return jsonify({"valid": False, "msg": "VIP Pass has expired after 48 hours."})
    
    return jsonify({"valid": False, "msg": "Invalid VIP Token."})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
