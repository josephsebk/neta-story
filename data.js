// Lok Sabha 2024 MP Investment Performance Data Story Dataset
window.NETA_DATA = {
  nifty: {
    baseLevel: 22888.15,
    currentLevel: 23719.30,
    returnPct: 3.63
  },
  indices: [
    { label: "Nifty 50 Index", short: "Nifty 50", returnPct: 3.63, color: "#5a524a" },
    { label: "MP Returns (ex Promoter) — Weighted", short: "MPs (weighted)", returnPct: 6.48, color: "#7a8a3a" },
    { label: "MP Returns (ex Promoter) — Simple Avg", short: "MPs (simple avg)", returnPct: 7.92, color: "#3a6a3a" },
    { label: "Total Combined (inc. Promoters)", short: "Combined w/ promoters", returnPct: 38.71, color: "#b88a00" }
  ],
  aumBreakdown: {
    discretionary: {
      equity: { base: 108.32, current: 112.88, returnPct: 4.21 },
      fund: { base: 88.48, current: 96.68, returnPct: 9.27 },
      combined: { base: 196.80, current: 209.56, returnPct: 6.48 }
    },
    full: {
      equity: { base: 2831.00, current: 3954.00, returnPct: 39.63 },
      fund: { base: 88.48, current: 96.68, returnPct: 9.27 },
      combined: { base: 2919.80, current: 4050.48, returnPct: 38.71 }
    }
  },
  leaderboards: {
    bestReturn: [
      { rank: 1, name: "Shankar Lalwani", party: "BJP", constituency: "Indore", base: 0.23, current: 0.34, returnPct: 47.93, driver: "Concentrated domestic equity selection." },
      { rank: 2, name: "Adv Adoor Prakash", party: "INC", constituency: "Attingal", base: 1.59, current: 2.16, returnPct: 36.34, driver: "Mid-cap equity growth." },
      { rank: 3, name: "Pathan Yusuf", party: "AITC", constituency: "Baharampur", base: 1.67, current: 2.17, returnPct: 29.48, driver: "Well-timed equity positions." },
      { rank: 4, name: "C R Patil", party: "BJP", constituency: "Navsari", base: 0.37, current: 0.47, returnPct: 26.16, driver: "Mixed portfolio (5 stocks, 6 MFs)." },
      { rank: 5, name: "Ve Vaithilingam", party: "INC", constituency: "Puducherry", base: 0.20, current: 0.25, returnPct: 24.77, driver: "High-performing domestic equity selection." }
    ],
    worstReturn: [
      { rank: 1, name: "Konda Vishweshwar Reddy", party: "BJP", constituency: "Chevella", base: 2.19, current: 1.44, returnPct: -34.23, driver: "GVK Power & Infrastructure (-70.8%)." },
      { rank: 2, name: "Nishikant Dubey", party: "BJP", constituency: "Godda", base: 2.66, current: 2.32, returnPct: -13.01, driver: "Mixed equity and mutual fund setbacks." },
      { rank: 3, name: "Hasmukhbhai Patel", party: "BJP", constituency: "Ahmedabad East", base: 0.12, current: 0.11, returnPct: -6.47, driver: "Dragged down by GVK Power (-70.8%)." },
      { rank: 4, name: "Mukeshkumar Dalal", party: "BJP", constituency: "Surat", base: 0.12, current: 0.11, returnPct: -5.63, driver: "Eastern Silk wiped to 0 via NCLT restructuring." },
      { rank: 5, name: "Shatrughan Prasad Sinha", party: "AITC", constituency: "Asansol", base: 3.21, current: 3.06, returnPct: -4.55, driver: "General market drops in minor holdings." }
    ],
    bestGainers: [
      { rank: 1, name: "Anurag Sharma", party: "BJP", constituency: "Jhansi", base: 17.65, gain: 2.06, returnPct: 11.70, driver: "Massive balanced public assets." },
      { rank: 2, name: "Amit Shah", party: "BJP", constituency: "Gandhinagar", base: 32.63, gain: 1.76, returnPct: 5.39, driver: "Extremely diversified 150+ mid-cap selection." },
      { rank: 3, name: "Ramasahayam Raghuram Reddy", party: "INC", constituency: "Khammam", base: 11.04, gain: 1.26, returnPct: 11.44, driver: "Strong equity portfolio returns." },
      { rank: 4, name: "Ravi Shankar Prasad", party: "BJP", constituency: "Patna Sahib", base: 8.22, gain: 1.18, returnPct: 14.35, driver: "Kotak Emerging FOF outperformance." },
      { rank: 5, name: "Supriya Sule", party: "NCP-SP", constituency: "Baramati", base: 12.04, gain: 0.76, returnPct: 6.33, driver: "Consistent domestic equity returns." }
    ]
  },
  spouseVsSelf: {
    self: { label: "Self / HUF", returnPct: 6.35, avgReturnPct: 7.25, base: 158.82, mps: 92 },
    spouse: { label: "Spouse / Dependent", returnPct: 6.81, avgReturnPct: 8.76, base: 49.98, mps: 54 }
  },
  bestStocks: [
    { rank: 1, name: "Amit Shah", party: "BJP", stock: "Tera Software Limited", ticker: "TERASOFT", baseVal: 50910, curVal: 272470, returnPct: 435.2, owner: "Self" },
    { rank: 2, name: "Amit Shah", party: "BJP", stock: "Garware Hi-Tech Films", ticker: "GRWRHITECH", baseVal: 68798, curVal: 236870, returnPct: 244.3, owner: "Self" },
    { rank: 3, name: "Amit Shah", party: "BJP", stock: "Hitachi Energy India", ticker: "POWERINDIA", baseVal: 1577000, curVal: 5373000, returnPct: 240.8, owner: "Self" },
    { rank: 4, name: "Piyush Goyal", party: "BJP", stock: "One 97 Communications", ticker: "PAYTM", baseVal: 547000, curVal: 1776000, returnPct: 224.5, owner: "Self" },
    { rank: 5, name: "Dr. Sharmila Sarkar", party: "AITC", stock: "One 97 Communications", ticker: "PAYTM", baseVal: 4500, curVal: 14602, returnPct: 224.5, owner: "Self" },
    { rank: 6, name: "Brijendra Singh Ola", party: "INC", stock: "Laurus Labs Limited", ticker: "LAURUSLABS", baseVal: 41200, curVal: 125000, returnPct: 202.5, owner: "Self" },
    { rank: 7, name: "Brijendra Singh Ola", party: "INC", stock: "Laurus Labs Limited", ticker: "LAURUSLABS", baseVal: 41200, curVal: 125000, returnPct: 202.5, owner: "Spouse" },
    { rank: 8, name: "Amit Shah", party: "BJP", stock: "Mcleod Russel India", ticker: "MCLEODRUSS", baseVal: 4343, curVal: 12315, returnPct: 183.6, owner: "Self" },
    { rank: 9, name: "Dr. Sharmila Sarkar", party: "AITC", stock: "Deepak Fertilizers", ticker: "DEEPAKFERT", baseVal: 202000, curVal: 553000, returnPct: 174.0, owner: "Self" },
    { rank: 10, name: "Amit Shah", party: "BJP", stock: "S.J.S. Enterprises Limited", ticker: "SJS", baseVal: 16397, curVal: 44622, returnPct: 172.1, owner: "Spouse" }
  ],
  superPickers: [
    { name: "Amit Shah", party: "BJP", count: 30, primaryDriver: "Diverse mid-cap selections" },
    { name: "Brijendra Singh Ola", party: "INC", count: 14, primaryDriver: "Laurus Labs and chemical picks" },
    { name: "Rachna Banerjee", party: "AITC", count: 12, primaryDriver: "Balanced FOFs and mid-caps" },
    { name: "Arun Nehru", party: "DMK", count: 9, primaryDriver: "Strong south-focused equities" },
    { name: "Supriya Sule", party: "NCP-SP", count: 8, primaryDriver: "Steady blue-chips" },
    { name: "Shatrughan Prasad Sinha", party: "AITC", count: 5, primaryDriver: "Consumer goods equities" },
    { name: "Piyush Goyal", party: "BJP", count: 4, primaryDriver: "Multi-commodity & PayTM rebounds" },
    { name: "Dr. Sharmila Sarkar", party: "AITC", count: 4, primaryDriver: "PayTM & fertilizer picks" }
  ],
  partyPerformance: [
    { name: "TDP", count: 6, aum: 3.94, returnPct: 11.40, avgReturnPct: 7.12, note: "Solid mid-cap growth." },
    { name: "AITC", count: 10, aum: 16.49, returnPct: 7.26, avgReturnPct: 6.60, note: "Consistent mid-cap selections." },
    { name: "INC", count: 20, aum: 51.78, returnPct: 6.78, avgReturnPct: 12.34, note: "Excellent simple avg (Raymond demerger correction)." },
    { name: "SP", count: 2, aum: 0.07, returnPct: 6.43, avgReturnPct: 21.86, note: "High avg returns on tiny portfolios." },
    { name: "NCP-SP", count: 4, aum: 12.85, returnPct: 6.33, avgReturnPct: 6.77, note: "Anchored by Supriya Sule's holdings." },
    { name: "BJP", count: 51, aum: 121.85, returnPct: 6.21, avgReturnPct: 5.94, note: "Massive institutional-grade diversification." },
    { name: "AAP", count: 2, aum: 0.64, returnPct: 5.62, avgReturnPct: 5.55, note: "Average performers, beating Nifty." },
    { name: "DMK", count: 2, aum: 1.69, returnPct: 0.27, avgReturnPct: 7.39, note: "Flat aggregate, decent simple average." }
  ],
  preciousMetals: {
    total: { base: 294.11, current: 654.36, returnPct: 122.49, gain: 360.25 },
    gold: { base: 281.22, current: 614.96, returnPct: 118.67, weight: 854.65, backCalculated: 30.40 },
    silver: { base: 12.89, current: 39.40, returnPct: 205.70, weight: 5063.93, backCalculated: 66.76 },
    goldPrices: { base: 7293, current: 15948, returnPct: 118.67 },
    silverPrices: { base: 96.50, current: 295.00, returnPct: 205.70 }
  },
  topGoldHolders: [
    { rank: 1, name: "Naveen Jindal", party: "BJP", constituency: "Kurukshetra", base: 43.15, current: 94.36, weight: 22103.3, note: "Premium diamond-studded gold & heritage jewelry." },
    { rank: 2, name: "C.M. Ramesh", party: "BJP", constituency: "Anakapalle", base: 9.16, current: 20.03, weight: 15110.0, note: "Disclosed across multiple family assets." },
    { rank: 3, name: "Sribharat Mathukumili", party: "TDP", constituency: "Visakhapatnam", base: 7.62, current: 16.66, weight: 12435.1, note: "Major institutional family gold holdings." },
    { rank: 4, name: "Chhatrapati Shahu Shahaji", party: "INC", constituency: "Kolhapur", base: 5.53, current: 12.09, weight: 9043.7, note: "Royal family heirloom collection." },
    { rank: 5, name: "Kangana Ranaut", party: "BJP", constituency: "Mandi", base: 5.00, current: 10.93, weight: 6700.0, note: "Concentrated designer & wedding jewelry." }
  ],
  topSilverHolders: [
    { rank: 1, name: "Sribharat Mathukumili", party: "TDP", constituency: "Visakhapatnam", base: 0.88, current: 2.68, weight: 104300, note: "Heavy collection of solid silver items and utensils." },
    { rank: 2, name: "Chhatrapati Shahu Shahaji", party: "INC", constituency: "Kolhapur", base: 0.72, current: 2.20, weight: 102700, note: "Royal family silver articles and utensils." },
    { rank: 3, name: "Mala Rajya Lakshmi Shah", party: "BJP", constituency: "Tehri Garhwal", base: 0.58, current: 1.76, weight: 140336, note: "High-volume heirloom and silver coin collection." },
    { rank: 4, name: "Kangana Ranaut", party: "BJP", constituency: "Mandi", base: 0.50, current: 1.53, weight: 60000, note: "High-value designer silver articles and ornaments." },
    { rank: 5, name: "Anurag Sharma", party: "BJP", constituency: "Jhansi", base: 0.47, current: 1.43, weight: 72830, note: "Large family silver articles and coin treasury." }
  ],
  partyGoldSilver: [
    { rank: "-", name: "NDA Coalition (BJP + TDP + JD(U) + SHS-Shinde + LJP-RV + JD(S) + JSP)", count: 235, base: 198.90, current: 442.25, returnPct: 122.3, goldWeight: 246.58, silverWeight: 1299.49 },
    { rank: 1, name: "BJP", count: 199, base: 168.45, current: 374.25, returnPct: 122.2, goldWeight: 201.07, silverWeight: 1085.47 },
    { rank: 2, name: "INC", count: 81, base: 43.98, current: 98.14, returnPct: 123.1, goldWeight: 109.90, silverWeight: 3479.69 },
    { rank: 3, name: "TDP", count: 13, base: 19.53, current: 43.70, returnPct: 123.7, goldWeight: 28.95, silverWeight: 143.91 },
    { rank: 4, name: "DMK", count: 18, base: 14.86, current: 33.10, returnPct: 122.7, goldWeight: 439.69, silverWeight: 86.02 }, // Skewed note
    { rank: 5, name: "SP", count: 25, base: 6.97, current: 15.40, returnPct: 121.0, goldWeight: 10.33, silverWeight: 24.04 },
    { rank: 6, name: "NCP-SP", count: 7, base: 5.56, current: 12.40, returnPct: 122.9, goldWeight: 9.90, silverWeight: 46.45 },
    { rank: 7, name: "JD(S)", count: 2, base: 3.47, current: 7.79, returnPct: 124.4, goldWeight: 5.37, silverWeight: 29.50 },
    { rank: 8, name: "SS(UBT)", count: 7, base: 3.47, current: 7.71, returnPct: 122.3, goldWeight: 5.32, silverWeight: 21.00 },
    { rank: 9, name: "AITC", count: 19, base: 3.46, current: 7.70, returnPct: 122.3, goldWeight: 6.16, silverWeight: 19.23 }
  ],
  mixedSeparations: [
    { name: "Amit Shah (BJP)", mixedStr: "Gold -770gm (Inheritance) Diamond Jewelry (7 Carate) Silver (25Kg) @ Rs 64.12 Lakh", separated: "25.00 kg Silver + 770g Gold. Combined with spouse (1.62 kg Gold, 63ct Diamond) & self-acquired gold, total family assets audited at 2.55 kg Gold, 25.00 kg Silver, and 70 carats of Diamonds." },
    { name: "Piyush Goyal (BJP)", mixedStr: "Three distinct multi-commodity entries worth combined Rs 7.81 Crore", separated: "Reconciled to reveal 9.05 kg of Gold, 25.03 kg of Silver, and 890.41 carats of Diamonds across family assets." },
    { name: "Akhilesh Yadav (SP)", mixedStr: "Gold Jewellery-2774.674,gm 203gm Moti, 127.75 Caret Diamond @ Rs 59.77 Lakh", separated: "Recovered 2.77 kg of Gold (Gold Jewellery) and 127.75 carats of Diamonds (previously mis-categorized as 203g Moti)." },
    { name: "Dharmendra Pradhan (BJP)", mixedStr: "Gold 200gm Silver- 2.5kg & Gold/Silver 500gm & 10kg @ Rs 48.50 Lakh", separated: "Separated to reveal a total of 700g of Gold and 12.50 kg of Silver." },
    { name: "Kuldeep Indora (INC)", mixedStr: "200g Gold + 3.25kg Silver & 140g Gold + 3.25kg Silver @ Rs 21.00 Lakh", separated: "Separated to reveal 340g of Gold and 6.50 kg of Silver." }
  ],
  weightDistortions: [
    { name: "Dr. Kalanidhi Veeraswamy (DMK)", claimed: "419.47 kg Gold", reality: "419.47 grams Gold (Value declared: Rs 24.52 Lakh). A transcription error scaled his weight 1,000x in raw datasets." },
    { name: "Sunil Bose (INC)", claimed: "3,200 kg Silver", reality: "3,200 grams / 3.2 kg Silver (Value declared: Rs 2.30 Lakh). Typographical error in affidavit listed 'kgs' instead of grams." },
    { name: "C.M. Ramesh (BJP)", claimed: "15.11 grams Gold", reality: "15.11 kg Gold (Value declared: Rs 9.16 Crore). Listed as 'Kg 6.92 Grams' and 'Kg 8.19 Grams' which parsers read as raw grams." }
  ],
  // Comprehensive searchable index — all unique MPs across the investigation
  searchIndex: [
    { name: "Amit Shah", party: "BJP", constituency: "Gandhinagar", returnPct: 5.39, baseCr: 32.63, gainCr: 1.76, superPickerCount: 30, goldKg: 2.55, silverKg: 25.00, topStock: "Tera Software (+435.2%)" },
    { name: "Shankar Lalwani", party: "BJP", constituency: "Indore", returnPct: 47.93, baseCr: 0.23 },
    { name: "Adv Adoor Prakash", party: "INC", constituency: "Attingal", returnPct: 36.34, baseCr: 1.59 },
    { name: "Pathan Yusuf", party: "AITC", constituency: "Baharampur", returnPct: 29.48, baseCr: 1.67 },
    { name: "C R Patil", party: "BJP", constituency: "Navsari", returnPct: 26.16, baseCr: 0.37, goldKg: 4.76, silverKg: 43.32 },
    { name: "Ve Vaithilingam", party: "INC", constituency: "Puducherry", returnPct: 24.77, baseCr: 0.20 },
    { name: "Konda Vishweshwar Reddy", party: "BJP", constituency: "Chevella", returnPct: -34.23, baseCr: 2.19, note: "GVK Power drag. Promoter: Apollo Hospitals excluded." },
    { name: "Nishikant Dubey", party: "BJP", constituency: "Godda", returnPct: -13.01, baseCr: 2.66 },
    { name: "Hasmukhbhai Patel", party: "BJP", constituency: "Ahmedabad East", returnPct: -6.47, baseCr: 0.12 },
    { name: "Mukeshkumar Dalal", party: "BJP", constituency: "Surat", returnPct: -5.63, baseCr: 0.12, note: "Eastern Silk wiped to Rs 0 via NCLT." },
    { name: "Shatrughan Prasad Sinha", party: "AITC", constituency: "Asansol", returnPct: -4.55, baseCr: 3.21, superPickerCount: 5 },
    { name: "Anurag Sharma", party: "BJP", constituency: "Jhansi", returnPct: 11.70, baseCr: 17.65, gainCr: 2.06, silverKg: 72.83 },
    { name: "Ramasahayam Raghuram Reddy", party: "INC", constituency: "Khammam", returnPct: 11.44, baseCr: 11.04, gainCr: 1.26 },
    { name: "Ravi Shankar Prasad", party: "BJP", constituency: "Patna Sahib", returnPct: 14.35, baseCr: 8.22, gainCr: 1.18 },
    { name: "Supriya Sule", party: "NCP-SP", constituency: "Baramati", returnPct: 6.33, baseCr: 12.04, gainCr: 0.76, superPickerCount: 8, goldKg: 4.12 },
    { name: "Piyush Goyal", party: "BJP", constituency: "Mumbai North", superPickerCount: 4, goldKg: 9.05, silverKg: 25.03, topStock: "PayTM (+224.5%)" },
    { name: "Dr. Sharmila Sarkar", party: "AITC", constituency: "Kolkata Uttar", superPickerCount: 4, topStock: "PayTM (+224.5%)" },
    { name: "Brijendra Singh Ola", party: "INC", constituency: "Jhunjhunu", superPickerCount: 14, topStock: "Laurus Labs (+202.5%)" },
    { name: "Rachna Banerjee", party: "AITC", constituency: "Hooghly", superPickerCount: 12 },
    { name: "Arun Nehru", party: "DMK", constituency: "Perambalur", superPickerCount: 9 },
    { name: "Naveen Jindal", party: "BJP", constituency: "Kurukshetra", goldKg: 22.10, note: "Promoter: Jindal/JSW excluded from equity. Rs 43.15 Cr gold." },
    { name: "C.M. Ramesh", party: "BJP", constituency: "Anakapalle", goldKg: 15.11, note: "15.11 kg gold corrected from raw 15.11g." },
    { name: "Sribharat Mathukumili", party: "TDP", constituency: "Visakhapatnam", goldKg: 12.44, silverKg: 104.30 },
    { name: "Chhatrapati Shahu Shahaji", party: "INC", constituency: "Kolhapur", returnPct: 2.4, baseCr: 18.29, goldKg: 9.04, silverKg: 102.70, note: "Royal family heirloom collection." },
    { name: "Kangana Ranaut", party: "BJP", constituency: "Mandi", goldKg: 6.70, silverKg: 60.00 },
    { name: "Mala Rajya Lakshmi Shah", party: "BJP", constituency: "Tehri Garhwal", silverKg: 140.34 },
    { name: "Akhilesh Yadav", party: "SP", constituency: "Kannauj", goldKg: 2.77, note: "Gold weight recovered from mixed Moti category." },
    { name: "Dharmendra Pradhan", party: "BJP", constituency: "Sambalpur", goldKg: 0.70, silverKg: 12.50 },
    { name: "Baijayant Panda", party: "BJP", constituency: "Kendrapara", returnPct: -1.30, baseCr: 8.62, note: "Promoter: IMFA excluded." },
    { name: "Harsimrat Kaur Badal", party: "SAD", constituency: "Bathinda", note: "Rs 7.03 Cr in mixed precious metals." },
    { name: "Dr. Kalanidhi Veeraswamy", party: "DMK", constituency: "Chennai North", note: "419.47g gold corrected from raw 419.47 kg." },
    { name: "Sunil Bose", party: "INC", constituency: "Chamarajanagar", note: "3.2 kg silver corrected from raw 3,200 kg." },
    { name: "Kuldeep Indora", party: "INC", constituency: "Ganganagar", goldKg: 0.34, silverKg: 6.50 },
    { name: "Ravindra Shukla alias Ravi Kishan", party: "BJP", constituency: "Gorakhpur", returnPct: -41.46 }
  ],

  // ─────────────────────────────────────────────────────────────────────
  // What lawmakers prefer — Section 8 of the report (top by # of holders)
  // ─────────────────────────────────────────────────────────────────────
  preferredStocks: [
    { ticker: "RELIANCE",  name: "Reliance Industries",    domain: "ril.com",                       holders: 18, aumCr: 2.81, returnPct: -5.8  },
    { ticker: "HDFCBANK",  name: "HDFC Bank",              domain: "hdfcbank.com",                  holders: 15, aumCr: 3.33, returnPct:  1.9  },
    { ticker: "ITC",       name: "ITC",                    domain: "itcportal.com",                 holders: 14, aumCr: 2.17, returnPct: -20.7 },
    { ticker: "TATASTEEL", name: "Tata Steel",             domain: "tatasteel.com",                 holders: 12, aumCr: 1.06, returnPct:  24.9 },
    { ticker: "RPOWER",    name: "Reliance Power",         domain: "reliancepower.co.in",           holders: 12, aumCr: 0.07, returnPct:   8.4 },
    { ticker: "JIOFIN",    name: "Jio Financial Services", domain: "jiofinancialservices.com",      holders: 12, aumCr: 0.23, returnPct: -32.7 },
    { ticker: "ICICIBANK", name: "ICICI Bank",             domain: "icicibank.com",                 holders:  9, aumCr: 1.10, returnPct:  14.5 },
    { ticker: "INFY",      name: "Infosys",                domain: "infosys.com",                   holders:  9, aumCr: 1.44, returnPct: -14.7 },
    { ticker: "SBIN",      name: "State Bank of India",    domain: "sbi.co.in",                     holders:  9, aumCr: 2.78, returnPct:  19.2 },
    { ticker: "YESBANK",   name: "Yes Bank",               domain: "yesbank.in",                    holders:  9, aumCr: 0.17, returnPct:  -3.8 }
  ],
  preferredFunds: [
    { name: "ICICI Prudential MNC Fund",          short: "MNC Fund",                house: "ICICI Prudential", domain: "iciciprumf.com",     holders: 11, aumCr: 3.89, returnPct: 10.0 },
    { name: "Kotak Flexicap Fund",                short: "Flexicap",                house: "Kotak Mahindra",   domain: "kotakmf.com",        holders:  9, aumCr: 1.14, returnPct:  4.6 },
    { name: "HDFC Mid Cap Fund",                  short: "Mid Cap",                 house: "HDFC",             domain: "hdfcfund.com",       holders:  9, aumCr: 1.57, returnPct: 15.8 },
    { name: "Axis Small Cap Fund",                short: "Small Cap",               house: "Axis",             domain: "axismf.com",         holders:  8, aumCr: 0.40, returnPct: 13.6 },
    { name: "HDFC Flexi Cap Fund",                short: "Flexi Cap",               house: "HDFC",             domain: "hdfcfund.com",       holders:  7, aumCr: 4.07, returnPct: 12.1 },
    { name: "HDFC Small Cap Fund",                short: "Small Cap",               house: "HDFC",             domain: "hdfcfund.com",       holders:  6, aumCr: 2.23, returnPct:  6.7 },
    { name: "Mirae Asset Large Cap Fund",         short: "Large Cap",               house: "Mirae Asset",      domain: "miraeassetmf.co.in", holders:  5, aumCr: 1.19, returnPct:  6.3 },
    { name: "Kotak Global Emerging Market FOF",   short: "Global EM FOF",           house: "Kotak Mahindra",   domain: "kotakmf.com",        holders:  5, aumCr: 1.57, returnPct: 82.0, foreign: true },
    { name: "SBI Equity Hybrid Fund",             short: "Equity Hybrid",           house: "SBI MF",           domain: "sbimf.com",          holders:  5, aumCr: 3.85, returnPct: 15.8 },
    { name: "Axis Large & Mid Cap Fund",          short: "Large & Mid Cap",         house: "Axis",             domain: "axismf.com",         holders:  5, aumCr: 0.26, returnPct: 11.1 }
  ],

  // Section 9 — global / overseas investment standouts
  globalAssets: [
    { holder: "Tanuj Punia",      party: "INC",  asset: "Motilal Oswal Nasdaq 100 FOF",         short: "Nasdaq 100 FOF",         domain: "motilaloswalmf.com",  kind: "US Index FOF",     returnPct: 112.4 },
    { holder: "Vivek Thakur",     party: "BJP",  asset: "LIC MF Gold ETF Fund of Fund",         short: "Gold ETF FOF",           domain: "licmf.com",           kind: "Gold FOF",         returnPct: 113.5 },
    { holder: "Multiple (5 MPs)", party: "—",    asset: "Kotak Global Emerging Market FOF",     short: "Global EM FOF",          domain: "kotakmf.com",         kind: "EM Equity FOF",    returnPct:  81.4 },
    { holder: "Pathan Yusuf",     party: "AITC", asset: "Mirae Asset Hang Seng TECH ETF FOF",   short: "Hang Seng TECH FOF",     domain: "miraeassetmf.co.in",  kind: "China Tech FOF",   returnPct:  68.2 },
    { holder: "Arun Nehru",       party: "DMK",  asset: "Motilal Oswal S&P 500 Index Fund",     short: "S&P 500 Index",          domain: "motilaloswalmf.com",  kind: "US Index Fund",    returnPct:  61.9 },
    { holder: "Naveen Jindal",    party: "BJP",  asset: "Meta Platforms (META) common stock",   short: "Meta Platforms",         domain: "meta.com",            kind: "Direct US Equity", returnPct:  27.4 }
  ]
};
