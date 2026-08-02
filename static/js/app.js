// Production Real-Time WebSocket Powered Client Controller for Lumo AI Trading
document.addEventListener("DOMContentLoaded", () => {
    let currentSymbol = "BTC/USDT";
    let currentTimeframe = "1h";
    let currentStrategy = "AI Hybrid";
    let isAutoBotEnabled = false;
    let chartInstance = null;
    let pnlChartInstance = null;
    let socket = null;

    // DOM Elements
    const symbolSelect = document.getElementById("symbolSelect");
    const strategySelect = document.getElementById("strategySelect");
    const toggleBotBtn = document.getElementById("toggleBotBtn");
    const wsDot = document.getElementById("wsDot");
    const wsStatusText = document.getElementById("wsStatusText");

    const valPortfolio = document.getElementById("valPortfolio");
    const valAvailableUsdt = document.getElementById("valAvailableUsdt");
    const valTotalPnl = document.getElementById("valTotalPnl");
    const valDailyPnl = document.getElementById("valDailyPnl");
    const pnlIconBox = document.getElementById("pnlIconBox");
    const valWinRate = document.getElementById("valWinRate");
    const valFearGreedScore = document.getElementById("valFearGreedScore");
    const valFearGreedLabel = document.getElementById("valFearGreedLabel");
    const valNewsScore = document.getElementById("valNewsScore");
    const valNewsLabel = document.getElementById("valNewsLabel");

    const accountingStatusBadge = document.getElementById("accountingStatusBadge");
    const dbSyncStatusBadge = document.getElementById("dbSyncStatusBadge");
    const lastValidationText = document.getElementById("lastValidationText");

    const liveTickerPrice = document.getElementById("liveTickerPrice");
    const activePositionCount = document.getElementById("activePositionCount");
    const positionsTableBody = document.getElementById("positionsTableBody");
    const tradeHistoryTableBody = document.getElementById("tradeHistoryTableBody");
    const tradeHistoryCount = document.getElementById("tradeHistoryCount");
    const ledgerTableBody = document.getElementById("ledgerTableBody");
    const ledgerCount = document.getElementById("ledgerCount");
    const scannerTableBody = document.getElementById("scannerTableBody");

    const aiSignalBadge = document.getElementById("aiSignalBadge");
    const aiConfidenceVal = document.getElementById("aiConfidenceVal");
    const aiActionTitle = document.getElementById("aiActionTitle");
    const aiTargetRange = document.getElementById("aiTargetRange");
    const aiReasoningText = document.getElementById("aiReasoningText");

    const btnOrderLong = document.getElementById("btnOrderLong");
    const btnOrderShort = document.getElementById("btnOrderShort");
    const orderLeverage = document.getElementById("orderLeverage");
    const lblLeverage = document.getElementById("lblLeverage");
    const newsListContainer = document.getElementById("newsListContainer");

    const toggleSMA = document.getElementById("toggleSMA");
    const toggleEMA = document.getElementById("toggleEMA");

    // Initialize Market Price Chart
    function initChart() {
        const ctx = document.getElementById("marketChart").getContext("2d");
        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Price ($)',
                        data: [],
                        borderColor: '#00f2fe',
                        backgroundColor: 'rgba(0, 242, 254, 0.08)',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 0
                    },
                    {
                        label: 'SMA 20',
                        data: [],
                        borderColor: '#ffd600',
                        borderWidth: 1.5,
                        hidden: !toggleSMA.checked,
                        pointRadius: 0
                    },
                    {
                        label: 'EMA 9',
                        data: [],
                        borderColor: '#7c4dff',
                        borderWidth: 1.5,
                        hidden: !toggleEMA.checked,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#94a3b8', font: { family: 'Outfit' } } }
                },
                scales: {
                    x: { ticks: { color: '#64748b', maxTicksLimit: 10 }, grid: { color: 'rgba(255, 255, 255, 0.04)' } },
                    y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255, 255, 255, 0.04)' } }
                }
            }
        });
    }

    // Initialize PnL & Equity History Chart
    function initPnlChart() {
        const ctx = document.getElementById("pnlChart").getContext("2d");
        pnlChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Portfolio Equity ($)',
                        data: [],
                        borderColor: '#00f2fe',
                        backgroundColor: 'rgba(0, 242, 254, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 1
                    },
                    {
                        label: 'Realized PnL ($)',
                        data: [],
                        borderColor: '#00e676',
                        borderWidth: 1.5,
                        fill: false,
                        pointRadius: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#94a3b8', font: { family: 'Outfit', size: 11 } } }
                },
                scales: {
                    x: { ticks: { color: '#64748b', maxTicksLimit: 8 }, grid: { color: 'rgba(255, 255, 255, 0.04)' } },
                    y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255, 255, 255, 0.04)' } }
                }
            }
        });
    }

    // Connect Real-Time WebSocket (<250ms latency)
    function connectWebSocket() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws/stream`;
        
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            wsDot.className = "pulse-dot green";
            wsStatusText.textContent = "WS Connected (Live)";
            console.log("WebSocket connected successfully");
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === "TICKER_UPDATE") {
                    handleLiveUpdate(data);
                }
            } catch (e) {
                console.error("Error parsing WS payload:", e);
            }
        };

        socket.onclose = () => {
            wsDot.className = "pulse-dot red";
            wsStatusText.textContent = "WS Reconnecting...";
            setTimeout(connectWebSocket, 2000);
        };

        socket.onerror = (err) => {
            console.error("WebSocket error:", err);
            socket.close();
        };
    }

    function handleLiveUpdate(data) {
        if (data.prices && data.prices[currentSymbol]) {
            const p = data.prices[currentSymbol];
            liveTickerPrice.textContent = `$${p.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 4})}`;
        }

        if (data.portfolio) {
            updatePortfolioDisplay(data.portfolio);
        }

        if (data.scanner && data.scanner.all_pairs) {
            renderScanner(data.scanner.all_pairs);
        }
    }

    function updatePortfolioDisplay(pf) {
        valPortfolio.textContent = `$${pf.total_portfolio_value.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        valAvailableUsdt.textContent = `Avail: $${pf.usdt_balance.toLocaleString(undefined, {minimumFractionDigits: 2})} | Margin: $${pf.margin_used.toLocaleString(undefined, {minimumFractionDigits: 2})}`;

        const pnlSign = pf.total_pnl_usd >= 0 ? "+" : "";
        valTotalPnl.textContent = `${pnlSign}$${pf.total_pnl_usd.toFixed(2)} (${pnlSign}${pf.total_pnl_pct.toFixed(2)}%)`;
        valTotalPnl.style.color = pf.total_pnl_usd >= 0 ? "var(--accent-green)" : "var(--accent-red)";
        pnlIconBox.className = pf.total_pnl_usd >= 0 ? "metric-icon green" : "metric-icon red";

        const dailySign = pf.daily_pnl_usd >= 0 ? "+" : "";
        valDailyPnl.textContent = `Daily: ${dailySign}$${pf.daily_pnl_usd.toFixed(2)} (${dailySign}${pf.daily_pnl_pct.toFixed(2)}%)`;

        valWinRate.textContent = `Win Rate: ${pf.win_rate}% (${pf.total_closed_trades} Trades)`;

        if (accountingStatusBadge && pf.accounting_status) {
            accountingStatusBadge.textContent = `${pf.accounting_status} (0.01 USDT Tol)`;
            accountingStatusBadge.className = pf.accounting_status === "PASS" ? "badge bullish" : "badge bearish";
        }
        if (dbSyncStatusBadge && pf.database_sync_status) {
            dbSyncStatusBadge.textContent = pf.database_sync_status;
        }
        if (lastValidationText && pf.last_validation_time) {
            lastValidationText.textContent = pf.last_validation_time;
        }

        isAutoBotEnabled = pf.auto_bot_enabled;
        if (isAutoBotEnabled) {
            toggleBotBtn.innerHTML = `<i class="fa-solid fa-power-off"></i> Auto-Bot: ACTIVE`;
            toggleBotBtn.style.background = "var(--accent-green)";
        } else {
            toggleBotBtn.innerHTML = `<i class="fa-solid fa-power-off"></i> Auto-Bot: OFF`;
            toggleBotBtn.style.background = "linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))";
        }

        renderPositions(pf.active_positions);
        renderTradeHistory(pf.trade_history);
        renderLedger(pf.ledger);
        renderPnlChart(pf.pnl_history);
    }

    function renderPositions(positions) {
        if (!positionsTableBody) return;
        activePositionCount.textContent = `${positions ? positions.length : 0} Open`;
        if (!positions || positions.length === 0) {
            positionsTableBody.innerHTML = `<tr><td colspan="9" class="empty-state">No open positions. Use manual panel or enable Auto-Bot.</td></tr>`;
            return;
        }

        let html = "";
        positions.forEach(pos => {
            const pnlSign = pos.unrealized_pnl_usd >= 0 ? "+" : "";
            const pnlColor = pos.unrealized_pnl_usd >= 0 ? "var(--accent-green)" : "var(--accent-red)";
            const sideClass = pos.side === "LONG" ? "long" : "short";

            html += `
                <tr>
                    <td><strong>${pos.symbol}</strong></td>
                    <td><span class="badge ${sideClass}">${pos.side}</span></td>
                    <td>${pos.leverage}x</td>
                    <td>$${pos.entry_price.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td>$${pos.current_price.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td>$${pos.margin_usd.toFixed(2)}</td>
                    <td style="color: ${pnlColor}; font-weight: 700;">${pnlSign}$${pos.unrealized_pnl_usd.toFixed(2)} (${pnlSign}${pos.unrealized_pnl_pct.toFixed(2)}%)</td>
                    <td style="font-size: 10px; color: var(--text-secondary);">SL: $${pos.stop_loss_price}<br>TP: $${pos.take_profit_price}<br>Liq: $${pos.liquidation_price}</td>
                    <td style="display: flex; gap: 4px; flex-wrap: wrap;">
                        <button class="btn-xs" style="color: var(--accent-red); border-color: var(--accent-red);" onclick="managePos('${pos.symbol}', 'CLOSE')">Close</button>
                        <button class="btn-xs" onclick="managePos('${pos.symbol}', 'PARTIAL_CLOSE')">50%</button>
                        <button class="btn-xs" style="color: var(--accent-yellow);" onclick="managePos('${pos.symbol}', 'REVERSE')">Reverse</button>
                    </td>
                </tr>
            `;
        });
        positionsTableBody.innerHTML = html;
    }

    function renderTradeHistory(trades) {
        if (!tradeHistoryTableBody) return;
        if (tradeHistoryCount) tradeHistoryCount.textContent = `${trades ? trades.length : 0} Trades`;

        if (!trades || trades.length === 0) {
            tradeHistoryTableBody.innerHTML = `<tr><td colspan="9" class="empty-state">No trade records available.</td></tr>`;
            return;
        }

        let html = "";
        trades.forEach(t => {
            const isClosed = t.status === "CLOSED" || (t.exit_time && t.exit_time !== "");
            const pnlVal = t.pnl_usd || 0.0;
            const pnlSign = pnlVal >= 0 ? "+" : "";
            const pnlColor = pnlVal >= 0 ? "var(--accent-green)" : "var(--accent-red)";
            const sideClass = t.side === "LONG" ? "long" : "short";

            html += `
                <tr>
                    <td><strong>${t.symbol}</strong><br><span style="font-size: 10px; color: var(--text-secondary);">${t.id}</span></td>
                    <td><span class="badge ${sideClass}">${t.side}</span></td>
                    <td>$${t.entry_price.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td>${isClosed ? '$' + t.exit_price.toLocaleString(undefined, {minimumFractionDigits: 2}) : '-'}</td>
                    <td>${typeof t.amount === 'number' ? t.amount.toFixed(4) : t.amount}</td>
                    <td>$${typeof t.margin_usd === 'number' ? t.margin_usd.toFixed(2) : t.margin_usd}</td>
                    <td style="color: ${pnlColor}; font-weight: 700;">${isClosed ? `${pnlSign}$${pnlVal.toFixed(2)}` : '$0.00'}</td>
                    <td style="color: ${pnlColor}; font-weight: 700;">${isClosed ? `${pnlSign}${(t.pnl_pct || 0).toFixed(2)}%` : '0.0%'}</td>
                    <td><span class="badge ${isClosed ? 'neutral' : 'bullish'}">${isClosed ? 'CLOSED' : 'OPEN'}</span><br><span style="font-size: 10px; color: var(--text-secondary);">${isClosed ? t.exit_time : t.entry_time}</span></td>
                </tr>
            `;
        });
        tradeHistoryTableBody.innerHTML = html;
    }

    function renderLedger(ledger) {
        if (!ledgerTableBody) return;
        if (ledgerCount) ledgerCount.textContent = `${ledger ? ledger.length : 0} Entries`;

        if (!ledger || ledger.length === 0) {
            ledgerTableBody.innerHTML = `<tr><td colspan="6" class="empty-state">No transaction records available.</td></tr>`;
            return;
        }

        let html = "";
        ledger.slice().reverse().forEach(tx => {
            const isCredit = tx.amount >= 0;
            const amtSign = isCredit ? "+" : "";
            const amtColor = isCredit ? "var(--accent-green)" : "var(--accent-red)";

            html += `
                <tr>
                    <td><strong style="font-size: 11px;">${tx.tx_id}</strong></td>
                    <td style="font-size: 11px; color: var(--text-secondary);">${tx.timestamp}</td>
                    <td><span class="badge ${isCredit ? 'bullish' : 'bearish'}">${tx.tx_type}</span></td>
                    <td style="color: ${amtColor}; font-weight: 700;">${amtSign}$${tx.amount.toFixed(2)}</td>
                    <td><strong>$${tx.balance_after.toFixed(2)}</strong></td>
                    <td style="font-size: 11px; color: var(--text-secondary);">${tx.description || tx.reference_id}</td>
                </tr>
            `;
        });
        ledgerTableBody.innerHTML = html;
    }

    function renderPnlChart(pnlHistory) {
        if (!pnlChartInstance || !pnlHistory) return;
        const labels = pnlHistory.map(h => h.timestamp);
        const equityData = pnlHistory.map(h => h.equity);
        const realizedData = pnlHistory.map(h => h.realized_pnl);

        pnlChartInstance.data.labels = labels;
        pnlChartInstance.data.datasets[0].data = equityData;
        pnlChartInstance.data.datasets[1].data = realizedData;
        pnlChartInstance.update();
    }

    function renderScanner(pairs) {
        let html = "";
        pairs.forEach(p => {
            const badgeClass = p.action.includes("BUY") ? "bullish" : (p.action.includes("SELL") ? "bearish" : "neutral");
            html += `
                <tr style="cursor: pointer;" onclick="selectSymbol('${p.symbol}')">
                    <td><strong>${p.symbol}</strong></td>
                    <td>$${p.current_price.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td><span class="badge ${badgeClass}">${p.action.replace('_', ' ')}</span></td>
                    <td><strong style="color: var(--accent-cyan);">${p.confidence_score}%</strong></td>
                </tr>
            `;
        });
        scannerTableBody.innerHTML = html;
    }

    window.selectSymbol = function(sym) {
        symbolSelect.value = sym;
        currentSymbol = sym;
        updateChartAndSignal();
    };

    window.managePos = async function(sym, action) {
        try {
            const res = await fetch("/api/trade/position-action", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symbol: sym, action: action, ratio: 0.5 })
            });
            const data = await res.json();
            alert(data.message);
            const pfRes = await fetch("/api/portfolio");
            if (pfRes.ok) {
                const pf = await pfRes.json();
                updatePortfolioDisplay(pf);
            }
        } catch (err) {
            alert("Position action failed: " + err);
        }
    };

    async function updateChartAndSignal() {
        try {
            const [mktRes, sigRes, newsRes, pfRes] = await Promise.all([
                fetch(`/api/market-summary?symbol=${encodeURIComponent(currentSymbol)}&timeframe=${currentTimeframe}`),
                fetch(`/api/ai-signal/${encodeURIComponent(currentSymbol)}?strategy=${encodeURIComponent(currentStrategy)}`),
                fetch("/api/news-sentiment"),
                fetch("/api/portfolio")
            ]);

            if (mktRes.ok) {
                const mkt = await mktRes.json();
                if (chartInstance && mkt.chart_data) {
                    const labels = mkt.chart_data.map(c => new Date(c.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}));
                    const prices = mkt.chart_data.map(c => c.close);
                    const sma20 = mkt.chart_data.map(c => c.sma_20);
                    const ema9 = mkt.chart_data.map(c => c.ema_9);

                    chartInstance.data.labels = labels;
                    chartInstance.data.datasets[0].data = prices;
                    chartInstance.data.datasets[0].label = `${currentSymbol} (${currentTimeframe})`;
                    chartInstance.data.datasets[1].data = sma20;
                    chartInstance.data.datasets[2].data = ema9;
                    chartInstance.update();
                }
            }

            if (sigRes.ok) {
                const sig = await sigRes.json();
                aiSignalBadge.textContent = sig.action.replace('_', ' ');
                aiSignalBadge.className = `badge ${sig.action.includes('BUY') ? 'bullish' : (sig.action.includes('SELL') ? 'bearish' : 'neutral')}`;

                aiConfidenceVal.textContent = `${sig.confidence_score}%`;
                aiActionTitle.textContent = `${sig.action.replace('_', ' ')} (${sig.direction})`;
                aiTargetRange.textContent = `SL: $${sig.stop_loss_price} (-${sig.stop_loss_pct}%) | TP: $${sig.take_profit_price} (+${sig.take_profit_pct}%)`;
                aiReasoningText.textContent = sig.reasoning;
            }

            if (newsRes.ok) {
                const news = await newsRes.json();
                valFearGreedScore.innerHTML = `${news.fear_greed.value} <span class="badge neutral">${news.fear_greed.classification}</span>`;
                valNewsScore.innerHTML = `${news.sentiment_summary.news_score_avg} <span class="badge bullish">${news.sentiment_summary.label}</span>`;

                let newsHtml = "";
                news.news_articles.forEach(art => {
                    newsHtml += `
                        <div class="news-item">
                            <span class="badge ${art.sentiment === 'Bullish' ? 'bullish' : 'bearish'}">${art.sentiment}</span>
                            <a href="${art.link}" target="_blank" class="news-title">${art.title}</a>
                        </div>
                    `;
                });
                newsListContainer.innerHTML = newsHtml;
            }

            if (pfRes.ok) {
                const pf = await pfRes.json();
                updatePortfolioDisplay(pf);
            }

        } catch (err) {
            console.error("Dashboard refresh error:", err);
        }
    }

    // Event Listeners
    symbolSelect.addEventListener("change", (e) => {
        currentSymbol = e.target.value;
        updateChartAndSignal();
    });

    strategySelect.addEventListener("change", async (e) => {
        currentStrategy = e.target.value;
        await fetch("/api/bot/strategy", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ strategy_name: currentStrategy, risk_mode: "Moderate" })
        });
        updateChartAndSignal();
    });

    document.querySelectorAll(".tf-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".tf-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentTimeframe = btn.dataset.tf;
            updateChartAndSignal();
        });
    });

    orderLeverage.addEventListener("input", (e) => {
        lblLeverage.textContent = `${e.target.value}x`;
    });

    toggleSMA.addEventListener("change", (e) => {
        if (chartInstance) { chartInstance.data.datasets[1].hidden = !e.target.checked; chartInstance.update(); }
    });
    toggleEMA.addEventListener("change", (e) => {
        if (chartInstance) { chartInstance.data.datasets[2].hidden = !e.target.checked; chartInstance.update(); }
    });

    btnOrderLong.addEventListener("click", async () => {
        await submitManualOrder("LONG");
    });

    btnOrderShort.addEventListener("click", async () => {
        await submitManualOrder("SHORT");
    });

    async function submitManualOrder(side) {
        const orderType = document.getElementById("orderTypeSelect").value;
        const allocUsdt = parseFloat(document.getElementById("orderAmountUsdt").value) || 1000.0;
        const lev = parseInt(orderLeverage.value) || 1;

        try {
            const res = await fetch("/api/trade/order", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    symbol: currentSymbol,
                    side: side,
                    order_type: orderType,
                    allocation_usd: allocUsdt,
                    leverage: lev,
                    stop_loss_price: null,
                    take_profit_price: null
                })
            });
            const data = await res.json();
            alert(data.message);
            const pfRes = await fetch("/api/portfolio");
            if (pfRes.ok) {
                const pf = await pfRes.json();
                updatePortfolioDisplay(pf);
            }
        } catch (err) {
            alert("Order failed: " + err);
        }
    }

    toggleBotBtn.addEventListener("click", async () => {
        const nextState = !isAutoBotEnabled;
        try {
            const res = await fetch(`/api/bot/toggle?enable=${nextState}`, { method: "POST" });
            const data = await res.json();
            alert(data.message);
        } catch (err) {
            alert("Error toggling bot: " + err);
        }
    });

    // Startup
    initChart();
    initPnlChart();
    connectWebSocket();
    updateChartAndSignal();
});
