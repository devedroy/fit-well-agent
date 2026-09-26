/**
 * FitWell — Dashboard & State Management Controller
 * Handles tab navigation, REST API synchronization, metric computations,
 * canvas chart rendering, facility filtering, and quick log modal interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initModals();
  initEventListeners();
  loadAllDashboardData();
  loadFacilities();
  loadRawMemory();
});

// Global state cache
const appState = {
  profile: null,
  workouts: [],
  meals: [],
  progress: { weight_log: [], strength_log: [], cardio_log: [] },
  facilities: [],
  activeFacilityFilter: 'all',
  maxFacilityDistance: 10,
};

/* ==========================================================================
   Tab Navigation
   ========================================================================== */
function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
}

function switchTab(tabId) {
  // Update buttons
  document.querySelectorAll('.tab-btn').forEach(b => {
    const isActive = b.getAttribute('data-tab') === tabId;
    b.classList.toggle('active', isActive);
    b.setAttribute('aria-selected', isActive ? 'true' : 'false');
  });

  // Update panes
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.remove('active');
  });

  const activePane = document.getElementById(`tab-${tabId}`);
  if (activePane) {
    activePane.classList.add('active');
  }

  // Specific triggers
  if (tabId === 'dashboard') {
    renderWeightChart();
  } else if (tabId === 'profile') {
    loadRawMemory();
  } else if (tabId === 'chat') {
    const input = document.getElementById('chat-input-field');
    if (input) input.focus();
  }
}

// Global helper for opening a tab from anywhere
window.switchTab = switchTab;

/* ==========================================================================
   Data Fetching & Synchronization
   ========================================================================== */
async function loadAllDashboardData() {
  try {
    await Promise.all([
      fetchProfile(),
      fetchWorkouts(),
      fetchMeals(),
      fetchProgress(),
    ]);
    updateDashboardMetrics();
    renderWorkoutsList();
    renderMealsList();
    renderStrengthPRs();
    renderWeightChart();
  } catch (err) {
    console.error('Error loading dashboard data:', err);
    showToast('Failed to load some dashboard metrics.', 'error');
  }
}

async function fetchProfile() {
  const res = await fetch('/api/profile');
  if (!res.ok) throw new Error('Failed to fetch profile');
  const profile = await res.json();
  appState.profile = profile;
  populateProfileUI(profile);
  return profile;
}

async function fetchWorkouts() {
  const res = await fetch('/api/workouts?limit=10');
  if (!res.ok) throw new Error('Failed to fetch workouts');
  const workouts = await res.json();
  appState.workouts = workouts;
  return workouts;
}

async function fetchMeals() {
  const res = await fetch('/api/meals?limit=14');
  if (!res.ok) throw new Error('Failed to fetch meals');
  const meals = await res.json();
  appState.meals = meals;
  return meals;
}

async function fetchProgress() {
  const res = await fetch('/api/progress');
  if (!res.ok) throw new Error('Failed to fetch progress');
  const progress = await res.json();
  appState.progress = progress;
  return progress;
}

/* ==========================================================================
   UI Population & Computations
   ========================================================================== */
function populateProfileUI(profile) {
  if (!profile) return;

  // Header & Banner
  const nameEl = document.getElementById('user-display-name');
  if (nameEl) nameEl.textContent = profile.name || 'Devpreyo';

  const goalEl = document.getElementById('user-display-goal');
  if (goalEl) goalEl.textContent = profile.goal || 'General Health';

  const locEl = document.getElementById('user-display-location');
  if (locEl) locEl.textContent = profile.location || 'Local';

  const levelEl = document.getElementById('user-display-level');
  if (levelEl) levelEl.textContent = profile.fitness_level ? capitalize(profile.fitness_level) : 'Intermediate';

  const dietEl = document.getElementById('user-display-diet');
  if (dietEl) {
    const restrictions = Array.isArray(profile.dietary_restrictions) 
      ? profile.dietary_restrictions.join(', ') 
      : profile.dietary_restrictions;
    dietEl.textContent = restrictions || 'None';
  }

  // Profile Form fields
  const form = document.getElementById('profile-edit-form');
  if (form) {
    if (form.elements['name']) form.elements['name'].value = profile.name || '';
    if (form.elements['location']) form.elements['location'].value = profile.location || '';
    if (form.elements['age']) form.elements['age'].value = profile.age || '';
    if (form.elements['gender']) form.elements['gender'].value = profile.gender || 'male';
    if (form.elements['fitness_level']) form.elements['fitness_level'].value = profile.fitness_level || 'intermediate';
    if (form.elements['weight_kg']) form.elements['weight_kg'].value = profile.weight_kg || '';
    if (form.elements['height_cm']) form.elements['height_cm'].value = profile.height_cm || '';
    if (form.elements['goal']) form.elements['goal'].value = profile.goal || '';
    if (form.elements['dietary_restrictions']) {
      const dietVal = Array.isArray(profile.dietary_restrictions)
        ? profile.dietary_restrictions.join(', ')
        : (profile.dietary_restrictions || '');
      form.elements['dietary_restrictions'].value = dietVal;
    }
  }
}

function updateDashboardMetrics() {
  const { profile, workouts, meals, progress } = appState;

  // 1. Weight Metric
  const weightValEl = document.getElementById('metric-weight-val');
  const weightSubEl = document.getElementById('metric-weight-sub');
  const weights = progress.weight_log || [];
  
  if (weights.length > 0) {
    const currentWeight = weights[weights.length - 1].weight_kg;
    const initialWeight = weights[0].weight_kg;
    const diff = (currentWeight - initialWeight).toFixed(1);
    const sign = diff >= 0 ? '+' : '';

    if (weightValEl) weightValEl.textContent = currentWeight.toFixed(1);
    if (weightSubEl) {
      weightSubEl.innerHTML = `
        <span class="trend-pill ${diff >= 0 ? 'trend-up' : 'trend-down'}">${diff >= 0 ? '▲' : '▼'} ${sign}${diff} kg</span>
        <span>from start (${initialWeight.toFixed(1)} kg)</span>
      `;
    }
  } else if (profile && profile.weight_kg) {
    if (weightValEl) weightValEl.textContent = Number(profile.weight_kg).toFixed(1);
    if (weightSubEl) weightSubEl.innerHTML = `<span>Profile recorded weight</span>`;
  }

  // 2. Workouts Metric
  const workoutCountEl = document.getElementById('metric-workout-count');
  const workoutSubEl = document.getElementById('metric-workout-sub');
  if (workoutCountEl) workoutCountEl.textContent = workouts.length;
  if (workoutSubEl) {
    const totalMinutes = workouts.reduce((sum, w) => sum + (Number(w.duration_min) || 0), 0);
    workoutSubEl.innerHTML = `<span>${totalMinutes} mins total recorded</span>`;
  }

  // 3. Nutrition Metric
  let totalCalories = 0;
  let totalP = 0, totalC = 0, totalF = 0;
  meals.forEach(m => {
    totalCalories += Number(m.total_calories) || 0;
    if (m.macros) {
      totalP += Number(m.macros.protein_g) || 0;
      totalC += Number(m.macros.carbs_g) || 0;
      totalF += Number(m.macros.fat_g) || 0;
    }
  });

  const calValEl = document.getElementById('metric-calories-val');
  const macroPEl = document.getElementById('macro-p-total');
  const macroCEl = document.getElementById('macro-c-total');
  const macroFEl = document.getElementById('macro-f-total');

  if (calValEl) calValEl.textContent = totalCalories.toLocaleString();
  if (macroPEl) macroPEl.textContent = `${Math.round(totalP)}g`;
  if (macroCEl) macroCEl.textContent = `${Math.round(totalC)}g`;
  if (macroFEl) macroFEl.textContent = `${Math.round(totalF)}g`;
}

/* ==========================================================================
   Activity Lists Rendering
   ========================================================================== */
function renderWorkoutsList() {
  const container = document.getElementById('workout-list-container');
  if (!container) return;

  const workouts = appState.workouts || [];
  if (workouts.length === 0) {
    container.innerHTML = `<div class="empty-state">No workout sessions logged yet. Click "+ New Workout" to record one!</div>`;
    return;
  }

  // Reverse so newest appears first
  const displayWorkouts = [...workouts].reverse().slice(0, 5);

  container.innerHTML = displayWorkouts.map(w => {
    const dateStr = formatDateTime(w.date);
    const type = (w.type || 'strength').toLowerCase();
    const tagClass = `tag-${type}`;

    let exercisesHtml = '';
    if (Array.isArray(w.exercises) && w.exercises.length > 0) {
      exercisesHtml = `
        <div class="exercises-tags-list">
          ${w.exercises.map(e => `
            <span class="exercise-pill">
              <strong>${escapeHtml(e.name)}</strong>: ${e.sets}×${e.reps}${e.weight_kg ? ` @ ${e.weight_kg}kg` : ''}
            </span>
          `).join('')}
        </div>
      `;
    }

    const notesHtml = w.notes ? `<div class="workout-item-notes">“${escapeHtml(w.notes)}”</div>` : '';

    return `
      <div class="workout-item-card">
        <div class="workout-item-header">
          <span class="workout-type-tag ${tagClass}">⚡ ${escapeHtml(w.type || 'workout')}</span>
          <span class="workout-duration">⏱️ ${w.duration_min} min • ${dateStr}</span>
        </div>
        ${exercisesHtml}
        ${notesHtml}
      </div>
    `;
  }).join('');
}

function renderMealsList() {
  const container = document.getElementById('meal-list-container');
  if (!container) return;

  const meals = appState.meals || [];
  if (meals.length === 0) {
    container.innerHTML = `<div class="empty-state">No meals logged yet. Click "+ Log Meal" to record nutrition!</div>`;
    return;
  }

  const displayMeals = [...meals].reverse().slice(0, 5);

  container.innerHTML = displayMeals.map(m => {
    const dateStr = formatDateTime(m.date);
    const foodsList = Array.isArray(m.foods) ? m.foods.join(', ') : (m.foods || '');
    const p = m.macros?.protein_g ? `${Math.round(m.macros.protein_g)}g P` : '';
    const c = m.macros?.carbs_g ? `${Math.round(m.macros.carbs_g)}g C` : '';
    const f = m.macros?.fat_g ? `${Math.round(m.macros.fat_g)}g F` : '';
    const macroStr = [p, c, f].filter(Boolean).join(' • ');

    return `
      <div class="meal-item-card">
        <div class="meal-item-header">
          <span class="meal-type-title">🥗 ${escapeHtml(m.meal_type || 'meal')}</span>
          <span class="meal-calories-badge">${m.total_calories} kcal</span>
        </div>
        <div class="meal-foods-str">${escapeHtml(foodsList)}</div>
        <div class="meal-macros-chips">
          <span>${macroStr}</span>
          <span style="margin-left: auto;">${dateStr}</span>
        </div>
      </div>
    `;
  }).join('');
}

function renderStrengthPRs() {
  const container = document.getElementById('pr-list-container');
  if (!container) return;

  const strengthLogs = appState.progress.strength_log || [];
  if (strengthLogs.length === 0) {
    container.innerHTML = `<div class="empty-state" style="grid-column: 1 / -1;">No strength PRs recorded yet.</div>`;
    return;
  }

  // Get max weight for each unique exercise
  const prMap = {};
  strengthLogs.forEach(entry => {
    const name = entry.exercise;
    if (!prMap[name] || entry.weight_kg > prMap[name].weight_kg) {
      prMap[name] = entry;
    }
  });

  container.innerHTML = Object.values(prMap).map(pr => `
    <div class="pr-card">
      <span class="pr-exercise">${escapeHtml(pr.exercise)}</span>
      <span class="pr-stat">${pr.weight_kg} <small style="font-size: 0.6em;">kg</small></span>
      <span class="pr-meta">${pr.sets} sets × ${pr.reps} reps</span>
    </div>
  `).join('');
}

/* ==========================================================================
   Weight Progress Chart (Smooth Canvas Chart)
   ========================================================================== */
function renderWeightChart() {
  const canvas = document.getElementById('weight-chart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();

  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.scale(dpr, dpr);

  const width = rect.width;
  const height = rect.height;

  ctx.clearRect(0, 0, width, height);

  const weights = appState.progress.weight_log || [];
  if (weights.length < 2) {
    ctx.fillStyle = '#64748b';
    ctx.font = '14px Plus Jakarta Sans, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Log 2 or more weight entries to visualize progress over time.', width / 2, height / 2);
    return;
  }

  // Padding
  const padLeft = 45;
  const padRight = 30;
  const padTop = 30;
  const padBottom = 40;

  const chartWidth = width - padLeft - padRight;
  const chartHeight = height - padTop - padBottom;

  const values = weights.map(w => w.weight_kg);
  const minVal = Math.floor(Math.min(...values) - 0.5);
  const maxVal = Math.ceil(Math.max(...values) + 0.5);
  const range = maxVal - minVal || 1;

  // Draw grid lines
  const steps = 4;
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
  ctx.lineWidth = 1;
  ctx.fillStyle = '#64748b';
  ctx.font = '11px Outfit, sans-serif';
  ctx.textAlign = 'right';

  for (let i = 0; i <= steps; i++) {
    const yVal = minVal + (range / steps) * i;
    const yPos = padTop + chartHeight - (chartHeight / steps) * i;
    ctx.beginPath();
    ctx.moveTo(padLeft, yPos);
    ctx.lineTo(width - padRight, yPos);
    ctx.stroke();
    ctx.fillText(`${yVal.toFixed(1)}kg`, padLeft - 8, yPos + 4);
  }

  // Calculate points
  const points = weights.map((w, idx) => {
    const x = padLeft + (chartWidth / (weights.length - 1)) * idx;
    const y = padTop + chartHeight - ((w.weight_kg - minVal) / range) * chartHeight;
    return { x, y, weight: w.weight_kg, date: w.date };
  });

  // Area gradient
  const areaGrad = ctx.createLinearGradient(0, padTop, 0, height - padBottom);
  areaGrad.addColorStop(0, 'rgba(16, 185, 129, 0.35)');
  areaGrad.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

  // Draw smooth area
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (let i = 0; i < points.length - 1; i++) {
    const xc = (points[i].x + points[i + 1].x) / 2;
    const yc = (points[i].y + points[i + 1].y) / 2;
    ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
  }
  ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y);
  ctx.lineTo(points[points.length - 1].x, height - padBottom);
  ctx.lineTo(points[0].x, height - padBottom);
  ctx.closePath();
  ctx.fillStyle = areaGrad;
  ctx.fill();

  // Draw line
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (let i = 0; i < points.length - 1; i++) {
    const xc = (points[i].x + points[i + 1].x) / 2;
    const yc = (points[i].y + points[i + 1].y) / 2;
    ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
  }
  ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y);
  ctx.strokeStyle = '#10b981';
  ctx.lineWidth = 3;
  ctx.stroke();

  // Draw points and labels
  points.forEach((p, idx) => {
    // Dot glow
    ctx.beginPath();
    ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#07090e';
    ctx.fill();
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Value tag above point
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 11px Outfit, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`${p.weight}kg`, p.x, p.y - 10);

    // Date below axis
    ctx.fillStyle = '#64748b';
    ctx.font = '10px Plus Jakarta Sans, sans-serif';
    const d = new Date(p.date);
    const dateFmt = `${d.getMonth() + 1}/${d.getDate()}`;
    ctx.fillText(dateFmt, p.x, height - padBottom + 16);
  });
}

// Re-render chart on window resize
window.addEventListener('resize', () => {
  if (document.getElementById('tab-dashboard')?.classList.contains('active')) {
    renderWeightChart();
  }
});

/* ==========================================================================
   Facilities Tab Controller
   ========================================================================== */
async function loadFacilities() {
  try {
    const { activeFacilityFilter, maxFacilityDistance } = appState;
    const url = `/api/facilities?type=${encodeURIComponent(activeFacilityFilter)}&max_distance=${maxFacilityDistance}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to load facilities');
    const data = await res.json();
    appState.facilities = data.facilities || [];
    renderFacilitiesList();
  } catch (err) {
    console.error('Facilities load error:', err);
  }
}

function renderFacilitiesList() {
  const container = document.getElementById('facilities-grid-container');
  if (!container) return;

  const facilities = appState.facilities || [];
  const searchInput = document.getElementById('facility-search-input');
  const searchKeyword = searchInput ? searchInput.value.toLowerCase().trim() : '';

  let filtered = facilities;
  if (searchKeyword) {
    filtered = filtered.filter(f => 
      f.name.toLowerCase().includes(searchKeyword) ||
      (f.amenities && f.amenities.some(a => a.toLowerCase().includes(searchKeyword))) ||
      (f.address && f.address.toLowerCase().includes(searchKeyword))
    );
  }

  if (filtered.length === 0) {
    container.innerHTML = `<div class="empty-state" style="grid-column: 1 / -1;">No facilities found matching your criteria. Try adjusting the category, distance slider, or search keyword.</div>`;
    return;
  }

  container.innerHTML = filtered.map(f => {
    const amenitiesHtml = (f.amenities || []).map(a => `<span class="amenity-chip">${escapeHtml(a)}</span>`).join('');
    return `
      <div class="facility-card glass-card">
        <div>
          <div class="facility-top">
            <h3 class="facility-name">${escapeHtml(f.name)}</h3>
            <span class="facility-dist-badge">📍 ${f.distance_km} km</span>
          </div>
          <div class="facility-meta">
            <span class="facility-rating">★ ${f.rating}</span>
            <span>•</span>
            <span style="text-transform: capitalize; color: var(--accent-cyan);">${escapeHtml(f.type)}</span>
            <span>•</span>
            <span>${escapeHtml(f.hours || 'Open')}</span>
          </div>
          <div class="facility-address">🏠 ${escapeHtml(f.address)}</div>
          <div class="facility-amenities">${amenitiesHtml}</div>
        </div>
        <div style="margin-top: 0.5rem;">
          <button class="btn btn-secondary btn-sm" style="width: 100%;" onclick="askCoachAboutFacility('${escapeJsString(f.name)}')">
            💬 Ask FitWell Coach About This Spot
          </button>
        </div>
      </div>
    `;
  }).join('');
}

window.askCoachAboutFacility = function(facilityName) {
  switchTab('chat');
  const chatInput = document.getElementById('chat-input-field');
  if (chatInput) {
    chatInput.value = `Tell me about ${facilityName}. What workouts or amenities are best suited for my muscle gain goal there?`;
    chatInput.focus();
  }
};

/* ==========================================================================
   Raw Memory Inspector
   ========================================================================== */
async function loadRawMemory() {
  const container = document.getElementById('raw-memory-json');
  if (!container) return;

  try {
    const res = await fetch('/api/memory');
    if (!res.ok) throw new Error('Failed to dump memory');
    const data = await res.json();
    container.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    container.textContent = `Error loading memory: ${err.message}`;
  }
}

/* ==========================================================================
   Modals & Form Interactions
   ========================================================================== */
function initModals() {
  // Open buttons
  document.getElementById('btn-quick-log-weight')?.addEventListener('click', () => openModal('modal-log-weight'));
  document.getElementById('btn-chart-add-weight')?.addEventListener('click', () => openModal('modal-log-weight'));
  
  document.getElementById('btn-quick-log-meal')?.addEventListener('click', () => openModal('modal-log-meal'));
  document.getElementById('btn-dash-add-meal')?.addEventListener('click', () => openModal('modal-log-meal'));

  document.getElementById('btn-quick-log-workout')?.addEventListener('click', () => openModal('modal-log-workout'));
  document.getElementById('btn-dash-add-workout')?.addEventListener('click', () => openModal('modal-log-workout'));

  // Close buttons
  document.querySelectorAll('[data-close]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modalId = btn.getAttribute('data-close');
      closeModal(modalId);
    });
  });

  // Close on backdrop click
  document.querySelectorAll('.app-modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.close();
      }
    });
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal && typeof modal.showModal === 'function') {
    modal.showModal();
    const firstInput = modal.querySelector('input, select, textarea');
    if (firstInput) setTimeout(() => firstInput.focus(), 50);
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal && typeof modal.close === 'function') {
    modal.close();
  }
}

function initEventListeners() {
  // Facility Filter Pills
  document.querySelectorAll('.filter-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      appState.activeFacilityFilter = pill.getAttribute('data-type');
      loadFacilities();
    });
  });

  // Facility Distance Slider
  const distSlider = document.getElementById('distance-slider');
  const distValLabel = document.getElementById('distance-slider-val');
  if (distSlider && distValLabel) {
    distSlider.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      distValLabel.textContent = `${val} km`;
      appState.maxFacilityDistance = val;
      loadFacilities();
    });
  }

  // Facility Search Input
  document.getElementById('facility-search-input')?.addEventListener('input', () => {
    renderFacilitiesList();
  });

  // Profile Form Save
  const profileForm = document.getElementById('profile-edit-form');
  if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const statusEl = document.getElementById('profile-save-status');
      if (statusEl) {
        statusEl.textContent = 'Saving…';
        statusEl.className = 'save-status-msg';
      }

      const dietaryRaw = profileForm.elements['dietary_restrictions'].value;
      const dietaryArray = dietaryRaw
        .split(',')
        .map(s => s.trim())
        .filter(Boolean);

      const payload = {
        name: profileForm.elements['name'].value.trim(),
        location: profileForm.elements['location'].value.trim(),
        age: parseInt(profileForm.elements['age'].value) || null,
        gender: profileForm.elements['gender'].value,
        fitness_level: profileForm.elements['fitness_level'].value,
        weight_kg: parseFloat(profileForm.elements['weight_kg'].value) || null,
        height_cm: parseFloat(profileForm.elements['height_cm'].value) || null,
        goal: profileForm.elements['goal'].value.trim(),
        dietary_restrictions: dietaryArray,
      };

      try {
        const res = await fetch('/api/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('Failed to update profile');
        const updated = await res.json();
        appState.profile = updated;
        populateProfileUI(updated);
        loadRawMemory();
        showToast('Profile updated successfully!', 'success');
        if (statusEl) {
          statusEl.textContent = 'Saved!';
          statusEl.className = 'save-status-msg success';
          setTimeout(() => { statusEl.textContent = ''; }, 3000);
        }
      } catch (err) {
        console.error(err);
        showToast('Error saving profile changes.', 'error');
        if (statusEl) {
          statusEl.textContent = 'Error saving';
          statusEl.className = 'save-status-msg error';
        }
      }
    });
  }

  // Log Weight Form
  const weightForm = document.getElementById('form-log-weight');
  if (weightForm) {
    weightForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const weightVal = parseFloat(document.getElementById('weight-input-val').value);
      if (isNaN(weightVal)) return;

      try {
        const res = await fetch('/api/progress/weight', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ weight_kg: weightVal }),
        });
        if (!res.ok) throw new Error('Failed to log weight');
        closeModal('modal-log-weight');
        showToast(`Weight recorded: ${weightVal} kg`, 'success');
        weightForm.reset();
        await loadAllDashboardData();
      } catch (err) {
        showToast('Failed to log weight.', 'error');
      }
    });
  }

  // Log Meal Form
  const mealForm = document.getElementById('form-log-meal');
  if (mealForm) {
    mealForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        meal_type: document.getElementById('meal-type-input').value,
        total_calories: parseInt(document.getElementById('meal-calories-input').value) || 0,
        foods: document.getElementById('meal-foods-input').value,
        protein_g: parseFloat(document.getElementById('meal-p-input').value) || 0,
        carbs_g: parseFloat(document.getElementById('meal-c-input').value) || 0,
        fat_g: parseFloat(document.getElementById('meal-f-input').value) || 0,
      };

      try {
        const res = await fetch('/api/meals', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('Failed to log meal');
        closeModal('modal-log-meal');
        showToast('Meal logged successfully!', 'success');
        mealForm.reset();
        await loadAllDashboardData();
      } catch (err) {
        showToast('Failed to log meal.', 'error');
      }
    });
  }

  // Log Workout Form
  const workoutForm = document.getElementById('form-log-workout');
  if (workoutForm) {
    workoutForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const rows = document.querySelectorAll('.exercise-input-row');
      const exercises = [];
      rows.forEach(row => {
        const name = row.querySelector('.ex-name')?.value.trim();
        const sets = parseInt(row.querySelector('.ex-sets')?.value) || 3;
        const reps = parseInt(row.querySelector('.ex-reps')?.value) || 10;
        const weight = parseFloat(row.querySelector('.ex-weight')?.value) || 0;
        if (name) {
          exercises.push({ name, sets, reps, weight_kg: weight });
        }
      });

      const payload = {
        workout_type: document.getElementById('workout-type-input').value,
        duration_min: parseInt(document.getElementById('workout-duration-input').value) || 45,
        exercises,
        notes: document.getElementById('workout-notes-input').value.trim(),
      };

      try {
        const res = await fetch('/api/workouts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('Failed to log workout');
        closeModal('modal-log-workout');
        showToast('Workout session logged!', 'success');
        workoutForm.reset();
        await loadAllDashboardData();
      } catch (err) {
        showToast('Failed to log workout.', 'error');
      }
    });
  }

  // Dynamic Exercise Row Add/Remove
  document.getElementById('btn-add-exercise-row')?.addEventListener('click', () => {
    const container = document.getElementById('exercise-rows-container');
    if (!container) return;
    const row = document.createElement('div');
    row.className = 'exercise-input-row';
    row.innerHTML = `
      <input type="text" placeholder="Exercise name" class="form-input ex-name" required>
      <input type="number" placeholder="Sets" class="form-input ex-sets" style="width: 75px;" value="3" min="1">
      <input type="number" placeholder="Reps" class="form-input ex-reps" style="width: 75px;" value="10" min="1">
      <input type="number" placeholder="Weight (kg)" class="form-input ex-weight" style="width: 105px;" value="60" min="0" step="0.5">
      <button type="button" class="btn-remove-row" title="Remove">&times;</button>
    `;
    container.appendChild(row);
    row.querySelector('.btn-remove-row').addEventListener('click', () => row.remove());
  });

  // Attach remove to initial row
  document.querySelectorAll('.btn-remove-row').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const row = e.target.closest('.exercise-input-row');
      const container = document.getElementById('exercise-rows-container');
      if (container && container.children.length > 1) {
        row.remove();
      }
    });
  });

  // Refresh Memory button
  document.getElementById('btn-refresh-memory')?.addEventListener('click', () => {
    loadRawMemory();
    showToast('Memory inspector reloaded.', 'info');
  });

  // Reset Memory button
  document.getElementById('btn-reset-memory')?.addEventListener('click', async () => {
    const confirmReset = confirm('Are you sure you want to reset memory.json to a blank slate? All logs will be erased.');
    if (!confirmReset) return;

    try {
      const res = await fetch('/api/memory/reset', { method: 'POST' });
      if (!res.ok) throw new Error('Reset failed');
      showToast('Memory reset to blank state.', 'info');
      await loadAllDashboardData();
      await loadRawMemory();
    } catch (err) {
      showToast('Reset failed.', 'error');
    }
  });

  // Re-seed Demo Data button
  document.getElementById('btn-reseed-memory')?.addEventListener('click', async () => {
    const confirmSeed = confirm('Re-seed memory with demo data for Devpreyo?');
    if (!confirmSeed) return;

    try {
      const res = await fetch('/api/memory/seed', { method: 'POST' });
      if (!res.ok) throw new Error('Seed failed');
      showToast('Memory re-seeded with demo data!', 'success');
      await loadAllDashboardData();
      await loadRawMemory();
    } catch (err) {
      showToast('Seeding failed.', 'error');
    }
  });

  // Copy JSON button
  document.getElementById('btn-copy-json')?.addEventListener('click', () => {
    const code = document.getElementById('raw-memory-json')?.textContent;
    if (code) {
      navigator.clipboard.writeText(code).then(() => {
        showToast('JSON copied to clipboard!', 'success');
      });
    }
  });
}

/* ==========================================================================
   Utilities
   ========================================================================== */
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}
window.showToast = showToast;

function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDateTime(isoString) {
  if (!isoString) return '';
  try {
    const d = new Date(isoString);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    return isoString;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeJsString(str) {
  if (!str) return '';
  return String(str).replace(/'/g, "\\'");
}
