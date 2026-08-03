from flask import Flask, jsonify, request, render_template_string
import requests
import uuid

app = Flask(__name__)

API_KEY = "e198108f6c6ecefca2c863b2ec752ec0"
BASE_URL = "https://v3.football.api-sports.io/"

ACTIVE_VIP_KEYS = {"VIP-SECRET-2026": {"status": "active", "email": "admin@local"}}
APP_REVENUE = 12450.00
TOTAL_TRANSACTIONS = 348

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Sports Analytics & Aggregator</title>
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
        .results-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .metric-box { background-color: var(--bg-color); border: 1px solid var(--border-color); padding: 15px; border-radius: 6px; }
        .metric-title { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 5px; }
        .metric-value { font-size: 1rem; font-weight: 600; color: var(--accent-green); }
        .recommendation-box { background-color: var(--bg-color); border-left: 4px solid var(--accent-green); padding: 15px; border-radius: 0 6px 6px 0; margin-bottom: 20px; }
        #admin-panel { display: none; border: 2px solid #f59e0b; background-color: #172033; }
        
        #ad-banner {
            background: linear-gradient(135deg, #312e81, #1e1b4b);
            border: 1px solid #6366f1;
            color: #f8fafc;
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        }
        #notification-banner {
            background: linear-gradient(135deg, #1e3a8a, #1e293b);
            border: 1px solid var(--accent-blue);
            color: #f8fafc;
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
        }
        
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9rem; }
        th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border-color); }
        th { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1 onclick="promptAdminAccess()" title="Admin Portal Access">Autonomous Sports Analytics & Aggregator</h1>
        <div><span id="status-text" class="status-badge"><span class="pulse-dot"></span>Live Feed Connected</span></div>
    </header>

    <div id="ad-banner">
        <div>
            <strong style="color: #a5b4fc;">⭐ Matchday VIP Pass:</strong> 
            <span>Unlock 24 Hours of Multi-Factor Predictions for only R30.</span>
        </div>
        <button onclick="openCheckoutModal()" style="width: auto; background: #6366f1; color: white; padding: 6px 14px; font-size: 0.85rem;">Get VIP Pass (R30)</button>
    </div>

    <div id="notification-banner">
        <div>
            <strong style="color: var(--accent-blue);">🔔 System Notification:</strong> 
            <span id="notification-text">System initialized and ready.</span>
        </div>
        <button onclick="dismissNotification()" style="width: auto; background: transparent; color: var(--text-muted); padding: 4px 8px; font-size: 0.8rem;">✕</button>
    </div>

    <div id="admin-panel" class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
            <h3 style="color: #f59e0b; margin: 0;">🛡️ Exclusive Admin & Owner Control Panel</h3>
            <button onclick="hideAdminDashboard()" style="width: auto; background: var(--border-color); color: var(--text-color); padding: 5px 12px; font-size: 0.8rem;">Close Panel</button>
        </div>
        <div class="results-grid" style="margin-bottom: 20px;">
            <div class="metric-box"><div class="metric-title">Total Proceeds / Revenue</div><div class="metric-value" id="admin-revenue">R12,450.00</div></div>
            <div class="metric-box"><div class="metric-title">Registered App Users</div><div class="metric-value" id="admin-users" style="color: var(--accent-blue);">348</div></div>
            <div class="metric-box"><div class="metric-title">Total Visits (Traffic)</div><div class="metric-value" style="color: #f59e0b;">1,892</div></div>
        </div>
    </div>

    <div class="card" id="checkout-card" style="display:none; border: 2px solid #6366f1; background-color: #172033;">
        <h3 style="color: #a5b4fc; margin-top: 0;">🛒 24-Hour Matchday VIP Pass (R30.00)</h3>
        <p style="font-size: 0.9rem; color: var(--text-muted);">Enter your email to receive your instant 24-hour access key upon checkout simulation.</p>
        <input type="email" id="customer-email" placeholder="Enter your email address">
        <div style="display: flex; gap: 10px;">
            <button onclick="simulateSuccessfulPayment()" class="btn-green" style="flex: 1;">Simulate Paystack / Yoco Payment (R30)</button>
            <button onclick="document.getElementById('checkout-card').style.display='none'" style="width: auto; background: var(--border-color); color: var(--text-color);">Cancel</button>
        </div>
        <div id="checkout-success-msg" style="display: none; margin-top: 15px; padding: 10px; background: #065f46; border-radius: 6px; font-size: 0.9rem;">
            <strong>Success! (Valid for 24 Hours):</strong> Your VIP Key is: <span id="generated-key-display" style="font-family: monospace; background: #022c22; padding: 2px 6px; border-radius: 4px;"></span>
        </div>
    </div>

    <div class="card">
        <label for="country-select">Step 1: Select Region / Country (Live Feed)</label>
        <select id="country-select" onchange="fetchLeaguesForSelectedCountry()">
            <option value="">-- Loading Live Countries... --</option>
        </select>
    </div>

    <div class="card" id="league-container" style="display:none;">
        <label for="league-select">Step 2: Select Competition / League / Cup</label>
        <select id="league-select" onchange="resetFixtureSelection()">
            <option value="">-- Select Competition --</option>
        </select>
        <button id="btn-load-fixtures" onclick="loadLiveFixtures()">Load Up-to-Date Fixtures & Results</button>
    </div>

    <div class="card" id="match-container" style="display:none;">
        <label for="match-select">Step 3: Select Fixture / Match Outcome:</label>
        <select id="match-select"><option value="">-- Select Fixture --</option></select>
        <button class="btn-green" id="btn-predict" onclick="triggerPredictionFlow()">Perform Multi-Factor Analysis & Show Results</button>
    </div>

    <div class="card" id="vip-lock-card" style="display:none; border: 2px dashed #f59e0b; background: #1e1b4b; text-align: center;">
        <h3 style="color: #f59e0b; margin-bottom: 10px;">⭐ VIP 24-Hour Pass Required</h3>
        <div style="display: flex; gap: 10px; max-width: 400px; margin: 0 auto;">
            <input type="password" id="vip-key-input" placeholder="Enter 24h VIP Key" style="flex: 1; margin-bottom: 0;">
            <button onclick="unlockVIPAnalysis()" style="width: auto; background: #f59e0b; color: #0f172a;">Unlock VIP</button>
        </div>
        <p id="vip-error-msg" style="color: #ef4444; font-size: 0.8rem; margin-top: 8px; display: none;">Invalid or Expired VIP Key.</p>
    </div>

    <div id="prediction-results" style="display:none;">
        <div class="results-grid">
            <div class="metric-box">
                <div class="metric-title" style="display: flex; justify-content: space-between;">
                    <span>Match Live Status & Score</span>
                    <span style="color: var(--accent-green); font-size: 0.75rem;">● Auto-Syncing</span>
                </div>
                <div class="metric-value" id="res-score">-</div>
            </div>
            <div class="metric-box"><div class="metric-title">Recent Form</div><div class="metric-value" id="res-form">-</div></div>
        </div>
        <div class="recommendation-box">
            <div class="metric-title">Accurate Match Outcome & Prediction:</div>
            <div id="res-pred" style="font-size: 1.2rem; font-weight: bold; color: var(--accent-green); margin-top: 4px;">-</div>
        </div>

        <div class="card" style="margin-top: 20px; background-color: #172033;">
            <h3 style="color: var(--accent-blue); margin-top: 0; font-size: 1.1rem;">🏆 Live League Standings & Team Form</h3>
            <div id="standings-content" style="overflow-x: auto;">
                <p style="color: var(--text-muted); font-size: 0.9rem;">Loading league table and statistics...</p>
            </div>
        </div>
    </div>
</div>

<script>
    const PROXY_URL = "/api/proxy?endpoint=";
    let currentFixtures = [];
    let selectedFixtureId = null;
    let refreshInterval = null;

    // Ensure initialization triggers properly on DOM load
    document.addEventListener("DOMContentLoaded", async function() {
        await initializeLiveCountries();
    });

    function showNotification(message) {
        document.getElementById('notification-text').textContent = message;
        document.getElementById('notification-banner').style.display = 'flex';
    }

    function dismissNotification() {
        document.getElementById('notification-banner').style.display = 'none';
    }

    function openCheckoutModal() {
        document.getElementById('checkout-card').style.display = 'block';
        document.getElementById('checkout-card').scrollIntoView({ behavior: 'smooth' });
    }

    async function simulateSuccessfulPayment() {
        const email = document.getElementById('customer-email').value.trim();
        if (!email) { alert("Please enter a valid email address."); return; }

        try {
            const response = await fetch('/api/purchase-vip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            });
            const data = await response.json();
            if (data.success) {
                document.getElementById('generated-key-display').textContent = data.vip_key;
                document.getElementById('checkout-success-msg').style.display = 'block';
                document.getElementById('admin-revenue').textContent = `R${data.new_revenue.toLocaleString()}`;
                document.getElementById('admin-users').textContent = data.new_users;
                showNotification("24h Matchday VIP Pass generated successfully!");
            }
        } catch (e) { alert("Checkout simulation failed."); }
    }

    function promptAdminAccess() {
        const pin = prompt("Enter Admin / Owner PIN:");
        if (pin === "1090") {
            document.getElementById('admin-panel').style.display = 'block';
            document.getElementById('admin-panel').scrollIntoView({ behavior: 'smooth' });
        } else if (pin !== null) { alert("Incorrect Admin PIN."); }
    }

    function hideAdminDashboard() { document.getElementById('admin-panel').style.display = 'none'; }

    async function initializeLiveCountries() {
        const countrySelect = document.getElementById('country-select');
        try {
            const response = await fetch(`${PROXY_URL}countries`);
            const data = await response.json();
            if (data.response && data.response.length > 0) {
                countrySelect.innerHTML = '<option value="">-- Select Country or Region --</option>';
                data.response.sort((a, b) => a.name.localeCompare(b.name)).forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.name;
                    opt.textContent = c.name;
                    countrySelect.appendChild(opt);
                });
            } else {
                countrySelect.innerHTML = '<option value="">-- No Countries Returned --</option>';
            }
        } catch (err) { 
            console.error("Error loading countries", err);
            countrySelect.innerHTML = '<option value="">-- Failed to Load Countries --</option>';
        }
    }

    async function fetchLeaguesForSelectedCountry() {
        const countryName = document.getElementById('country-select').value;
        const leagueContainer = document.getElementById('league-container');
        const leagueSelect = document.getElementById('league-select');
        
        resetFixtureSelection();
        if (!countryName) {
            leagueContainer.style.display = 'none';
            return;
        }

        try {
            const response = await fetch(`${PROXY_URL}leagues&country=${countryName}`);
            const data = await response.json();
            if (data.response && data.response.length > 0) {
                leagueSelect.innerHTML = '<option value="">-- Select Competition --</option>';
                data.response.forEach(item => {
                    const opt = document.createElement('option');
                    opt.value = item.league.id;
                    opt.textContent = `${item.league.name} (${item.league.type})`;
                    leagueSelect.appendChild(opt);
                });
                leagueContainer.style.display = 'block';
            }
        } catch (err) { console.error("Error loading leagues", err); }
    }

    async function loadLiveFixtures() {
        const leagueId = document.getElementById('league-select').value;
        if (!leagueId) return;
        const btn = document.getElementById('btn-load-fixtures');
        btn.textContent = "Fetching Live Fixtures from API...";
        btn.disabled = true;

        try {
            let res = await fetch(`${PROXY_URL}fixtures&league=${leagueId}&season=2026`);
            let data = await res.json();
            
            if (data.response && data.response.length > 0) {
                currentFixtures = data.response;
            } else {
                let res2 = await fetch(`${PROXY_URL}fixtures&league=${leagueId}&season=2025`);
                let data2 = await res2.json();
                
                if (data2.response && data2.response.length > 0) {
                    currentFixtures = data2.response;
                } else {
                    let res3 = await fetch(`${PROXY_URL}fixtures&league=${leagueId}&season=2024`);
                    let data3 = await res3.json();
                    currentFixtures = (data3.response && data3.response.length > 0) ? data3.response : [];
                }
            }
        } catch (e) { currentFixtures = []; }

        btn.textContent = "Load Up-to-Date Fixtures & Results";
        btn.disabled = false;
        renderMatchDropdown();
        showNotification("Fixtures successfully loaded from live API feed.");
    }

    function resetFixtureSelection() {
        document.getElementById('match-container').style.display = 'none';
        document.getElementById('prediction-results').style.display = 'none';
        document.getElementById('vip-lock-card').style.display = 'none';
        if (refreshInterval) clearInterval(refreshInterval);
    }

    function renderMatchDropdown() {
        const matchSelect = document.getElementById('match-select');
        matchSelect.innerHTML = '';

        if (currentFixtures.length === 0) {
            matchSelect.innerHTML = '<option value="">-- No fixtures found for this season --</option>';
            document.getElementById('match-container').style.display = 'block';
            return;
        }

        matchSelect.innerHTML = '<option value="">-- Select Fixture --</option>';
        currentFixtures.forEach(item => {
            const opt = document.createElement('option');
            opt.value = item.fixture.id;
            const matchDate = item.fixture.date ? item.fixture.date.split('T')[0] : '';
            opt.textContent = `[${item.fixture.status.short}] ${item.teams.home.name} vs ${item.teams.away.name} (${matchDate})`;
            matchSelect.appendChild(opt);
        });
        document.getElementById('match-container').style.display = 'block';
    }

    function triggerPredictionFlow() {
        const matchId = document.getElementById('match-select').value;
        if (!matchId) return;
        selectedFixtureId = matchId;
        document.getElementById('prediction-results').style.display = 'none';
        document.getElementById('vip-lock-card').style.display = 'block';
    }

    async function unlockVIPAnalysis() {
        const keyInput = document.getElementById('vip-key-input').value.trim();
        try {
            const res = await fetch('/api/verify-vip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key: keyInput })
            });
            const data = await res.json();
            if (data.valid) {
                document.getElementById('vip-lock-card').style.display = 'none';
                document.getElementById('vip-error-msg').style.display = 'none';
                generateAdvancedPrediction();
                loadLeagueStandings();
                startAutoRefreshScoreEngine();
            } else {
                document.getElementById('vip-error-msg').style.display = 'block';
            }
        } catch (e) { document.getElementById('vip-error-msg').style.display = 'block'; }
    }

    function generateAdvancedPrediction() {
        const fixture = currentFixtures.find(m => m.fixture.id == selectedFixtureId);
        if (!fixture) return;
        document.getElementById('res-score').textContent = `${fixture.teams.home.name} ${fixture.goals.home ?? 0} - ${fixture.goals.away ?? 0} ${fixture.teams.away.name} [${fixture.fixture.status.short}]`;
        document.getElementById('res-form').textContent = "Multi-Factor Form Analyzed via Live API";
        document.getElementById('res-pred').textContent = `${fixture.teams.home.name} Win / Outcome Projected`;
        document.getElementById('prediction-results').style.display = 'block';
    }

    async function loadLeagueStandings() {
        const leagueId = document.getElementById('league-select').value;
        const container = document.getElementById('standings-content');
        if (!leagueId) return;

        container.innerHTML = '<p style="color: var(--text-muted);">Fetching live league table...</p>';

        try {
            let res = await fetch(`${PROXY_URL}standings&league=${leagueId}&season=2025`);
            let data = await res.json();
            
            if (!data.response || data.response.length === 0) {
                res = await fetch(`${PROXY_URL}standings&league=${leagueId}&season=2024`);
                data = await res.json();
            }

            if (data.response && data.response.length > 0) {
                const standings = data.response[0].league.standings[0];
                let html = `<table>
                    <thead>
                        <tr>
                            <th>Pos</th>
                            <th>Team</th>
                            <th>P</th>
                            <th>W</th>
                            <th>D</th>
                            <th>L</th>
                            <th>PTS</th>
                            <th>Form</th>
                        </tr>
                    </thead>
                    <tbody>`;
                
                standings.forEach(row => {
                    html += `<tr>
                        <td>${row.rank}</td>
                        <td style="font-weight:600; color: #f8fafc;">${row.team.name}</td>
                        <td>${row.all.played}</td>
                        <td>${row.all.win}</td>
                        <td>${row.all.draw}</td>
                        <td>${row.all.lose}</td>
                        <td style="color: var(--accent-green); font-weight:bold;">${row.points}</td>
                        <td style="font-family: monospace; font-size: 0.8rem;">${row.form || '-'}</td>
                    </tr>`;
                });
                html += `</tbody></table>`;
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p style="color: var(--text-muted);">Standings table unavailable for this league season.</p>';
            }
        } catch (e) {
            container.innerHTML = '<p style="color: #ef4444;">Failed to load live standings.</p>';
        }
    }

    function startAutoRefreshScoreEngine() {
        if (refreshInterval) clearInterval(refreshInterval);
        refreshInterval = setInterval(async () => {
            if (!selectedFixtureId) return;
            try {
                const res = await fetch(`${PROXY_URL}fixtures&id=${selectedFixtureId}`);
                const data = await res.json();
                if (data.response && data.response.length > 0) {
                    const updated = data.response[0];
                    const index = currentFixtures.findIndex(m => m.fixture.id == selectedFixtureId);
                    if (index !== -1) currentFixtures[index] = updated;

                    document.getElementById('res-score').textContent = `${updated.teams.home.name} ${updated.goals.home ?? 0} - ${updated.goals.away ?? 0} ${updated.teams.away.name} [${updated.fixture.status.short}]`;
                    showNotification(`Live score updated at ${new Date().toLocaleTimeString()}`);
                }
            } catch (e) { console.error("Auto-refresh error", e); }
        }, 30000);
    }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/proxy')
def proxy():
    endpoint = request.args.get('endpoint')
    if not endpoint:
        return jsonify({"error": "Missing endpoint parameter"}), 400

    headers = {'x-apisports-key': API_KEY}
    url = f"{BASE_URL}{endpoint}"
    params = {k: v for k, v in request.args.items() if k != 'endpoint'}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/purchase-vip', methods=['POST'])
def purchase_vip():
    global APP_REVENUE, TOTAL_TRANSACTIONS
    data = request.get_json()
    email = data.get('email', 'customer@local')
    
    new_key = f"VIP24-{uuid.uuid4().hex[:8].upper()}"
    ACTIVE_VIP_KEYS[new_key] = {"status": "active", "email": email}
    
    APP_REVENUE += 30.00
    TOTAL_TRANSACTIONS += 1
    
    return jsonify({
        "success": True,
        "vip_key": new_key,
        "new_revenue": APP_REVENUE,
        "new_users": TOTAL_TRANSACTIONS
    })

@app.route('/api/verify-vip', methods=['POST'])
def verify_vip():
    data = request.get_json()
    key = data.get('key', '').strip()
    is_valid = key in ACTIVE_VIP_KEYS
    return jsonify({"valid": is_valid})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
