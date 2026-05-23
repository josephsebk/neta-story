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
  // 2. CHAPTER 1 — ANIMATED HORIZONTAL BAR CHART (Index Comparison)
  // =====================================================================
  const chartContainer = document.getElementById("nifty-comparison-chart");

  /**
   * Build the horizontal bar rows from `NETA_DATA.indices`.
   * Bars start at width:0 and animate in via IntersectionObserver.
   */
  function renderComparisonChart() {
    if (!chartContainer) return;
    chartContainer.innerHTML = "";

    // The largest value in the dataset drives proportional sizing
    const maxVal = 38.71;

    data.indices.forEach(item => {
      const displayPct =
        (item.returnPct >= 0 ? "+" : "") + item.returnPct.toFixed(2) + "%";

      // Calculate the target width as a percentage of the max bar
      const targetWidth = ((Math.abs(item.returnPct) / maxVal) * 100).toFixed(2);

      const row = document.createElement("div");
      row.className = "bar-row";
      row.innerHTML = `
        <div class="bar-label">
          <span>${item.label}</span>
          <span class="bar-label-val" style="color:${item.color}">${displayPct}</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" style="background:${item.color}; width:0%" data-target="${targetWidth}"></div>
        </div>
      `;
      chartContainer.appendChild(row);
    });
  }

  renderComparisonChart();

  // Use IntersectionObserver so bars animate only when scrolled into view
  if (chartContainer) {
    const chartObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            // Animate every bar-fill to its target width
            chartContainer.querySelectorAll(".bar-fill").forEach(bar => {
              const target = parseFloat(bar.dataset.target) || 0;
              // Guarantee a minimum visible width so short bars are still legible
              bar.style.width = Math.max(8, target) + "%";
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
  // 3. CHAPTER 2 — TABBED LEADERBOARD CARDS
  // =====================================================================
  const leaderboardCards = document.getElementById("leaderboard-cards");
  const tabButtons = document.querySelectorAll(".selector-tabs .tab-btn");

  /**
   * Render a leaderboard tab.
   * @param {string} tabKey — one of 'bestReturn', 'worstReturn', 'bestGainers'
   */
  function renderLeaderboard(tabKey) {
    if (!leaderboardCards) return;
    leaderboardCards.innerHTML = "";

    const list = data.leaderboards[tabKey];
    if (!list) return;

    list.forEach(item => {
      const isGainer = tabKey === "bestGainers";

      // For bestGainers show the absolute gain in Rs Crore;
      // otherwise show the return percentage
      const valueLabel = isGainer
        ? `+Rs ${item.gain.toFixed(2)} Cr`
        : (item.returnPct >= 0 ? "+" : "") + item.returnPct.toFixed(2) + "%";

      const valueColorClass = isGainer || item.returnPct >= 0 ? "green" : "red";
      const returnLabel = isGainer ? "Capital Gain" : "Net Return";

      // Pad the rank with a leading zero for single digits
      const rankStr = "#" + String(item.rank).padStart(2, "0");

      const initials = item.name.split(" ").filter(w => /^[A-Za-z]/.test(w)).slice(0, 2).map(w => w[0].toUpperCase()).join("");

      const card = document.createElement("div");
      card.className = "leaderboard-card";
      card.innerHTML = `
        <div class="card-rank">${rankStr}</div>
        <div class="card-avatar">${initials}</div>
        <div class="card-header-info">
          <span class="card-tag ${item.party.toLowerCase().replace(/[^a-z]/g,'')}">${item.party}</span>
          <h4 class="card-name">${item.name}</h4>
          <span class="card-constituency">${item.constituency}</span>
        </div>
        <div class="card-stats">
          <div class="stat-item">
            <span class="num">Rs ${item.base.toFixed(2)} Cr</span>
            <span class="label">Base</span>
          </div>
          <div class="stat-item">
            <span class="num ${valueColorClass}">${valueLabel}</span>
            <span class="label">${returnLabel}</span>
          </div>
        </div>
        <p class="card-driver">${item.driver}</p>
      `;
      leaderboardCards.appendChild(card);
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

});
