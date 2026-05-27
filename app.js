// ==========================================================================
// Vibecoding Political Wealth: Interactive Application Logic
// Scrollama scrollytelling + data-driven DOM rendering + search
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {

  // ---------- DATA BOOTSTRAP ----------
  const data = window.NETA_DATA;
  if (!data) {
    console.error("[app] NETA_DATA not loaded – make sure data.js is included before app.js");
    return;
  }

  // =====================================================================
  // 1. SCROLLAMA — STICKY PANE SCROLLYTELLING
  // =====================================================================
  const scroller = scrollama();

  /**
   * Handle each narrative step entering the viewport.
   * - Toggles `.is-active` on the step text blocks
   * - Swaps the visible sticky graphic pane
   */
  function handleStepEnter(response) {
    const stepIndex = +response.element.dataset.step;

    // Toggle active class on step text sections
    document.querySelectorAll("#scrolly .step").forEach((el, idx) => {
      el.classList.toggle("is-active", idx === stepIndex - 1);
    });

    // Remove active from all graphic panes first
    document.querySelectorAll(".graphic-container .pane").forEach(pane => {
      pane.classList.remove("is-active");
    });

    // Activate the correct pane based on step number
    const paneMap = {
      1: "pane-whatsapp",
      2: "pane-parser",
      3: "pane-reveal"
    };
    const targetPaneId = paneMap[stepIndex];
    if (targetPaneId) {
      document.getElementById(targetPaneId)?.classList.add("is-active");
    }
  }

  // Initialise Scrollama with a 50 % viewport offset
  scroller
    .setup({
      step: "#scrolly .step",
      offset: 0.5,
      debug: false
    })
    .onStepEnter(handleStepEnter);

  // Re-measure on window resize so sticky positions stay correct
  window.addEventListener("resize", scroller.resize);


  // =====================================================================
  // 2. CHAPTER 1 — ANIMATED VERTICAL BAR CHART (Index Comparison)
  // =====================================================================
  const chartContainer = document.getElementById("nifty-comparison-chart");

  /**
   * Convert "#rrggbb" -> "rgba(r,g,b,alpha)" so bar fills can be translucent
   * while remaining keyed off the same palette tokens defined in data.js.
   */
  function hexToRgba(hex, alpha) {
    const h = hex.replace("#", "");
    const r = parseInt(h.substring(0, 2), 16);
    const g = parseInt(h.substring(2, 4), 16);
    const b = parseInt(h.substring(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  /**
   * Build the vertical bar columns from `NETA_DATA.indices`.
   * Bars start at height:0 and animate up via IntersectionObserver.
   */
  function renderComparisonChart() {
    if (!chartContainer) return;
    chartContainer.innerHTML = "";

    // Wrapper that lays bars side-by-side
    const chart = document.createElement("div");
    chart.className = "vbar-chart";

    // Largest absolute value drives proportional sizing
    const maxVal = Math.max(...data.indices.map(i => Math.abs(i.returnPct)));

    data.indices.forEach(item => {
      const displayPct =
        (item.returnPct >= 0 ? "+" : "") + item.returnPct.toFixed(2) + "%";

      // Target height as % of track. Guarantee a minimum so small bars stay legible.
      const targetHeight = Math.max(
        6,
        (Math.abs(item.returnPct) / maxVal) * 100
      ).toFixed(2);

      const col = document.createElement("div");
      col.className = "vbar";
      col.innerHTML = `
        <div class="vbar-value" style="color:${item.color}">${displayPct}</div>
        <div class="vbar-track">
          <div class="vbar-fill"
               style="background:${hexToRgba(item.color, 0.55)};
                      border-top:2px solid ${item.color};"
               data-target="${targetHeight}"></div>
        </div>
        <div class="vbar-label">${item.short || item.label}</div>
      `;
      chart.appendChild(col);
    });

    chartContainer.appendChild(chart);
  }

  renderComparisonChart();

  // Animate bar heights only when the chart scrolls into view
  if (chartContainer) {
    const chartObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            chartContainer.querySelectorAll(".vbar-fill").forEach(bar => {
              const target = parseFloat(bar.dataset.target) || 0;
              bar.style.height = target + "%";
            });
            chartObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    chartObserver.observe(chartContainer);
  }


  // =====================================================================
  // 3. CHAPTER 2 — TABBED LEADERBOARD (Dumbbell / slope-chart)
  // Each MP is a row with two dots (base → current) and a colored line
  // between them. Replaces the previous 5-card grid for a more graphical,
  // skim-friendly comparison.
  // =====================================================================
  const leaderboardCards = document.getElementById("leaderboard-cards");
  const tabButtons = document.querySelectorAll(".selector-tabs .tab-btn");

  /**
   * Render a leaderboard tab as a dumbbell chart.
   * @param {string} tabKey — one of 'bestReturn', 'worstReturn', 'bestGainers'
   */
  function renderLeaderboard(tabKey) {
    if (!leaderboardCards) return;
    leaderboardCards.innerHTML = "";
    leaderboardCards.classList.add("leaderboard-dumbbells");

    const list = data.leaderboards[tabKey];
    if (!list) return;

    // Normalise rows: bestGainers stores `gain` not `current`. Compute both.
    const rows = list.map(item => {
      const current = item.current != null
        ? item.current
        : item.base + (item.gain || 0);
      const gain = item.gain != null ? item.gain : (current - item.base);
      return { ...item, current, gain };
    });

    // Shared scale across the visible tab so bars are comparable.
    const maxVal = Math.max(...rows.map(r => Math.max(r.base, r.current))) * 1.04;

    rows.forEach(item => {
      const positive   = item.gain >= 0;
      const leftPct    = (Math.min(item.base, item.current) / maxVal) * 100;
      const rightPct   = (Math.max(item.base, item.current) / maxVal) * 100;
      const segWidth   = Math.max(0.4, rightPct - leftPct); // never zero-width
      const segColor   = positive ? "var(--green)" : "var(--red)";

      const rankStr = "#" + String(item.rank).padStart(2, "0");
      const partyClass = item.party.toLowerCase().replace(/[^a-z]/g, "");
      const pctStr     = (item.returnPct >= 0 ? "+" : "") + item.returnPct.toFixed(2) + "%";
      const gainStr    = (item.gain >= 0 ? "+" : "−") + "Rs " + Math.abs(item.gain).toFixed(2) + " Cr";

      const row = document.createElement("div");
      row.className = "lb-row";
      row.innerHTML = `
        <div class="lb-rank">${rankStr}</div>
        <div class="lb-info">
          <span class="lb-party-pill ${partyClass}">${item.party}</span>
          <div class="lb-name">${item.name}</div>
          <div class="lb-constituency">${item.constituency}</div>
        </div>

        <div class="lb-track" aria-label="Wealth from base to current">
          <div class="lb-axis"></div>
          <div class="lb-segment" style="left:${leftPct}%; width:${segWidth}%; background:${segColor}"></div>
          <div class="lb-dot lb-dot-base"    style="left:${(item.base   /maxVal)*100}%" title="Base Rs ${item.base.toFixed(2)} Cr"></div>
          <div class="lb-dot lb-dot-current" style="left:${(item.current/maxVal)*100}%; background:${segColor}; border-color:${segColor}" title="Current Rs ${item.current.toFixed(2)} Cr"></div>
          <div class="lb-scale-label lb-base-label"    style="left:${(item.base   /maxVal)*100}%">Rs ${item.base.toFixed(2)} Cr</div>
          <div class="lb-scale-label lb-current-label" style="left:${(item.current/maxVal)*100}%; color:${segColor}">Rs ${item.current.toFixed(2)} Cr</div>
        </div>

        <div class="lb-meta">
          <div class="lb-gain ${positive ? "green" : "red"}">${gainStr}</div>
          <div class="lb-pct  ${positive ? "green" : "red"}">${pctStr}</div>
        </div>

        <div class="lb-driver-row">
          <span class="lb-driver-label">Driver</span>
          <span class="lb-driver-text">${item.driver}</span>
        </div>
      `;
      leaderboardCards.appendChild(row);
    });
  }

  // Default render: best returns
  renderLeaderboard("bestReturn");

  // Tab click handler — swap active class and re-render
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderLeaderboard(btn.getAttribute("data-tab"));
    });
  });


  // =====================================================================
  // 4. CHAPTER 4 — GOLD & SILVER RENDERING
  // =====================================================================

  // ----- A. Top Gold Holders -----
  const goldHoldersTable = document.getElementById("gold-holders-table");

  function renderGoldHolders() {
    if (!goldHoldersTable) return;
    goldHoldersTable.innerHTML = "";

    data.topGoldHolders.forEach(item => {
      const weightKg = (item.weight / 1000).toFixed(2);
      const row = document.createElement("div");
      row.className = "holder-row";
      row.innerHTML = `
        <div class="holder-rank">0${item.rank}</div>
        <div class="holder-info">
          <h4 class="holder-name">
            ${item.name}
            <span class="card-tag ${item.party.toLowerCase().replace(/[^a-z]/g,'')}">${item.party}</span>
          </h4>
          <p class="holder-meta">${item.constituency} &bull; ${weightKg} kg gold</p>
        </div>
        <div class="holder-value">
          <div class="holder-val-now gold-text">Rs ${item.current.toFixed(2)} Cr</div>
          <div class="holder-val-then"><s>Rs ${item.base.toFixed(2)} Cr</s></div>
        </div>
      `;
      goldHoldersTable.appendChild(row);
    });
  }
  renderGoldHolders();

  // ----- B. Top Silver Holders -----
  const silverHoldersTable = document.getElementById("silver-holders-table");

  function renderSilverHolders() {
    if (!silverHoldersTable) return;
    silverHoldersTable.innerHTML = "";

    data.topSilverHolders.forEach(item => {
      const weightKg = (item.weight / 1000).toFixed(2);
      const row = document.createElement("div");
      row.className = "holder-row";
      row.innerHTML = `
        <div class="holder-rank">0${item.rank}</div>
        <div class="holder-info">
          <h4 class="holder-name">
            ${item.name}
            <span class="card-tag ${item.party.toLowerCase().replace(/[^a-z]/g,'')}">${item.party}</span>
          </h4>
          <p class="holder-meta">${item.constituency} &bull; ${weightKg} kg silver</p>
        </div>
        <div class="holder-value">
          <div class="holder-val-now silver-text">Rs ${item.current.toFixed(2)} Cr</div>
          <div class="holder-val-then"><s>Rs ${item.base.toFixed(2)} Cr</s></div>
        </div>
      `;
      silverHoldersTable.appendChild(row);
    });
  }
  renderSilverHolders();

  // ----- C. Mixed Separations Cards -----
  const mixedSeparationCards = document.getElementById("mixed-separation-cards");

  function renderMixedSeparations() {
    if (!mixedSeparationCards) return;
    mixedSeparationCards.innerHTML = "";

    data.mixedSeparations.forEach(item => {
      const card = document.createElement("div");
      card.className = "mixed-card";
      card.innerHTML = `
        <h4>${item.name}</h4>
        <div class="mixed-bubble" style="font-family:monospace">${item.mixedStr}</div>
        <p class="mixed-separated"><strong>Audited Separation:</strong> ${item.separated}</p>
      `;
      mixedSeparationCards.appendChild(card);
    });
  }
  renderMixedSeparations();

  // ----- D. Party Gold & Silver Table -----
  const partyMetalsTbody = document
    .getElementById("party-metals-table")
    ?.querySelector("tbody");

  function renderPartyMetals() {
    if (!partyMetalsTbody) return;
    partyMetalsTbody.innerHTML = "";

    data.partyGoldSilver.forEach(item => {
      const isCoalition = item.rank === "-";
      const tr = document.createElement("tr");
      if (isCoalition) tr.className = "highlight-coalition";

      tr.innerHTML = `
        <td>${item.rank}</td>
        <td><strong>${item.name}</strong></td>
        <td>${item.count}</td>
        <td>${item.goldWeight.toFixed(2)} kg</td>
        <td>${item.silverWeight.toLocaleString("en-IN")} kg</td>
        <td>Rs ${item.base.toFixed(2)} Cr</td>
        <td><strong>Rs ${item.current.toFixed(2)} Cr</strong></td>
        <td class="green-pct">+${item.returnPct.toFixed(1)}%</td>
      `;
      partyMetalsTbody.appendChild(tr);
    });
  }
  renderPartyMetals();


  // =====================================================================
  //  CH.3 / CH.4 — Insights from the investment performance report
  // =====================================================================

  /**
   * Return a CSS class for ± return colouring, using the page palette
   * (green / red CSS vars) rather than bespoke colours per table.
   */
  function pctClass(p) {
    return p >= 0 ? "green-pct" : "red-pct";
  }
  function pctFmt(p) {
    return (p >= 0 ? "+" : "") + p.toFixed(1) + "%";
  }

  /**
   * Manifest: company/fund-house domain → self-hosted logo path under
   * assets/logos/. These were fetched once from each company's own
   * apple-touch-icon / favicon endpoint (or Google's favicon mirror for
   * the few sites that don't serve one directly), so the page no longer
   * depends on any third-party CDN being up at runtime.
   */
  const LOGO_MANIFEST = {
    "ril.com":                       "assets/logos/ril.ico",
    "hdfcbank.com":                  "assets/logos/hdfcbank.png",
    "itcportal.com":                 "assets/logos/itcportal.png",
    "tatasteel.com":                 "assets/logos/tatasteel.png",
    "reliancepower.co.in":           "assets/logos/reliancepower.svg",
    "jiofinancialservices.com":      "assets/logos/jiofinancialservices.ico",
    "icicibank.com":                 "assets/logos/icicibank.png",
    "infosys.com":                   "assets/logos/infosys.png",
    "sbi.co.in":                     "assets/logos/sbi.png",
    "yesbank.in":                    "assets/logos/yesbank.ico",
    "iciciprumf.com":                "assets/logos/iciciprumf.png",
    "kotakmf.com":                   "assets/logos/kotakmf.ico",
    "hdfcfund.com":                  "assets/logos/hdfcfund.png",
    "axismf.com":                    "assets/logos/axismf.ico",
    "miraeassetmf.co.in":            "assets/logos/miraeassetmf.png",
    "sbimf.com":                     "assets/logos/sbimf.png",
    "motilaloswalmf.com":            "assets/logos/motilaloswalmf.ico",
    "licmf.com":                     "assets/logos/licmf.png",
    "meta.com":                      "assets/logos/meta.png"
  };

  /**
   * Build a square logo tile for a company / fund house.
   *
   * Source priority:
   *   1. Self-hosted file in assets/logos/ (via LOGO_MANIFEST)
   *   2. Google s2 favicons (sz=128)  — for any domain not in manifest
   *   3. DuckDuckGo ip3 icons         — backup if Google blocks
   *   4. Monogram (initials)          — final fallback
   *
   * @param {string} domain — e.g. "hdfcbank.com"
   * @param {string} label  — used for alt text + fallback initials
   */
  function logoTile(domain, label) {
    const safe = (label || "").replace(/&/g, "&amp;").replace(/</g, "&lt;");
    const initials = (label || "")
      .split(/\s+/)
      .filter(w => /^[A-Za-z]/.test(w))
      .slice(0, 2)
      .map(w => w[0].toUpperCase())
      .join("") || "·";

    if (!domain) {
      return `<span class="logo-tile"><span class="logo-fallback" style="display:flex">${initials}</span></span>`;
    }

    const local    = LOGO_MANIFEST[domain];
    const google   = `https://www.google.com/s2/favicons?domain=${domain}&sz=128`;
    const ddg      = `https://icons.duckduckgo.com/ip3/${domain}.ico`;
    const primary  = local || google;
    const fallback = local ? google : ddg;

    return `
      <span class="logo-tile">
        <img class="logo-img"
             src="${primary}"
             alt="${safe}"
             loading="lazy"
             data-fallback="${fallback}"
             onerror="
               if (this.dataset.fallback) {
                 this.src = this.dataset.fallback;
                 this.dataset.fallback = '';
               } else {
                 this.style.display='none';
                 this.nextElementSibling.style.display='flex';
               }
             ">
        <span class="logo-fallback">${initials}</span>
      </span>
    `;
  }

  // ----- Super Pickers (Ch.3) -----
  const superPickersTbody = document
    .getElementById("super-pickers-table")
    ?.querySelector("tbody");

  function renderSuperPickers() {
    if (!superPickersTbody) return;
    superPickersTbody.innerHTML = "";
    (data.superPickers || []).forEach((sp, i) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${i + 1}</td>
        <td><strong>${sp.name}</strong></td>
        <td>${sp.party}</td>
        <td><strong>${sp.count}</strong></td>
        <td>${sp.primaryDriver}</td>
      `;
      superPickersTbody.appendChild(tr);
    });
  }
  renderSuperPickers();

  // ----- Party Performance (Ch.3) -----
  const partyPerfTbody = document
    .getElementById("party-perf-table")
    ?.querySelector("tbody");

  function renderPartyPerformance() {
    if (!partyPerfTbody) return;
    partyPerfTbody.innerHTML = "";
    (data.partyPerformance || []).forEach((p, i) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${i + 1}</td>
        <td><strong>${p.name}</strong></td>
        <td>${p.count}</td>
        <td>Rs ${p.aum.toFixed(2)}</td>
        <td class="${pctClass(p.returnPct)}">${pctFmt(p.returnPct)}</td>
        <td class="${pctClass(p.avgReturnPct)}">${pctFmt(p.avgReturnPct)}</td>
        <td class="party-note">${p.note}</td>
      `;
      partyPerfTbody.appendChild(tr);
    });
  }
  renderPartyPerformance();

  // ----- Preferred Stocks (Ch.4) -----
  const preferredStocksTbody = document
    .getElementById("preferred-stocks-table")
    ?.querySelector("tbody");

  function renderPreferredStocks(view = "holders") {
    if (!preferredStocksTbody) return;
    preferredStocksTbody.innerHTML = "";
    const rows = view === "aum"
      ? (data.preferredStocksByAum || [])
      : (data.preferredStocks      || []);
    rows.forEach((s, i) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${i + 1}</td>
        <td class="logo-cell">
          ${logoTile(s.domain, s.name)}
          <span class="logo-cell-label">
            <span class="logo-cell-name">${s.name}</span>
            <code class="logo-cell-ticker">${s.ticker}</code>
          </span>
        </td>
        <td><strong>${s.holders}</strong></td>
        <td>Rs ${s.aumCr.toFixed(2)}</td>
        <td class="${pctClass(s.returnPct)}">${pctFmt(s.returnPct)}</td>
      `;
      preferredStocksTbody.appendChild(tr);
    });
  }
  renderPreferredStocks();

  // ----- Preferred Mutual Funds (Ch.4) -----
  const preferredFundsTbody = document
    .getElementById("preferred-funds-table")
    ?.querySelector("tbody");

  function renderPreferredFunds(view = "holders") {
    if (!preferredFundsTbody) return;
    preferredFundsTbody.innerHTML = "";
    const rows = view === "aum"
      ? (data.preferredFundsByAum || [])
      : (data.preferredFunds      || []);
    rows.forEach((f, i) => {
      const tr = document.createElement("tr");
      const foreignPill = f.foreign ? ` <span class="foreign-pill">global</span>` : "";
      tr.innerHTML = `
        <td>${i + 1}</td>
        <td class="logo-cell">
          ${logoTile(f.domain, f.house || f.name)}
          <span class="logo-cell-label">
            <span class="logo-cell-name">${f.house || ""} · ${f.short || f.name}${foreignPill}</span>
            <span class="logo-cell-ticker">${f.name}</span>
          </span>
        </td>
        <td><strong>${f.holders}</strong></td>
        <td>Rs ${f.aumCr.toFixed(2)}</td>
        <td class="${pctClass(f.returnPct)}">${pctFmt(f.returnPct)}</td>
      `;
      preferredFundsTbody.appendChild(tr);
    });
  }
  renderPreferredFunds();

  // ----- Toggle wiring: swap dataset + lead paragraph by view -----
  document.querySelectorAll(".view-toggle").forEach(group => {
    const targetId = group.dataset.toggle; // "preferred-stocks" | "preferred-funds"
    const section  = group.closest(".ch3-subsection");
    const buttons  = group.querySelectorAll(".view-toggle-btn");

    buttons.forEach(btn => {
      btn.addEventListener("click", () => {
        const view = btn.dataset.view;
        // Toggle active button styling
        buttons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        // Swap which lead paragraph is visible
        section.querySelectorAll(".subsection-lead").forEach(p => {
          p.hidden = (p.dataset.view !== view);
        });
        // Re-render the matching table
        if (targetId === "preferred-stocks") renderPreferredStocks(view);
        if (targetId === "preferred-funds")  renderPreferredFunds(view);
      });
    });
  });

  // ----- Global Standouts (Ch.4) -----
  const globalCardsEl = document.getElementById("global-cards");

  function renderGlobalCards() {
    if (!globalCardsEl) return;
    globalCardsEl.innerHTML = "";
    (data.globalAssets || []).forEach(g => {
      const card = document.createElement("div");
      card.className = "global-card";
      card.innerHTML = `
        <div class="global-card-head">
          ${logoTile(g.domain, g.short || g.asset)}
          <div class="global-card-kind">${g.kind}</div>
        </div>
        <div class="global-card-asset">${g.short || g.asset}</div>
        <div class="global-card-holder">${g.holder}${g.party && g.party !== "—" ? ` · ${g.party}` : ""}</div>
        <div class="global-card-return">${pctFmt(g.returnPct)}</div>
      `;
      globalCardsEl.appendChild(card);
    });
  }
  renderGlobalCards();


  // ----- E. Comical Affidavit Weight Distortions -----
  const distortionCardsEl = document.getElementById("distortion-cards");

  function renderDistortions() {
    if (!distortionCardsEl) return;
    distortionCardsEl.innerHTML = "";

    data.weightDistortions.forEach(item => {
      const card = document.createElement("div");
      card.className = "distortion-card";
      card.innerHTML = `
        <h4>${item.name}</h4>
        <div class="dist-metric-box">
          <div class="dist-claim">
            <span class="lbl">Raw Claimed Weight</span>
            <span class="val raw" style="text-decoration:line-through; color:#ef4444">${item.claimed}</span>
          </div>
          <div class="dist-claim">
            <span class="lbl">Audited Real Weight</span>
            <span class="val real" style="color:#10b981">${item.reality.split(".")[0]}.</span>
          </div>
        </div>
        <p class="dist-desc">${item.reality}</p>
      `;
      distortionCardsEl.appendChild(card);
    });
  }
  renderDistortions();


  // =====================================================================
  // 5. SEARCH BAR — MP PORTFOLIO SEARCH
  // =====================================================================
  const searchInput = document.getElementById("mp-search-input");
  const searchResults = document.getElementById("search-results");

  if (searchInput && searchResults) {
    /**
     * Build a de-duplicated, searchable index of all MP names across every
     * data source in NETA_DATA. For each MP we gather whatever metrics are
     * available (return%, gold weight, constituency, party, etc.).
     */
    function buildSearchIndex() {
      const mpMap = new Map(); // keyed by normalised name

      /**
       * Helper: upsert an MP record into the map, merging new fields
       * into any existing entry so we don't lose data across sources.
       */
      function upsert(raw) {
        if (!raw || !raw.name) return;
        const key = raw.name.trim().toLowerCase();

        const existing = mpMap.get(key) || {
          name: raw.name.trim(),
          party: null,
          constituency: null,
          returnPct: null,
          gain: null,
          base: null,
          current: null,
          goldWeightKg: null,
          silverWeightKg: null,
          superPickerCount: null,
          driver: null,
          stock: null,
          stockReturnPct: null
        };

        // Merge fields – keep the first non-null value already stored
        if (raw.party) existing.party = existing.party || raw.party;
        if (raw.constituency) existing.constituency = existing.constituency || raw.constituency;
        if (raw.returnPct != null && existing.returnPct == null) existing.returnPct = raw.returnPct;
        if (raw.gain != null) existing.gain = existing.gain || raw.gain;
        if (raw.base != null) existing.base = existing.base || raw.base;
        if (raw.current != null) existing.current = existing.current || raw.current;
        if (raw.goldWeightKg != null) existing.goldWeightKg = raw.goldWeightKg;
        if (raw.silverWeightKg != null) existing.silverWeightKg = raw.silverWeightKg;
        if (raw.superPickerCount != null) existing.superPickerCount = raw.superPickerCount;
        if (raw.driver) existing.driver = existing.driver || raw.driver;
        if (raw.stock) existing.stock = raw.stock;
        if (raw.stockReturnPct != null) existing.stockReturnPct = raw.stockReturnPct;

        mpMap.set(key, existing);
      }

      // --- Source: Leaderboards (bestReturn, worstReturn, bestGainers) ---
      ["bestReturn", "worstReturn", "bestGainers"].forEach(key => {
        (data.leaderboards[key] || []).forEach(mp => {
          upsert({
            name: mp.name,
            party: mp.party,
            constituency: mp.constituency,
            returnPct: mp.returnPct,
            gain: mp.gain || null,
            base: mp.base,
            current: mp.current,
            driver: mp.driver
          });
        });
      });

      // --- Source: Super Pickers ---
      (data.superPickers || []).forEach(sp => {
        upsert({
          name: sp.name,
          party: sp.party,
          superPickerCount: sp.count
        });
      });

      // --- Source: Best Stocks (individual stock picks) ---
      (data.bestStocks || []).forEach(bs => {
        upsert({
          name: bs.name,
          party: bs.party,
          stock: bs.stock,
          stockReturnPct: bs.returnPct
        });
      });

      // --- Source: Top Gold Holders ---
      (data.topGoldHolders || []).forEach(gh => {
        upsert({
          name: gh.name,
          party: gh.party,
          constituency: gh.constituency,
          goldWeightKg: (gh.weight / 1000).toFixed(2),
          base: gh.base,
          current: gh.current
        });
      });

      // --- Source: Top Silver Holders ---
      (data.topSilverHolders || []).forEach(sh => {
        upsert({
          name: sh.name,
          party: sh.party,
          constituency: sh.constituency,
          silverWeightKg: (sh.weight / 1000).toFixed(2),
          base: sh.base,
          current: sh.current
        });
      });

      // --- Source: Party Gold/Silver (party-level, no individual names) ---
      // These are party aggregates, not individual MPs — skip for search.

      return Array.from(mpMap.values());
    }

    const searchIndex = buildSearchIndex();

    /**
     * Render search results to the DOM.
     * @param {Array} results — filtered MP objects
     * @param {string} query  — the raw user query (for empty-state messaging)
     */
    function renderSearchResults(results, query) {
      searchResults.innerHTML = "";

      // Empty state: no query entered yet
      if (!query || query.trim().length === 0) {
        searchResults.innerHTML =
          '<p class="search-empty">Type an MP\'s name to search...</p>';
        return;
      }

      // No matches
      if (results.length === 0) {
        searchResults.innerHTML =
          '<p class="search-empty">No results found</p>';
        return;
      }

      results.forEach(mp => {
        const card = document.createElement("div");
        card.className = "result-card";

        // Build dynamic metrics line based on available data
        const metrics = [];
        if (mp.returnPct != null) {
          const sign = mp.returnPct >= 0 ? "+" : "";
          metrics.push(`Return: <span class="${mp.returnPct >= 0 ? "green" : "red"}">${sign}${mp.returnPct.toFixed(2)}%</span>`);
        }
        if (mp.gain != null) {
          metrics.push(`Gain: +Rs ${mp.gain.toFixed(2)} Cr`);
        }
        if (mp.goldWeightKg != null) {
          metrics.push(`Gold: ${mp.goldWeightKg} kg`);
        }
        if (mp.silverWeightKg != null) {
          metrics.push(`Silver: ${mp.silverWeightKg} kg`);
        }
        if (mp.superPickerCount != null) {
          metrics.push(`Super Picks: ${mp.superPickerCount}`);
        }
        if (mp.stockReturnPct != null) {
          metrics.push(`Best Stock: +${mp.stockReturnPct.toFixed(1)}%`);
        }

        const metricsHtml = metrics.length
          ? `<div class="result-metrics">${metrics.join(" &middot; ")}</div>`
          : "";

        card.innerHTML = `
          <div class="result-header">
            ${mp.party ? `<span class="card-tag ${mp.party.toLowerCase().replace(/[^a-z]/g,'')}">${mp.party}</span>` : ""}
            <span class="result-name" style="font-family:'Playfair Display',serif; font-weight:700">${mp.name}</span>
          </div>
          ${mp.constituency ? `<span class="result-constituency">${mp.constituency}</span>` : ""}
          ${metricsHtml}
        `;
        searchResults.appendChild(card);
      });
    }

    /**
     * Simple debounce utility.
     * @param {Function} fn   — the function to debounce
     * @param {number}   ms   — delay in milliseconds
     * @returns {Function}
     */
    function debounce(fn, ms) {
      let timer;
      return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), ms);
      };
    }

    /**
     * Core search handler — filters the pre-built index by name substring.
     */
    function handleSearch() {
      const query = searchInput.value.trim().toLowerCase();

      if (!query) {
        renderSearchResults([], "");
        return;
      }

      const matches = searchIndex.filter(mp =>
        mp.name.toLowerCase().includes(query)
      );

      renderSearchResults(matches, query);
    }

    // Attach debounced listener (200ms)
    searchInput.addEventListener("input", debounce(handleSearch, 200));

    // Show default placeholder text on load
    renderSearchResults([], "");
  }

  // ═══════════════════ CHAPTER 5: PIE CHART RENDERING ═══════════════════
  
  function getSlicePath(cx, cy, r, startPct, endPct) {
    if (endPct - startPct >= 99.99) {
      endPct = 99.99;
    }
    const startAngle = (startPct / 100) * 2 * Math.PI;
    const endAngle = (endPct / 100) * 2 * Math.PI;
    
    const x1 = cx + r * Math.cos(startAngle);
    const y1 = cy + r * Math.sin(startAngle);
    const x2 = cx + r * Math.cos(endAngle);
    const y2 = cy + r * Math.sin(endAngle);
    
    const largeArcFlag = (endPct - startPct > 50) ? 1 : 0;
    
    return `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
  }

  function renderDonutChart(svgId, legendId, centerLabelId, data, categoryTitle, totalAumText) {
    const svg = document.getElementById(svgId);
    const legend = document.getElementById(legendId);
    const centerLabel = document.getElementById(centerLabelId);
    
    if (!svg || !legend || !centerLabel) return;
    
    svg.innerHTML = "";
    legend.innerHTML = "";
    
    let accumulatedPct = 0;
    const cx = 180;
    const cy = 180;
    const r = 150;
    
    const sliceElements = [];
    const legendElements = [];
    
    data.forEach((item, index) => {
      const startPct = accumulatedPct;
      const endPct = accumulatedPct + item.pct;
      accumulatedPct += item.pct;
      
      const pathD = getSlicePath(cx, cy, r, startPct, endPct);
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", pathD);
      path.setAttribute("fill", item.color);
      path.setAttribute("class", "pie-slice");
      svg.appendChild(path);
      sliceElements.push(path);
      
      const legendItem = document.createElement("div");
      legendItem.className = "legend-item";
      legendItem.innerHTML = `
        <div class="legend-swatch" style="background-color: ${item.color}"></div>
        <div class="legend-label" title="${item.name}">${item.label}</div>
        <div class="legend-val">₹${item.aumCr.toFixed(2)} Cr</div>
        <div class="legend-pct">${item.pct.toFixed(1)}%</div>
      `;
      legend.appendChild(legendItem);
      legendElements.push(legendItem);
    });
    
    const centerCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    centerCircle.setAttribute("cx", cx);
    centerCircle.setAttribute("cy", cy);
    centerCircle.setAttribute("r", "100");
    centerCircle.setAttribute("fill", "var(--bg)");
    centerCircle.style.pointerEvents = "none";
    svg.appendChild(centerCircle);
    
    function updateCenter(title, sub) {
      const titleEl = centerLabel.querySelector(".center-title");
      const subEl = centerLabel.querySelector(".center-sub");
      if (titleEl && subEl) {
        titleEl.textContent = title;
        subEl.textContent = sub;
        titleEl.style.fontSize = title.length > 12 ? "0.95rem" : "1.2rem";
      }
    }
    
    function resetCenter() {
      updateCenter(categoryTitle, totalAumText);
    }
    
    function highlightItem(targetIndex) {
      sliceElements.forEach((path, idx) => {
        if (idx === targetIndex) {
          path.classList.add("is-highlighted");
          path.classList.remove("is-dimmed");
        } else {
          path.classList.remove("is-highlighted");
          path.classList.add("is-dimmed");
        }
      });
      
      legendElements.forEach((item, idx) => {
        if (idx === targetIndex) {
          item.classList.add("is-highlighted");
        } else {
          item.classList.remove("is-highlighted");
        }
      });
      
      const activeItem = data[targetIndex];
      updateCenter(activeItem.label, `₹${activeItem.aumCr.toFixed(2)} Cr (${activeItem.pct.toFixed(1)}%)`);
    }
    
    function clearHighlight() {
      sliceElements.forEach(path => {
        path.classList.remove("is-highlighted");
        path.classList.remove("is-dimmed");
      });
      
      legendElements.forEach(item => {
        item.classList.remove("is-highlighted");
      });
      
      resetCenter();
    }
    
    sliceElements.forEach((path, idx) => {
      path.addEventListener("mouseenter", () => highlightItem(idx));
      path.addEventListener("mouseleave", clearHighlight);
    });
    
    legendElements.forEach((item, idx) => {
      item.addEventListener("mouseenter", () => highlightItem(idx));
      item.addEventListener("mouseleave", clearHighlight);
    });
    
    resetCenter();
  }

  // Initialize charts
  if (window.NETA_DATA && window.NETA_DATA.mpStockIndex && window.NETA_DATA.mpFundBasket) {
    renderDonutChart(
      "stock-pie-chart",
      "stock-legend",
      "stock-center-label",
      window.NETA_DATA.mpStockIndex,
      "Stocks",
      "₹72.8 Cr"
    );
    renderDonutChart(
      "fund-pie-chart",
      "fund-legend",
      "fund-center-label",
      window.NETA_DATA.mpFundBasket,
      "Funds",
      "₹45.0 Cr"
    );
  }


  // =====================================================================
  //  CH.6 — 3D ZDOG COINS (gold + silver, auto-rotating, drag-to-spin)
  // =====================================================================
  if (typeof window.Zdog !== "undefined") {
    const Zdog = window.Zdog;

    /**
     * Build a single 3D faceted coin inside the given canvas element.
     *
     * Architecture mirrors the Zdog diamond demo: a polyhedron assembled
     * from flat polygonal facets with alternating shade pairs (A/B) so
     * that each face catches "light" differently as the coin rotates.
     *
     * Geometry: 12-sided prism (SIDES = 12).
     *   • Top + bottom face   → solid polygons, lightest tone
     *   • Beveled rim         → 12 short quads sloping from the face down
     *                           to the side wall (alternating shades)
     *   • Side wall           → 12 vertical quads (alternating darker
     *                           shades — these are the rim panels)
     * Slowly auto-rotates on Y; drag to spin manually.
     */
    function buildCoin(canvas, kind) {
      const isGold = kind === "gold";

      // Five-tone palette so adjacent facets always differ: face is the
      // brightest, then a pair of bevel tones, then a pair of darker
      // rim tones for the vertical side panels.
      const palette = isGold ? {
        face:   "#f0c84a",
        bevelA: "#dfb02a",
        bevelB: "#b88a00",
        sideA:  "#8a5f10",
        sideB:  "#5a3a00"
      } : {
        face:   "#f0f0f0",
        bevelA: "#c8c8c8",
        bevelB: "#a4a4a4",
        sideA:  "#787878",
        sideB:  "#4a4a4a"
      };

      const SIDES        = 12;
      const RADIUS_OUT   = 0.82;   // outer rim radius
      const RADIUS_IN    = 0.70;   // top/bottom face radius (smaller → bevel)
      const HALF_H_OUT   = 0.08;   // half-thickness at the rim
      const HALF_H_IN    = 0.10;   // half-thickness at the inner face
      const TAU          = Zdog.TAU;

      // Match canvas pixel resolution to CSS size × devicePixelRatio
      const dpr  = window.devicePixelRatio || 1;
      const cssW = canvas.getBoundingClientRect().width || 100;
      canvas.width  = cssW * dpr;
      canvas.height = cssW * dpr;

      let spinning = true;

      const illo = new Zdog.Illustration({
        element:    canvas,
        dragRotate: true,
        rotate:     { x: -0.42 },                // tilt so rim + facets visible
        scale:      cssW * dpr * 0.45,
        onDragStart() { spinning = false; }
      });

      const coin = new Zdog.Anchor({ addTo: illo });

      // Helper: point on a regular polygon at (radius, y)
      const pt = (i, r, y) => {
        const a = (i / SIDES) * TAU;
        return { x: Math.cos(a) * r, y, z: Math.sin(a) * r };
      };

      // ── Top face (solid polygon, lifted slightly above bevel apex) ──
      new Zdog.Shape({
        addTo:    coin,
        path:     Array.from({ length: SIDES }, (_, i) => pt(i, RADIUS_IN, -HALF_H_IN)),
        closed:   true,
        stroke:   false,
        fill:     true,
        color:    palette.face,
        backface: palette.face
      });

      // ── Bottom face ─────────────────────────────────────────────────
      new Zdog.Shape({
        addTo:    coin,
        path:     Array.from({ length: SIDES }, (_, i) => pt(i, RADIUS_IN, HALF_H_IN)),
        closed:   true,
        stroke:   false,
        fill:     true,
        color:    palette.face,
        backface: palette.face
      });

      // ── Facets: top bevel + side wall + bottom bevel per panel ──────
      for (let i = 0; i < SIDES; i++) {
        const even = i % 2 === 0;
        const a1   = pt(i,     RADIUS_IN,  -HALF_H_IN);
        const a2   = pt(i + 1, RADIUS_IN,  -HALF_H_IN);
        const b1   = pt(i,     RADIUS_OUT, -HALF_H_OUT);
        const b2   = pt(i + 1, RADIUS_OUT, -HALF_H_OUT);
        const c1   = pt(i,     RADIUS_OUT,  HALF_H_OUT);
        const c2   = pt(i + 1, RADIUS_OUT,  HALF_H_OUT);
        const d1   = pt(i,     RADIUS_IN,   HALF_H_IN);
        const d2   = pt(i + 1, RADIUS_IN,   HALF_H_IN);

        // Top bevel quad (slope from top face down/out to the rim)
        new Zdog.Shape({
          addTo:    coin,
          path:     [a1, a2, b2, b1],
          closed:   true,
          stroke:   false,
          fill:     true,
          color:    even ? palette.bevelA : palette.bevelB,
          backface: even ? palette.bevelA : palette.bevelB
        });

        // Vertical side panel
        new Zdog.Shape({
          addTo:    coin,
          path:     [b1, b2, c2, c1],
          closed:   true,
          stroke:   false,
          fill:     true,
          color:    even ? palette.sideA : palette.sideB,
          backface: even ? palette.sideA : palette.sideB
        });

        // Bottom bevel quad (mirror of top)
        new Zdog.Shape({
          addTo:    coin,
          path:     [c1, c2, d2, d1],
          closed:   true,
          stroke:   false,
          fill:     true,
          color:    even ? palette.bevelB : palette.bevelA,
          backface: even ? palette.bevelB : palette.bevelA
        });
      }

      // ── Decorative ornament on the top face ─────────────────────────
      // Just above the top face plane so the embossing is visible:
      const TOP_DECO_Y  = -HALF_H_IN - 0.002;
      const FACE_ROTATE = { x: TAU / 4 };  // lay flat on the top face

      // Raised inner ring (defines the decorated medallion area)
      new Zdog.Ellipse({
        addTo:     coin,
        diameter:  RADIUS_IN * 1.7,
        color:     palette.sideA,
        stroke:    0.018,
        fill:      false,
        translate: { y: TOP_DECO_Y },
        rotate:    FACE_ROTATE
      });

      // Beaded border: 18 small filled dots around the inner ring
      const BEADS    = 18;
      const beadR    = RADIUS_IN * 0.78;
      const beadSize = 0.045;
      for (let i = 0; i < BEADS; i++) {
        const a = (i / BEADS) * TAU;
        new Zdog.Ellipse({
          addTo:     coin,
          diameter:  beadSize,
          color:     palette.bevelB,
          stroke:    0.012,
          fill:      true,
          translate: { x: Math.cos(a) * beadR, y: TOP_DECO_Y - 0.001, z: Math.sin(a) * beadR },
          rotate:    FACE_ROTATE
        });
      }

      // Eight-pointed star (Star of Lakshmi) made of two overlapped squares
      // rotated 45° apart. Sits on the upper half of the medallion.
      const starCenterZ = -RADIUS_IN * 0.05;     // sits slightly above middle
      const starR       = RADIUS_IN * 0.32;
      for (let twist = 0; twist < 2; twist++) {
        const rot = (twist * TAU) / 8;           // 0 then 45°
        const square = [];
        for (let k = 0; k < 4; k++) {
          const a = rot + (k / 4) * TAU;
          square.push({
            x: Math.cos(a) * starR,
            y: TOP_DECO_Y - 0.003,
            z: starCenterZ + Math.sin(a) * starR
          });
        }
        new Zdog.Shape({
          addTo:    coin,
          path:     square,
          closed:   true,
          stroke:   false,
          fill:     true,
          color:    twist === 0 ? palette.face   : palette.bevelA,
          backface: twist === 0 ? palette.face   : palette.bevelA
        });
      }

      // Centre boss disc
      new Zdog.Ellipse({
        addTo:     coin,
        diameter:  0.16,
        color:     palette.bevelB,
        stroke:    0.045,
        fill:      true,
        translate: { x: 0, y: TOP_DECO_Y - 0.005, z: starCenterZ },
        rotate:    FACE_ROTATE
      });

      // Wave lines below the star (evoke the rippling water motif).
      // Three slightly-curved horizontal arcs built from polyline points.
      const WAVE_BASE_Z = RADIUS_IN * 0.30;
      for (let line = 0; line < 3; line++) {
        const zPos    = WAVE_BASE_Z + line * 0.10;
        const halfW   = RADIUS_IN * (0.55 - line * 0.07);
        const points  = [];
        const STEPS   = 9;
        for (let s = 0; s <= STEPS; s++) {
          const t = s / STEPS;
          const x = -halfW + t * (halfW * 2);
          // small sinusoidal ripple superimposed on the line
          const z = zPos + Math.sin(t * TAU * 1.5) * 0.018;
          points.push({ x, y: TOP_DECO_Y - 0.003, z });
        }
        new Zdog.Shape({
          addTo:  coin,
          path:   points,
          closed: false,
          stroke: 0.022,
          color:  palette.sideA,
          fill:   false
        });
      }

      // ── Animate ─────────────────────────────────────────────────────
      function tick() {
        if (spinning) illo.rotate.y += 0.01;
        illo.updateRenderGraph();
        requestAnimationFrame(tick);
      }
      tick();
    }

    // Wait one tick so each canvas has its CSS-sized box, then init.
    requestAnimationFrame(() => {
      document.querySelectorAll("canvas[data-coin]").forEach(c => {
        try { buildCoin(c, c.dataset.coin); }
        catch (err) { console.warn("[coin] init failed", err); }
      });
    });
  }

});
