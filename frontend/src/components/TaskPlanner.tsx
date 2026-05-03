import { useState } from 'react';
import client from '../api/client';
import type { TaskItem, TaskPlanResponse, PlannedTask } from '../utils/constants';

interface Props {
  days: number;
}

export default function TaskPlanner({ days }: Props) {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [taskName, setTaskName] = useState('');
  const [taskDuration, setTaskDuration] = useState(60);
  const [taskPriority, setTaskPriority] = useState<'high' | 'medium' | 'low'>('medium');
  const [result, setResult] = useState<TaskPlanResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const addTask = () => {
    if (!taskName.trim()) return;
    setTasks(prev => [...prev, { name: taskName.trim(), duration_minutes: taskDuration, priority: taskPriority }]);
    setTaskName('');
    setTaskDuration(60);
    setTaskPriority('medium');
  };

  const removeTask = (idx: number) => {
    setTasks(prev => prev.filter((_, i) => i !== idx));
  };

  const handlePlan = async () => {
    if (tasks.length === 0) return;
    setLoading(true);
    try {
      const { data } = await client.post('/analytics/plan', { tasks, days });
      setResult(data);
    } catch (err) {
      console.error('Planning failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const priorityLabels: Record<string, string> = { high: 'Wysoki', medium: 'Średni', low: 'Niski' };
  const priorityColors: Record<string, string> = { high: 'var(--energy-1)', medium: 'var(--accent)', low: 'var(--text-muted)' };

  return (
    <div className="card">
      <h3 className="card-title" style={{ marginBottom: '1rem' }}>Planer zadań</h3>

      {/* Task input */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
        <input
          className="input"
          style={{ flex: 2, minWidth: 180 }}
          placeholder="Nazwa zadania..."
          value={taskName}
          onChange={e => setTaskName(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && addTask()}
          maxLength={100}
        />
        <select
          className="input"
          style={{ flex: 0, minWidth: 90 }}
          value={taskDuration}
          onChange={e => setTaskDuration(Number(e.target.value))}
        >
          <option value={30}>30 min</option>
          <option value={60}>1 godz</option>
          <option value={90}>1.5 godz</option>
          <option value={120}>2 godz</option>
          <option value={180}>3 godz</option>
          <option value={240}>4 godz</option>
        </select>
        <select
          className="input"
          style={{ flex: 0, minWidth: 100 }}
          value={taskPriority}
          onChange={e => setTaskPriority(e.target.value as 'high' | 'medium' | 'low')}
        >
          <option value="high">Wysoki</option>
          <option value="medium">Średni</option>
          <option value="low">Niski</option>
        </select>
        <button className="btn btn-secondary" onClick={addTask} disabled={!taskName.trim()}>
          Dodaj
        </button>
      </div>

      {/* Task list */}
      {tasks.length > 0 && (
        <div style={{ marginBottom: '1rem' }}>
          {tasks.map((t, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem 0',
              borderBottom: '1px solid var(--border)',
            }}>
              <span style={{ flex: 1, fontSize: '0.85rem' }}>{t.name}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.duration_minutes} min</span>
              <span style={{
                fontSize: '0.7rem', fontWeight: 600, padding: '0.15rem 0.5rem',
                borderRadius: 12, border: `1px solid ${priorityColors[t.priority]}`,
                color: priorityColors[t.priority],
              }}>
                {priorityLabels[t.priority]}
              </span>
              <button className="btn btn-danger btn-sm" onClick={() => removeTask(i)}>×</button>
            </div>
          ))}

          <button
            className="btn btn-primary"
            onClick={handlePlan}
            disabled={loading}
            style={{ width: '100%', marginTop: '0.75rem' }}
          >
            {loading ? 'Planuję...' : `Zaplanuj ${tasks.length} zadań`}
          </button>
        </div>
      )}

      {tasks.length === 0 && !result && (
        <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', textAlign: 'center', padding: '1rem 0' }}>
          Dodaj zadania, a system ułoży je w optymalnej kolejności na podstawie Twoich wzorców energii.
        </p>
      )}

      {/* Results */}
      {result && (
        <div style={{ marginTop: '0.5rem' }}>
          <div className="insight-card" style={{ marginBottom: '1rem' }}>
            <div className="insight-content">
              <h3>Plan</h3>
              <p>{result.summary}</p>
            </div>
          </div>

          {result.planned_tasks.length > 0 && (
            <div className="schedule-timeline">
              {result.planned_tasks.map((t, i) => (
                <div key={i} className={`schedule-block ${t.zone}`}>
                  <span className="schedule-hour">
                    {t.start_hour.toString().padStart(2, '0')}:00–{t.end_hour.toString().padStart(2, '0')}:00
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{t.name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.reason}</div>
                  </div>
                  <span style={{
                    fontSize: '0.7rem', fontWeight: 600, padding: '0.15rem 0.5rem',
                    borderRadius: 12, border: `1px solid ${priorityColors[t.priority]}`,
                    color: priorityColors[t.priority],
                  }}>
                    {priorityLabels[t.priority]}
                  </span>
                </div>
              ))}
            </div>
          )}

          {result.unplanned_tasks.length > 0 && (
            <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(181,90,74,0.08)', borderRadius: 'var(--radius-sm)', fontSize: '0.82rem' }}>
              <span style={{ fontWeight: 600, color: 'var(--danger)' }}>Nie zmieściły się: </span>
              {result.unplanned_tasks.join(', ')}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
