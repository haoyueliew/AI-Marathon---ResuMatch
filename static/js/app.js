/* ══════════════════════════════════════════════════════════════
   ResuMatch — Frontend Logic (demo-data build, Morpheus AI)
   ══════════════════════════════════════════════════════════════ */

/* ── State ───────────────────────────────────────────────────── */
let userProfile   = null;
let allJobs       = {};
let currentFilter = "all";
let selectedJob   = null;
let currentMode   = "score";
let scoreData     = null;
let reportData    = null;

/* ── Helpers ─────────────────────────────────────────────────── */
function toast(msg, type = "") {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = "toast show " + type;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.className = "toast"; }, 3500);
}

function setStep(n) {
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById("step-" + i);
    el.classList.remove("active", "done");
    if (i < n)  el.classList.add("done");
    if (i === n) el.classList.add("active");
  }
}

function showPage(id) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.getElementById("page-" + id).classList.add("active");
}

function initials(name) {
  if (!name || name === "Not found") return "?";
  return name.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2);
}

async function api(path, method = "GET", body = null) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function apiForm(path, formData) {
  const res = await fetch(path, { method: "POST", body: formData });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

/* ── Platform checkboxes ─────────────────────────────────────── */
document.querySelectorAll(".platform-toggle").forEach(label => {
  label.addEventListener("click", () => {
    const cb = label.querySelector("input[type=checkbox]");
    cb.checked = !cb.checked;
    label.classList.toggle("checked", cb.checked);
  });
});

/* ══════════════════════════════════════════════════════════════
   STEP 1 — Upload & Parse Resume
   ══════════════════════════════════════════════════════════════ */
const dropZone  = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
let   chosenFile = null;

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", e => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files[0]) setChosenFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) setChosenFile(fileInput.files[0]);
});
document.getElementById("remove-file").addEventListener("click", () => {
  chosenFile = null;
  fileInput.value = "";
  document.getElementById("file-chosen").style.display = "none";
  document.getElementById("btn-parse-resume").disabled = true;
});

function setChosenFile(f) {
  const ext = f.name.split(".").pop().toLowerCase();
  if (!["pdf","docx","txt"].includes(ext)) {
    toast("Only PDF, DOCX, or TXT files are supported", "error"); return;
  }
  if (f.size > 5 * 1024 * 1024) {
    toast("File too large (max 5 MB)", "error"); return;
  }
  chosenFile = f;
  document.getElementById("file-chosen-name").textContent = f.name;
  document.getElementById("file-chosen").style.display = "flex";
  document.getElementById("btn-parse-resume").disabled = false;
}

const parseTexts = [
  "Reading your resume...",
  "Extracting skills and experience...",
  "Identifying your professional profile...",
  "Almost there..."
];

document.getElementById("btn-parse-resume").addEventListener("click", async () => {
  if (!chosenFile) { toast("Please upload a resume first", "error"); return; }

  const loader     = document.getElementById("upload-loader");
  const loaderText = document.getElementById("upload-loader-text");
  const btn        = document.getElementById("btn-parse-resume");

  loader.classList.add("show");
  btn.disabled = true;

  let li = 0;
  const iv = setInterval(() => {
    loaderText.textContent = parseTexts[++li % parseTexts.length];
  }, 2200);

  const fd = new FormData();
  fd.append("resume", chosenFile);

  try {
    const data = await apiForm("/api/parse-resume", fd);
    clearInterval(iv);
    loader.classList.remove("show");
    userProfile = data.profile;
    renderProfileCard(data.profile);
    setStep(2);
    showPage("profile");
    toast("Resume analysed ✓", "success");
  } catch (e) {
    clearInterval(iv);
    loader.classList.remove("show");
    btn.disabled = false;
    toast(e.message, "error");
  }
});

/* ══════════════════════════════════════════════════════════════
   STEP 2 — Profile & Job Search
   ══════════════════════════════════════════════════════════════ */
function renderProfileCard(p) {
  const card = document.getElementById("profile-card");
  const skillsHtml = (p.skills || []).slice(0, 12)
    .map(s => `<span class="tag">${s}</span>`).join("");
  card.innerHTML = `
    <div class="profile-avatar">${initials(p.name)}</div>
    <div class="profile-name">${p.name || "You"}</div>
    <div class="profile-major">${p.major || "Professional"}</div>
    <div class="profile-level">📊 ${p.level || "Mid-level"} &nbsp;·&nbsp; ${p.experience_years || 0} yrs exp.</div>
    <div class="profile-summary">${p.summary || ""}</div>
    <div class="profile-meta"><strong>Education:</strong> ${p.education || "Not specified"}</div>
    <div class="profile-skills">${skillsHtml}</div>
  `;
  // Pre-fill search with AI keywords
  document.getElementById("search-query").value =
    (p.search_keywords || [p.major || ""]).join(", ");
}

document.getElementById("btn-search-jobs").addEventListener("click", async () => {
  const query    = document.getElementById("search-query").value.trim();
  const platforms = Array.from(
    document.querySelectorAll(".platform-toggle input:checked")
  ).map(cb => cb.value);

  if (!platforms.length) { toast("Select at least one platform", "error"); return; }
  if (!query)            { toast("Enter job keywords", "error"); return; }

  const loader = document.getElementById("jobs-loader");
  const btn    = document.getElementById("btn-search-jobs");
  loader.classList.add("show");
  btn.disabled = true;

  try {
    const data = await api("/api/jobs", "POST", { platforms, query });
    allJobs = data;
    setStep(3);
    showPage("jobs");
    renderJobsPage(platforms);
    toast("Jobs loaded ✓", "success");
  } catch (e) {
    toast(e.message, "error");
  } finally {
    loader.classList.remove("show");
    btn.disabled = false;
  }
});

/* ══════════════════════════════════════════════════════════════
   STEP 3 — Job Listings
   ══════════════════════════════════════════════════════════════ */
function renderJobsPage(platforms) {
  const filterBar = document.getElementById("platform-filter");
  const allList   = getAllJobsList();

  filterBar.innerHTML =
    `<button class="filter-btn active" data-filter="all">All (${allList.length})</button>`;

  platforms.forEach(p => {
    const count = (allJobs[p] || []).length;
    if (count)
      filterBar.innerHTML +=
        `<button class="filter-btn" data-filter="${p}">${capitalise(p)} (${count})</button>`;
  });

  filterBar.querySelectorAll(".filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      filterBar.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.dataset.filter;
      renderJobGrid();
    });
  });

  document.getElementById("jobs-sub").textContent =
    `${allList.length} jobs found across ${platforms.length} platform(s)`;
  currentFilter = "all";
  renderJobGrid();
}

function capitalise(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function getAllJobsList() {
  return Object.values(allJobs).flat().filter(j => j && j.title);
}

function getFilteredJobs() {
  return currentFilter === "all" ? getAllJobsList() : (allJobs[currentFilter] || []);
}

function renderJobGrid() {
  const grid = document.getElementById("job-grid");
  const jobs = getFilteredJobs();

  if (!jobs.length) {
    grid.innerHTML = `<div class="empty"><div class="empty-icon">🔍</div>No jobs found for this filter.</div>`;
    return;
  }

  grid.innerHTML = jobs.map(job => {
    const pl = (job.platform || "").toLowerCase();
    const skillsHtml = (job.skills || []).slice(0, 5)
      .map(s => `<span class="tag">${s}</span>`).join("");
    return `
      <div class="job-card">
        <div class="job-card-top">
          <div>
            <div class="job-title">${job.title}</div>
            <div class="job-company">${job.company}</div>
          </div>
          <span class="job-platform-badge platform-${pl}">${job.platform}</span>
        </div>
        <div class="job-meta">
          <span>📍 ${job.location || "Malaysia"}</span>
          <span>⏱ ${job.type || "Full-time"}</span>
        </div>
        ${job.salary ? `<div class="job-salary">💰 ${job.salary}</div>` : ""}
        <div class="job-tags">${skillsHtml}</div>
        <div class="job-card-footer">
          <span class="job-posted">${job.posted ? "📅 "+job.posted : ""}</span>
          <button class="btn-match" data-id="${job.id}">Analyse Match →</button>
        </div>
      </div>`;
  }).join("");

  grid.querySelectorAll(".btn-match").forEach(btn => {
    btn.addEventListener("click", e => {
      e.stopPropagation();
      const job = getAllJobsList().find(j => j.id == btn.dataset.id);
      if (job) startMatch(job);
    });
  });
}

document.getElementById("btn-back-profile").addEventListener("click", () => {
  setStep(2); showPage("profile");
});

/* ══════════════════════════════════════════════════════════════
   STEP 4 — Match Analysis
   ══════════════════════════════════════════════════════════════ */
function startMatch(job) {
  selectedJob = job;
  scoreData   = null;
  reportData  = null;
  currentMode = "score";

  document.getElementById("match-job-title").textContent =
    `${job.title} @ ${job.company}`;
  document.getElementById("mode-score").classList.add("active");
  document.getElementById("mode-report").classList.remove("active");

  const pl = (job.platform || "").toLowerCase();
  document.getElementById("match-job-info").innerHTML = `
    <span class="job-platform-badge platform-${pl}"
          style="margin-bottom:10px;display:inline-block">${job.platform}</span>
    <h3>${job.title}</h3>
    <div class="co">${job.company} &middot; ${job.location || "Malaysia"}</div>
    ${job.salary ? `<div style="font-size:12px;font-weight:700;color:var(--green);margin-bottom:8px">💰 ${job.salary}</div>` : ""}
    <div class="desc">${job.description || "No description available."}</div>
    <div class="profile-skills" style="margin-top:10px">
      ${(job.skills||[]).map(s=>`<span class="tag">${s}</span>`).join("")}
    </div>
  `;

  document.getElementById("score-view").style.display  = "none";
  document.getElementById("report-view").style.display = "none";

  setStep(4);
  showPage("match");
  runMatch("score");
}

async function runMatch(mode) {
  const loader = document.getElementById("match-loader");
  document.getElementById("match-loader-text").textContent =
    mode === "score" ? "Calculating match score..." : "Writing detailed report...";

  loader.classList.add("show");
  document.getElementById("score-view").style.display  = "none";
  document.getElementById("report-view").style.display = "none";

  try {
    const data = await api("/api/match", "POST", {
      profile: userProfile,
      job:     selectedJob,
      mode
    });
    loader.classList.remove("show");
    if (mode === "score") {
      scoreData = data.data;
      renderScoreView(data.data);
    } else {
      reportData = data.data;
      renderReportView(data.data, data.engine);
    }
  } catch (e) {
    loader.classList.remove("show");
    toast(e.message, "error");
  }
}

function renderScoreView(d) {
  const score = d.overall_score || 0;
  const circ  = 327;
  const ring  = document.getElementById("ring-fill");

  // Reset then animate
  ring.style.transition = "none";
  ring.style.strokeDashoffset = circ;
  setTimeout(() => {
    ring.style.transition = "stroke-dashoffset 1s ease";
    ring.style.strokeDashoffset = circ - (score / 100) * circ;
  }, 50);

  // Colour by score
  if      (score >= 75) ring.style.stroke = "var(--green)";
  else if (score >= 55) ring.style.stroke = "var(--accent)";
  else if (score >= 35) ring.style.stroke = "var(--amber)";
  else                  ring.style.stroke = "var(--red)";

  document.getElementById("score-num").textContent = score;

  // Verdict badge
  const vm = {
    "Strong Match": "badge-strong",
    "Good Match":   "badge-good",
    "Partial Match":"badge-partial",
    "Weak Match":   "badge-weak"
  };
  const v = d.verdict || "Partial Match";
  document.getElementById("score-verdict").innerHTML =
    `<span class="status-badge ${vm[v] || 'badge-partial'}">${v}</span>`;
  document.getElementById("score-oneliner").textContent = d.one_liner || "";

  // Sub-score bars
  const setBar = (barId, valId, val) => {
    document.getElementById(barId).style.width    = (val || 0) + "%";
    document.getElementById(valId).textContent    = (val || 0);
  };
  setBar("bar-skills", "val-skills", d.skills_score);
  setBar("bar-exp",    "val-exp",    d.experience_score);
  setBar("bar-edu",    "val-edu",    d.education_score);

  // Skill tags
  document.getElementById("matched-skills").innerHTML =
    (d.matched_skills || []).map(s =>
      `<span class="skill-tag-matched">${s}</span>`).join("") ||
    `<em style="font-size:12px;color:var(--text3)">No direct skill overlap found</em>`;

  document.getElementById("missing-skills").innerHTML =
    (d.missing_skills || []).map(s =>
      `<span class="skill-tag-missing">${s}</span>`).join("") ||
    `<em style="font-size:12px;color:var(--text3)">None — great match!</em>`;

  document.getElementById("score-view").style.display = "block";
}

function renderReportView(text, engine) {
  document.getElementById("report-view").innerHTML =
    `<div class="report-engine-tag">✦ ${engine || "Morpheus AI"}</div>\n${text}`;
  document.getElementById("report-view").style.display = "block";
}

/* Mode toggle */
document.getElementById("mode-score").addEventListener("click", () => {
  currentMode = "score";
  document.getElementById("mode-score").classList.add("active");
  document.getElementById("mode-report").classList.remove("active");
  if (scoreData) {
    document.getElementById("report-view").style.display = "none";
    renderScoreView(scoreData);
  } else {
    runMatch("score");
  }
});

document.getElementById("mode-report").addEventListener("click", () => {
  currentMode = "report";
  document.getElementById("mode-report").classList.add("active");
  document.getElementById("mode-score").classList.remove("active");
  if (reportData) {
    document.getElementById("score-view").style.display = "none";
    renderReportView(reportData);
  } else {
    runMatch("report");
  }
});

document.getElementById("btn-view-report").addEventListener("click", () => {
  document.getElementById("mode-report").click();
});

document.getElementById("btn-back-jobs").addEventListener("click", () => {
  setStep(3); showPage("jobs");
});