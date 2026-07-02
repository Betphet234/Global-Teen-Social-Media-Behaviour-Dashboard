const DATA_PATH = "";
const files = {
  countrySummary: "country_year_summary_2015_2060.csv",
  rankings: "global_country_risk_rankings_2026.csv",
  forecast: "global_forecast_2030_2040_2050_2060.csv",
  regionRisk: "region_2026_risk_profile.csv",
  urbanRural: "regional_urban_rural_risk_summary_2026.csv",
  segments: "teen_behaviour_segments.csv",
  features: "model_feature_importance.csv"
};

let datasets = {};
let tableRows = [];
let sortState = { key: null, asc: true };

const colors = ["#2563eb", "#22c55e", "#f97316", "#ec4899", "#8b5cf6", "#06b6d4"];
const font = { family: "Inter, Arial, sans-serif", color: "#334155" };
const monoFont = { family: "Roboto Mono, monospace", color: "#334155" };

function cleanLabel(text) {
  return String(text).replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
}
function num(v) { const n = Number(v); return Number.isFinite(n) ? n : 0; }
function mean(arr, key) { return arr.length ? arr.reduce((s, r) => s + num(r[key]), 0) / arr.length : 0; }
function format(n, decimals = 2) { return Number(n).toLocaleString(undefined, { maximumFractionDigits: decimals }); }
function unique(arr, key) { return [...new Set(arr.map(r => r[key]).filter(Boolean))]; }

async function loadCsv(file) {
  return new Promise((resolve, reject) => {
    Papa.parse(DATA_PATH + file, {
      download: true,
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: results => resolve(results.data),
      error: err => reject(err)
    });
  });
}

async function init() {
  try {
    const entries = await Promise.all(Object.entries(files).map(async ([key, file]) => [key, await loadCsv(file)]));
    datasets = Object.fromEntries(entries);
    populateCountrySelect();
    updateKpis();
    renderAllCharts(document.getElementById("countrySelect").value);
    renderTable(datasets.rankings);
    setupEvents();
  } catch (error) {
    document.body.innerHTML = `<main style="padding:40px;font-family:Inter"><h2>Dashboard data failed to load</h2><p>${error.message}</p><p>Make sure the CSV files are inside the <b>data</b> folder.</p></main>`;
  }
}

function populateCountrySelect() {
  const countries = unique(datasets.countrySummary, "country").sort();
  const select = document.getElementById("countrySelect");
  select.innerHTML = countries.map(c => `<option value="${c}">${c}</option>`).join("");
  select.value = countries.includes("Nigeria") ? "Nigeria" : countries[0];
}

function updateKpis() {
  document.getElementById("kpiRecords").textContent = format(datasets.countrySummary.length, 0);
  document.getElementById("kpiCountries").textContent = format(unique(datasets.countrySummary, "country").length, 0);
  document.getElementById("kpiRegions").textContent = format(unique(datasets.regionRisk, "region").length, 0);
  document.getElementById("kpiScreen").textContent = `${format(mean(datasets.countrySummary, "avg_screen_time_hours"), 2)} hrs`;
}

function baseLayout(title, height = 420) {
  return {
    title: { text: title, font: { family: "Inter", size: 18, color: "#0f172a" } },
    height,
    margin: { l: 45, r: 20, t: 58, b: 55 },
    font,
    plot_bgcolor: "#ffffff",
    paper_bgcolor: "#ffffff",
    hoverlabel: { font: monoFont },
    legend: { orientation: "h", y: -0.18 }
  };
}

function renderAllCharts(country) {
  renderTrend(country);
  renderTopRisk();
  renderRegional();
  renderUrbanRural();
  renderForecast(country);
  renderSegments();
  renderFeatures();
}

function renderTrend(country) {
  const rows = datasets.countrySummary.filter(r => r.country === country).sort((a, b) => a.year - b.year);
  const metrics = [
    ["avg_screen_time_hours", "Avg Screen Time Hours"],
    ["avg_sleep_hours", "Avg Sleep Hours"],
    ["avg_addiction_score", "Avg Addiction Score"],
    ["avg_mental_health_risk", "Avg Mental Health Risk"]
  ];
  const traces = metrics.map(([key, label], i) => ({
    x: rows.map(r => r.year),
    y: rows.map(r => num(r[key])),
    type: "scatter",
    mode: "lines+markers",
    name: label,
    line: { width: 4, color: colors[i] },
    marker: { size: 7 },
    hovertemplate: `<b>${label}</b><br>Year: %{x}<br>Value: %{y:.2f}<extra></extra>`
  }));
  Plotly.newPlot("trendChart", traces, { ...baseLayout(`Trend Analysis For ${country}`, 430), xaxis: { title: "Year" }, yaxis: { title: "Value" } }, { responsive: true, displayModeBar: false });
}

function renderTopRisk() {
  const rows = [...datasets.rankings].sort((a, b) => num(b.avg_overall_risk) - num(a.avg_overall_risk)).slice(0, 10).reverse();
  const trace = {
    x: rows.map(r => num(r.avg_overall_risk)),
    y: rows.map(r => r.country),
    type: "bar",
    orientation: "h",
    marker: { color: rows.map(r => num(r.avg_overall_risk)), colorscale: "Plasma" },
    text: rows.map(r => format(r.avg_overall_risk, 2)),
    textposition: "auto",
    textfont: monoFont,
    hovertemplate: "<b>%{y}</b><br>Overall Risk: %{x:.2f}<extra></extra>"
  };
  Plotly.newPlot("topRiskChart", [trace], { ...baseLayout("Top 10 High-Risk Countries 2026", 430), xaxis: { title: "Overall Risk" }, yaxis: { title: "" } }, { responsive: true, displayModeBar: false });
}

function renderRegional() {
  const rows = [...datasets.regionRisk].sort((a, b) => num(b.avg_addiction_score) - num(a.avg_addiction_score));
  const trace = {
    x: rows.map(r => r.region),
    y: rows.map(r => num(r.avg_addiction_score)),
    type: "bar",
    marker: { color: rows.map(r => num(r.avg_addiction_score)), colorscale: "Bluered" },
    text: rows.map(r => format(r.avg_addiction_score, 1)),
    textposition: "auto",
    textfont: monoFont,
    hovertemplate: "<b>%{x}</b><br>Addiction Score: %{y:.2f}<extra></extra>"
  };
  Plotly.newPlot("regionalChart", [trace], { ...baseLayout("Regional Addiction Comparison 2026"), xaxis: { title: "Region", tickangle: -35 }, yaxis: { title: "Addiction Score" } }, { responsive: true, displayModeBar: false });
}

function renderUrbanRural() {
  const groups = {};
  datasets.urbanRural.forEach(r => { groups[r.urban_rural] = groups[r.urban_rural] || []; groups[r.urban_rural].push(num(r.avg_addiction_score)); });
  const labels = Object.keys(groups);
  const values = labels.map(k => groups[k].reduce((a, b) => a + b, 0) / groups[k].length);
  const trace = {
    labels,
    values,
    type: "pie",
    hole: 0.58,
    marker: { colors: ["#2563eb", "#9333ea", "#14b8a6", "#f97316"] },
    textinfo: "label+percent",
    textfont: monoFont,
    hovertemplate: "<b>%{label}</b><br>Avg Risk: %{value:.2f}<extra></extra>"
  };
  Plotly.newPlot("urbanRuralChart", [trace], { ...baseLayout("Urban Vs Rural Addiction Risk"), margin: { l: 20, r: 20, t: 58, b: 20 }, showlegend: false }, { responsive: true, displayModeBar: false });
}

function renderForecast(country) {
  const row = datasets.forecast.find(r => r.country === country) || datasets.forecast[0];
  const years = ["2026", "2030", "2040", "2050", "2060"];
  const addiction = [row.baseline_addiction_2026, row.projected_addiction_risk_2030, row.projected_addiction_risk_2040, row.projected_addiction_risk_2050, row.projected_addiction_risk_2060].map(num);
  const mental = [row.baseline_mental_risk_2026, row.projected_mental_health_risk_2030, row.projected_mental_health_risk_2040, row.projected_mental_health_risk_2050, row.projected_mental_health_risk_2060].map(num);
  const traces = [
    { x: years, y: addiction, type: "scatter", mode: "lines+markers", fill: "tozeroy", name: "Addiction Risk", line: { color: "#2563eb", width: 4 }, marker: { size: 8 } },
    { x: years, y: mental, type: "scatter", mode: "lines+markers", fill: "tonexty", name: "Mental Health Risk", line: { color: "#ec4899", width: 4 }, marker: { size: 8 } }
  ];
  Plotly.newPlot("forecastChart", traces, { ...baseLayout(`Forecast Analytics For ${country}`), xaxis: { title: "Forecast Year" }, yaxis: { title: "Risk Score" } }, { responsive: true, displayModeBar: false });
}

function renderSegments() {
  const rows = datasets.segments;
  const trace = {
    x: rows.map(r => r.segment_name || `Segment ${r.segment}`),
    y: rows.map(r => num(r.daily_screen_time_hours)),
    type: "bar",
    marker: { color: rows.map(r => num(r.social_media_hours)), colorscale: "YlOrRd" },
    text: rows.map(r => format(r.daily_screen_time_hours, 2)),
    textposition: "auto",
    textfont: monoFont,
    hovertemplate: "<b>%{x}</b><br>Daily Screen Time: %{y:.2f} hrs<extra></extra>"
  };
  Plotly.newPlot("segmentChart", [trace], { ...baseLayout("Teen Behaviour Segments"), xaxis: { title: "Segment", tickangle: -20 }, yaxis: { title: "Daily Screen Time Hours" } }, { responsive: true, displayModeBar: false });
}

function renderFeatures() {
  const rows = [...datasets.features].sort((a, b) => num(b.importance) - num(a.importance)).slice(0, 10).reverse();
  const trace = {
    x: rows.map(r => num(r.importance)),
    y: rows.map(r => cleanLabel(r.feature)),
    type: "bar",
    orientation: "h",
    marker: { color: rows.map(r => num(r.importance)), colorscale: "Viridis" },
    text: rows.map(r => format(r.importance, 3)),
    textposition: "auto",
    textfont: monoFont,
    hovertemplate: "<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>"
  };
  Plotly.newPlot("featureChart", [trace], { ...baseLayout("Top Model Feature Importance"), xaxis: { title: "Importance" }, yaxis: { title: "" } }, { responsive: true, displayModeBar: false });
}

function renderTable(rows) {
  tableRows = rows;
  const table = document.getElementById("riskTable");
  const columns = Object.keys(rows[0] || {});
  table.querySelector("thead").innerHTML = `<tr>${columns.map(c => `<th data-key="${c}">${cleanLabel(c)}</th>`).join("")}</tr>`;
  table.querySelector("tbody").innerHTML = rows.map(row => `<tr>${columns.map(c => `<td>${typeof row[c] === "number" ? format(row[c], 3) : row[c]}</td>`).join("")}</tr>`).join("");
  table.querySelectorAll("th").forEach(th => th.addEventListener("click", () => sortTable(th.dataset.key)));
}

function sortTable(key) {
  sortState.asc = sortState.key === key ? !sortState.asc : true;
  sortState.key = key;
  const sorted = [...tableRows].sort((a, b) => {
    const av = a[key], bv = b[key];
    const result = (typeof av === "number" && typeof bv === "number") ? av - bv : String(av).localeCompare(String(bv));
    return sortState.asc ? result : -result;
  });
  renderTable(sorted);
}

function setupEvents() {
  document.getElementById("countrySelect").addEventListener("change", e => renderAllCharts(e.target.value));
  document.getElementById("searchInput").addEventListener("input", e => {
    const q = e.target.value.toLowerCase();
    const filtered = datasets.rankings.filter(r => Object.values(r).join(" ").toLowerCase().includes(q));
    renderTable(filtered);
  });
  const navLinks = [...document.querySelectorAll(".nav-link")];
  window.addEventListener("scroll", () => {
    const fromTop = window.scrollY + 120;
    navLinks.forEach(link => {
      const section = document.querySelector(link.hash);
      if (section && section.offsetTop <= fromTop && section.offsetTop + section.offsetHeight > fromTop) {
        navLinks.forEach(l => l.classList.remove("active"));
        link.classList.add("active");
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", init);
