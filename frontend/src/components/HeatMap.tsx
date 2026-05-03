import type { HeatmapCell } from '../utils/constants';
import { ENERGY_COLORS, DAY_NAMES } from '../utils/constants';

interface Props {
  cells: HeatmapCell[];
}

function getHeatColor(avg: number): string {
  if (avg >= 4.5) return ENERGY_COLORS[5];
  if (avg >= 3.5) return ENERGY_COLORS[4];
  if (avg >= 2.5) return ENERGY_COLORS[3];
  if (avg >= 1.5) return ENERGY_COLORS[2];
  return ENERGY_COLORS[1];
}

export default function HeatMap({ cells }: Props) {
  const hours = Array.from({ length: 17 }, (_, i) => i + 6);

  const getCellData = (dow: number, hour: number): HeatmapCell | undefined => {
    return cells.find(c => c.day_of_week === dow && c.hour === hour);
  };

  if (cells.length === 0) {
    return (
      <div className="card">
        <h3 className="card-title">Heatmapa tygodniowa</h3>
        <div className="empty-state"><p>Za mało danych. Dodawaj check-iny przez kilka dni.</p></div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="card-title" style={{ marginBottom: '1rem' }}>Heatmapa tygodniowa</h3>
      <div className="heatmap-grid">
        <div className="heatmap-label"></div>
        {hours.map(h => (
          <div key={h} className="heatmap-label">{h}</div>
        ))}

        {DAY_NAMES.map((day, dow) => (
          <div key={`row-${dow}`} style={{ display: 'contents' }}>
            <div className="heatmap-label">{day}</div>
            {hours.map(hour => {
              const cell = getCellData(dow, hour);
              return (
                <div
                  key={`${dow}-${hour}`}
                  className="heatmap-cell"
                  style={{
                    backgroundColor: cell ? getHeatColor(cell.avg_energy) : 'var(--bg-input)',
                    opacity: cell ? 1 : 0.2,
                  }}
                  title={cell ? `${day} ${hour}:00 — ${cell.avg_energy.toFixed(1)} (${cell.count})` : `${day} ${hour}:00`}
                >
                  {cell ? cell.avg_energy.toFixed(1) : ''}
                </div>
              );
            })}
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', marginTop: '1rem', fontSize: '0.7rem' }}>
        {[1, 2, 3, 4, 5].map(level => (
          <div key={level} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <div style={{ width: 10, height: 10, borderRadius: 2, backgroundColor: ENERGY_COLORS[level] }} />
            <span style={{ color: 'var(--text-muted)' }}>{level}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
