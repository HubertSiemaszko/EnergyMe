import type { ScheduleResponse } from '../utils/constants';

interface Props {
  data: ScheduleResponse;
}

export default function SmartScheduler({ data }: Props) {
  const { hourly, peak_block, dip_block, golden_hour, summary } = data;

  if (hourly.length === 0) {
    return (
      <div className="card">
        <h3 className="card-title">Smart Scheduler</h3>
        <div className="empty-state">
          <p>Za mało danych. Dodawaj check-iny, aby otrzymać plan dnia.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="card-title" style={{ marginBottom: '0.5rem' }}>Smart Scheduler</h3>

      <div className="insight-card" style={{ marginBottom: '1.5rem' }}>
        <div className="insight-content">
          <h3>Rekomendacja dnia</h3>
          <p>{summary}</p>
        </div>
      </div>

      <div className="grid grid-3" style={{ marginBottom: '1.5rem' }}>
        {golden_hour && (
          <div className="stat-card">
            <div className="stat-value">{golden_hour}</div>
            <div className="stat-label">Złota godzina</div>
          </div>
        )}
        {peak_block && (
          <div className="stat-card">
            <div className="stat-value" style={{ fontSize: '1.2rem', color: 'var(--energy-4)' }}>{peak_block}</div>
            <div className="stat-label">Deep work</div>
          </div>
        )}
        {dip_block && (
          <div className="stat-card">
            <div className="stat-value" style={{ fontSize: '1.2rem', color: 'var(--energy-1)' }}>{dip_block}</div>
            <div className="stat-label">Przerwa</div>
          </div>
        )}
      </div>

      <h4 style={{ fontSize: '0.78rem', fontWeight: 500, marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
        Optymalny plan dnia
      </h4>
      <div className="schedule-timeline">
        {hourly.map(block => (
          <div key={block.hour} className={`schedule-block ${block.zone}`}>
            <span className="schedule-hour">{block.hour.toString().padStart(2, '0')}:00</span>
            <span className="schedule-suggestion">{block.suggestion}</span>
            <span style={{
              marginLeft: 'auto', fontSize: '0.75rem', fontWeight: 600,
              color: block.zone === 'high' ? 'var(--energy-4)' : block.zone === 'medium' ? 'var(--energy-3)' : 'var(--energy-1)',
            }}>
              {block.avg_energy.toFixed(1)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
