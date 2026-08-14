/* =========================================
   URBAN PARKING PREDICTION DASHBOARD
   ========================================= */

let charts = {};

document.addEventListener("DOMContentLoaded", function() {
  initTabs();
  startClock();
  loadAll();
});

async function loadAll() {
  await checkStatus();
  await loadStats();
  await loadZones();
  await loadForecast();
  await loadHistory();
}

// ── Clock ───────────────────────────────────
function startClock() {
  function tick() {
    var el = document.getElementById("clock");
    if (el) el.textContent = new Date().toLocaleString();
  }
  tick();
  setInterval(tick, 1000);
}

// ── Tabs ────────────────────────────────────
function initTabs() {
  var tabs = document.querySelectorAll(".tab");
  tabs.forEach(function(btn) {
    btn.addEventListener("click", function() {
      tabs.forEach(function(b) { b.classList.remove("active"); });
      document.querySelectorAll(".tab-content").forEach(function(p) {
        p.classList.remove("active");
      });
      btn.classList.add("active");
      var page = document.getElementById("tab-" + btn.dataset.tab);
      if (page) page.classList.add("active");
    });
  });
}

// ── Set card ────────────────────────────────
function setCard(id, value) {
  var el = document.getElementById(id);
  if (el) el.textContent = value;
}

// ── Status ──────────────────────────────────
async function checkStatus() {
  try {
    var res   = await fetch("/api/status");
    var data  = await res.json();
    var badge = document.getElementById("statusBadge");
    if (badge) {
      badge.textContent = data.model_ready ? "Model Ready" : "Mock Mode";
      badge.className   = "badge ok";
    }
  } catch(e) {
    var badge = document.getElementById("statusBadge");
    if (badge) { badge.textContent = "Offline"; badge.className = "badge err"; }
  }
}

// ── Stats ───────────────────────────────────
async function loadStats() {
  try {
    var res  = await fetch("/api/stats");
    var data = await res.json();
    if (!data.success) return;
    var s = data.stats;

    setCard("totalCapacity", s.total_capacity);
    setCard("peakHour",      s.peak_hour);
    setCard("eventCount",    s.event_count);
    setCard("totalOccupancy", Math.round(s.avg_occupancy * 100) + "%");
    setCard("totalAvailable", Math.round(s.avg_available));
    setCard("overallStatus",  getStatusLabel(s.avg_occupancy));

    if (s.hourly_pattern) renderPatternChart(s.hourly_pattern);
    if (s.zone_stats)     renderZoneChart(s.zone_stats);

  } catch(e) { console.error("Stats error:", e); }
}

// ── Zones ───────────────────────────────────
async function loadZones() {
  try {
    var res  = await fetch("/api/predict");
    var data = await res.json();
    if (!data.success) return;
    renderZonesGrid("zonesGrid", data.zones);
  } catch(e) { console.error("Zones error:", e); }
}

// ── Train ───────────────────────────────────
async function trainModel() {
  var btn    = document.getElementById("trainBtn");
  var status = document.getElementById("trainStatus");
  btn.disabled    = true;
  btn.textContent = "Training...";
  if (status) {
    status.textContent = "Training in progress (~30 seconds)...";
    status.style.color = "#f59e0b";
  }
  try {
    var res  = await fetch("/api/train");
    var data = await res.json();
    if (data.success) {
      if (status) {
        status.textContent = "Done! " + data.message;
        status.style.color = "#10b981";
      }
      await checkStatus();
      await loadZones();
      await loadStats();
    } else {
      if (status) {
        status.textContent = "Error: " + data.error;
        status.style.color = "#ef4444";
      }
    }
  } catch(e) {
    if (status) {
      status.textContent = "Failed: " + e.message;
      status.style.color = "#ef4444";
    }
  }
  btn.disabled    = false;
  btn.textContent = "Train Model";
}

// ── Forecast ────────────────────────────────
async function loadForecast() {
  try {
    var res  = await fetch("/api/forecast");
    var data = await res.json();
    if (!data.success) return;
    renderForecastChart(data.forecast);
    renderForecastTable(data.forecast);
  } catch(e) { console.error("Forecast error:", e); }
}

// ── History ─────────────────────────────────
async function loadHistory() {
  try {
    var sel   = document.getElementById("hoursSelect");
    var hours = sel ? sel.value : 48;
    var res   = await fetch("/api/history?hours=" + hours);
    var data  = await res.json();
    if (!data.success) return;
    renderHistoryChart(data.data);
    renderHistoryTable(data.data);
  } catch(e) { console.error("History error:", e); }
}

// ── Predict ─────────────────────────────────
async function runPredict() {
  try {
    var hour    = parseInt(document.getElementById("inp-hour").value)    || 12;
    var weather = parseInt(document.getElementById("inp-weather").value) || 0;
    var event   = parseInt(document.getElementById("inp-event").value)   || 0;

    // Use current prediction from API
    var res  = await fetch("/api/predict");
    var data = await res.json();
    if (!data.success) return;

    document.getElementById("predictResults").style.display = "block";
    renderPredictChart(data.zones);
    renderZonesGrid("predictZonesGrid", data.zones);

  } catch(e) { console.error("Predict error:", e); }
}

// ── Zone Card Renderer ───────────────────────
function renderZonesGrid(containerId, zones) {
  var grid = document.getElementById(containerId);
  if (!grid) return;

  var icons = {
    mall    : "🏬",
    hospital: "🏥",
    office  : "🏢",
    station : "🚉",
    market  : "🛒",
    airport : "✈️",
  };

  var colors = {
    "Available"   : "#10b981",
    "Filling"     : "#f59e0b",
    "Almost Full" : "#f97316",
    "Full"        : "#ef4444",
  };

  grid.innerHTML = Object.entries(zones).map(function(entry) {
    var name = entry[0];
    var info = entry[1];
    var occ  = Math.round(info.occupancy * 100);
    var icon = icons[name] || "🅿️";
    var color= colors[info.status] || "#3b82f6";
    var statusClass = info.status.toLowerCase().replace(" ", "-");

    return "<div class='zone-card'>" +
      "<div class='zone-header'>" +
        "<div class='zone-name'>" + icon + " " +
          name.charAt(0).toUpperCase() + name.slice(1) +
        "</div>" +
        "<span class='zone-status status-" + statusClass + "'>" +
          info.status + "</span>" +
      "</div>" +
      "<div class='zone-stats'>" +
        "<div class='zone-stat'>" +
          "<div class='zone-stat-value' style='color:" + color + "'>" +
            info.available + "</div>" +
          "<div class='zone-stat-label'>Available</div>" +
        "</div>" +
        "<div class='zone-stat'>" +
          "<div class='zone-stat-value'>" + info.occupied + "</div>" +
          "<div class='zone-stat-label'>Occupied</div>" +
        "</div>" +
        "<div class='zone-stat'>" +
          "<div class='zone-stat-value'>" + info.capacity + "</div>" +
          "<div class='zone-stat-label'>Capacity</div>" +
        "</div>" +
      "</div>" +
      "<div class='progress-bar'>" +
        "<div class='progress-fill' style='width:" + occ + "%;background:" + color + "'></div>" +
      "</div>" +
      "<p style='font-size:12px;color:#94a3b8;margin-top:8px;text-align:right'>" +
        occ + "% occupied</p>" +
    "</div>";
  }).join("");
}

// ── Status Label ────────────────────────────
function getStatusLabel(occ) {
  if (occ < 0.5)  return "Good";
  if (occ < 0.75) return "Moderate";
  if (occ < 0.90) return "Busy";
  return "Full";
}

// ── Forecast Table ───────────────────────────
function renderForecastTable(forecast) {
  var tbody = document.querySelector("#forecastTable tbody");
  if (!tbody) return;
  tbody.innerHTML = forecast.map(function(f) {
    var occ   = Math.round(f.occupancy * 100);
    var color = occ > 85 ? "#ef4444" : occ > 70 ? "#f59e0b" : "#10b981";
    return "<tr>" +
      "<td>" + f.label + "</td>" +
      "<td style='color:#10b981;font-weight:600'>" + f.available_spots + "</td>" +
      "<td>" + f.occupied_spots + "</td>" +
      "<td><span style='color:" + color + ";font-weight:600'>" + occ + "%</span></td>" +
      "<td><span class='status-badge status-" +
        f.status.toLowerCase().replace(" ","-") + "'>" +
        f.status + "</span></td>" +
    "</tr>";
  }).join("");
}

// ── History Table ────────────────────────────
function renderHistoryTable(data) {
  var tbody = document.querySelector("#historyTable tbody");
  if (!tbody) return;
  var slice = data.slice(-24).reverse();
  tbody.innerHTML = slice.map(function(r) {
    var d   = new Date(r.timestamp);
    var occ = Math.round(r.total_occupancy * 100);
    return "<tr>" +
      "<td>" + d.toLocaleString() + "</td>" +
      "<td style='color:#10b981'>" + r.total_available + "</td>" +
      "<td>" + occ + "%</td>" +
      "<td>" + r.weather + "</td>" +
      "<td>" + (r.event ? "⭐ Yes" : "No") + "</td>" +
    "</tr>";
  }).join("");
}

// ── Chart Helpers ────────────────────────────
function tip() {
  return {
    backgroundColor:"#111827",titleColor:"#f0f4f8",
    bodyColor:"#94a3b8",borderColor:"#2d3748",borderWidth:1,padding:10
  };
}
function sc() {
  return {
    grid:{color:"rgba(255,255,255,.05)"},
    ticks:{color:"#6b7280",font:{size:11}}
  };
}

// ── Pattern Chart ────────────────────────────
function renderPatternChart(pattern) {
  var ctx = document.getElementById("patternChart");
  if (!ctx) return;
  if (charts["pattern"]) charts["pattern"].destroy();

  var labels = Object.keys(pattern).map(function(h){return h+":00";});
  var values = Object.values(pattern).map(function(v){return Math.round(v*100);});
  var colors = values.map(function(v) {
    if (v > 85) return "rgba(239,68,68,.8)";
    if (v > 70) return "rgba(245,158,11,.8)";
    return "rgba(16,185,129,.8)";
  });

  charts["pattern"] = new Chart(ctx, {
    type:"bar",
    data:{
      labels:labels,
      datasets:[{
        label:"Occupancy %",
        data:values,
        backgroundColor:colors,
        borderRadius:5,
        borderSkipped:false
      }]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:tip()},
      scales:{
        x:sc(),
        y:Object.assign({},sc(),{
          min:0,max:100,
          title:{display:true,text:"Occupancy %",color:"#6b7280"}
        })
      }
    }
  });
}

// ── Zone Chart ───────────────────────────────
function renderZoneChart(zoneStats) {
  var ctx = document.getElementById("zoneChart");
  if (!ctx) return;
  if (charts["zone"]) charts["zone"].destroy();

  var zones  = Object.keys(zoneStats);
  var labels = zones.map(function(z){
    return z.charAt(0).toUpperCase()+z.slice(1);
  });
  var occs = zones.map(function(z){
    return Math.round(zoneStats[z].avg_occupancy * 100);
  });
  var avails = zones.map(function(z){
    return Math.round(zoneStats[z].avg_available);
  });

  charts["zone"] = new Chart(ctx, {
    type:"bar",
    data:{
      labels:labels,
      datasets:[
        {
          label:"Avg Occupancy %",
          data:occs,
          backgroundColor:"rgba(239,68,68,.7)",
          borderRadius:5,
          yAxisID:"y"
        },
        {
          label:"Avg Available Spots",
          data:avails,
          backgroundColor:"rgba(16,185,129,.7)",
          borderRadius:5,
          yAxisID:"y2"
        }
      ]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{
        legend:{display:true,labels:{color:"#94a3b8",font:{size:12},usePointStyle:true}},
        tooltip:tip()
      },
      scales:{
        x:sc(),
        y:Object.assign({},sc(),{
          title:{display:true,text:"Occupancy %",color:"#6b7280"},
          position:"left",min:0,max:100
        }),
        y2:Object.assign({},sc(),{
          title:{display:true,text:"Available Spots",color:"#6b7280"},
          position:"right",grid:{drawOnChartArea:false}
        })
      }
    }
  });
}

// ── Forecast Chart ───────────────────────────
function renderForecastChart(forecast) {
  var ctx = document.getElementById("forecastChart");
  if (!ctx) return;
  if (charts["forecast"]) charts["forecast"].destroy();

  charts["forecast"] = new Chart(ctx, {
    type:"line",
    data:{
      labels:forecast.map(function(f){return f.label;}),
      datasets:[
        {
          label:"Available Spots",
          data:forecast.map(function(f){return f.available_spots;}),
          borderColor:"#10b981",
          backgroundColor:"rgba(16,185,129,.1)",
          fill:true,tension:0.4,borderWidth:2,pointRadius:3,
          yAxisID:"y"
        },
        {
          label:"Occupancy %",
          data:forecast.map(function(f){return Math.round(f.occupancy*100);}),
          borderColor:"#ef4444",
          backgroundColor:"transparent",
          borderDash:[5,4],tension:0.4,borderWidth:2,pointRadius:2,
          yAxisID:"y2"
        }
      ]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      interaction:{mode:"index",intersect:false},
      plugins:{
        legend:{display:true,labels:{color:"#94a3b8",font:{size:12},usePointStyle:true}},
        tooltip:tip()
      },
      scales:{
        x:sc(),
        y:Object.assign({},sc(),{
          title:{display:true,text:"Available Spots",color:"#6b7280"},
          position:"left"
        }),
        y2:Object.assign({},sc(),{
          title:{display:true,text:"Occupancy %",color:"#6b7280"},
          position:"right",
          min:0,max:100,
          grid:{drawOnChartArea:false}
        })
      }
    }
  });
}

// ── History Chart ────────────────────────────
function renderHistoryChart(data) {
  var ctx = document.getElementById("historyChart");
  if (!ctx) return;
  if (charts["history"]) charts["history"].destroy();

  var step   = data.length > 100 ? 2 : 1;
  var points = data.filter(function(_,i){return i%step===0;});

  charts["history"] = new Chart(ctx, {
    type:"line",
    data:{
      labels:points.map(function(r){
        var d=new Date(r.timestamp);
        return d.toLocaleString("en-US",{month:"short",day:"numeric",hour:"2-digit"});
      }),
      datasets:[
        {
          label:"Available Spots",
          data:points.map(function(r){return r.total_available;}),
          borderColor:"#10b981",
          backgroundColor:"rgba(16,185,129,.08)",
          fill:true,tension:0.3,borderWidth:1.5,pointRadius:0,
          yAxisID:"y"
        },
        {
          label:"Occupancy %",
          data:points.map(function(r){return Math.round(r.total_occupancy*100);}),
          borderColor:"#ef4444",
          backgroundColor:"transparent",
          borderDash:[4,3],tension:0.3,borderWidth:1.5,pointRadius:0,
          yAxisID:"y2"
        }
      ]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      interaction:{mode:"index",intersect:false},
      plugins:{
        legend:{display:true,labels:{color:"#94a3b8",font:{size:12},usePointStyle:true}},
        tooltip:tip()
      },
      scales:{
        x:Object.assign({},sc(),{
          ticks:Object.assign({},sc().ticks,{maxTicksLimit:10,maxRotation:45})
        }),
        y:Object.assign({},sc(),{
          title:{display:true,text:"Available Spots",color:"#6b7280"},
          position:"left"
        }),
        y2:Object.assign({},sc(),{
          title:{display:true,text:"Occupancy %",color:"#6b7280"},
          position:"right",min:0,max:100,
          grid:{drawOnChartArea:false}
        })
      }
    }
  });
}

// ── Predict Chart ────────────────────────────
function renderPredictChart(zones) {
  var ctx = document.getElementById("predictChart");
  if (!ctx) return;
  if (charts["predict"]) charts["predict"].destroy();

  var labels = Object.keys(zones).map(function(z){
    return z.charAt(0).toUpperCase()+z.slice(1);
  });
  var available = Object.values(zones).map(function(z){return z.available;});
  var occupied  = Object.values(zones).map(function(z){return z.occupied;});

  charts["predict"] = new Chart(ctx, {
    type:"bar",
    data:{
      labels:labels,
      datasets:[
        {
          label:"Available",
          data:available,
          backgroundColor:"rgba(16,185,129,.8)",
          borderRadius:5,borderSkipped:false
        },
        {
          label:"Occupied",
          data:occupied,
          backgroundColor:"rgba(239,68,68,.8)",
          borderRadius:5,borderSkipped:false
        }
      ]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{
        legend:{display:true,labels:{color:"#94a3b8",font:{size:12},usePointStyle:true}},
        tooltip:tip()
      },
      scales:{
        x:sc(),
        y:Object.assign({},sc(),{
          title:{display:true,text:"Parking Spots",color:"#6b7280"},
          stacked:false
        })
      }
    }
  });
}