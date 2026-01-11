(() => {
  const API = window.location.origin + '/api';

  async function jsonFetch(url) {
    const token = window.TimeNestAuth?.getToken?.();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(url, { headers });
    let data = null; try { data = await res.json(); } catch {}
    return { ok: res.ok, status: res.status, data };
  }

  async function init() {
    const [tasksRes, habitsRes] = await Promise.all([
      jsonFetch(`${API}/tasks/`),
      jsonFetch(`${API}/habits/`)
    ]);
    
    const tasks = tasksRes.ok ? (tasksRes.data?.items || []) : [];
    const habits = habitsRes.ok ? (habitsRes.data?.items || []) : [];
    
    const today = new Date().toISOString().slice(0,10);
    const dueToday = tasks.filter(t => (t.due_date || '').slice(0,10) === today && !t.completed).length;
    const completedCount = tasks.filter(t => t.completed).length;
    const maxStreak = habits.reduce((m,h) => Math.max(m, h.streak||0), 0);
    
    document.getElementById('tasks-today').textContent = dueToday;
    document.getElementById('active-habits').textContent = habits.length;
    document.getElementById('max-streak').textContent = maxStreak ? `${maxStreak} 🔥` : '0';
    document.getElementById('completed-tasks').textContent = completedCount;
    
    // Today's focus
    const focus = document.getElementById('today-focus');
    const highPriority = tasks.filter(t => !t.completed && t.priority === 'high').slice(0, 3);
    if (highPriority.length > 0) {
      focus.innerHTML = '<strong>High Priority Tasks:</strong><ul style="margin-top:0.5rem;padding-left:1.5rem;">' + 
        highPriority.map(t => `<li>${t.title}</li>`).join('') + '</ul>';
    } else if (dueToday > 0) {
      focus.textContent = `You have ${dueToday} task${dueToday !== 1 ? 's' : ''} due today!`;
    } else {
      focus.textContent = '✨ All caught up! Great job.';
    }
  }

  window.addEventListener('DOMContentLoaded', init);
})();
