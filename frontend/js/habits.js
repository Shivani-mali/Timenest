(() => {
  const API = window.location.origin + '/api';

  async function jsonFetch(url, options = {}) {
    const token = window.TimeNestAuth?.getToken?.();
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(url, { headers, ...options });
    let body = null;
    try { body = await res.json(); } catch (_) {}
    return { status: res.status, ok: res.ok, data: body };
  }

  async function listHabits() {
    return jsonFetch(`${API}/habits/`);
  }

  async function createHabit(payload) {
    return jsonFetch(`${API}/habits/`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async function completeHabit(habitId) {
    return jsonFetch(`${API}/habits/${habitId}/complete`, {
      method: 'POST',
    });
  }

  async function init() {
    const container = document.getElementById('habits');
    const form = document.getElementById('habit-form');
    const render = async () => {
      const res = await listHabits();
      if (!res.ok) {
        container.textContent = res.data?.error || `Failed to load habits (${res.status})`;
        return;
      }
      const items = res.data?.items || [];
      container.innerHTML = items.map(h => {
        const streakEmoji = h.streak >= 7 ? '🔥' : h.streak >= 3 ? '⭐' : '✨';
        const lastCompleted = h.last_completed_at ? new Date(h.last_completed_at).toLocaleDateString() : 'Never';
        return `
        <div class="habit-item" data-id="${h.id}">
          <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:0.5rem;">
            <strong>${h.name}</strong>
            <span class="badge" style="background:linear-gradient(135deg,var(--primary),var(--success));">
              ${streakEmoji} ${h.streak} day${h.streak !== 1 ? 's' : ''}
            </span>
          </div>
          <div class="muted" style="font-size:0.85rem;">
            Frequency: ${h.frequency} • Last: ${lastCompleted}
          </div>
          <div class="btn-group">
            <button class="success" data-action="complete" data-id="${h.id}">✓ Complete Today</button>
            <button class="danger" data-action="delete" data-id="${h.id}">🗑️ Delete</button>
          </div>
        </div>
      `}).join('');
      
      container.querySelectorAll('button[data-action="complete"]').forEach(btn => {
        btn.addEventListener('click', async (e) => {
          const id = e.currentTarget.getAttribute('data-id');
          const res = await completeHabit(id);
          if (res.ok) {
            await render();
            if (res.data?.message) {
              alert(res.data.message);
            }
          } else {
            alert(res.data?.error || `Complete failed (${res.status})`);
          }
        });
      });
      
      container.querySelectorAll('button[data-action="delete"]').forEach(btn => {
        btn.addEventListener('click', async (e) => {
          if (!confirm('Delete this habit?')) return;
          const id = e.currentTarget.getAttribute('data-id');
          const res = await jsonFetch(`${API}/habits/${id}`, { method: 'DELETE' });
          if (res.ok) await render();
          else alert(res.data?.error || `Delete failed (${res.status})`);
        });
      });
    };

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('h-name').value;
      const frequency = document.getElementById('h-frequency').value;
      const res = await createHabit({ name, frequency });
      if (res.ok) {
        (e.target).reset();
        await render();
      } else {
        alert(res.data?.error || `Create failed (${res.status})`);
      }
    });

    await render();
  }

  window.addEventListener('DOMContentLoaded', init);
})();
