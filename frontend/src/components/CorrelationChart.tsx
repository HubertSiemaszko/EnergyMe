import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import type { CorrelationResponse } from '../utils/constants';
import { getActivityLabel, ENERGY_COLORS } from '../utils/constants';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

interface Props {
  data: CorrelationResponse;
}

export default function CorrelationChart({ data }: Props) {
  const { activity_correlations, emotion_correlations, global_avg_energy } = data;

  if (activity_correlations.length === 0) {
    return (
      <div className="card">
        <h3 className="card-title">Korelacje</h3>
        <div className="empty-state"><p>Za mało danych do analizy korelacji.</p></div>
      </div>
    );
  }

  const sorted = [...activity_correlations].sort((a, b) => b.avg_energy - a.avg_energy);

  const chartData = {
    labels: sorted.map(c => getActivityLabel(c.activity)),
    datasets: [{
      label: 'Średnia energia',
      data: sorted.map(c => c.avg_energy),
      backgroundColor: sorted.map(c => {
        if (c.avg_energy >= 4) return ENERGY_COLORS[5];
        if (c.avg_energy >= 3.5) return ENERGY_COLORS[4];
        if (c.avg_energy >= 2.5) return ENERGY_COLORS[3];
        if (c.avg_energy >= 1.5) return ENERGY_COLORS[2];
        return ENERGY_COLORS[1];
      }),
      borderRadius: 4,
      borderSkipped: false,
    }],
  };

  const chartOptions = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { min: 0, max: 5, ticks: { color: '#7a6350' }, grid: { color: 'rgba(176,154,130,0.06)' } },
      y: { ticks: { color: '#b09a82', font: { size: 11 } }, grid: { display: false } },
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          afterLabel: (context: any) => {
            const item = sorted[context.dataIndex];
            return [`Delta: ${item.delta_energy > 0 ? '+' : ''}${item.delta_energy.toFixed(2)}`, `Pomiarów: ${item.count}`];
          },
        },
      },
    },
  };

  return (
    <div className="card">
      <h3 className="card-title" style={{ marginBottom: '0.5rem' }}>Korelacje aktywność — energia</h3>
      <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
        Średnia globalna: {global_avg_energy.toFixed(2)}
      </p>

      <div style={{ height: Math.max(200, sorted.length * 36) }}>
        <Bar data={chartData} options={chartOptions} />
      </div>

      {sorted.slice(0, 3).map(item => (
        <div key={item.activity} className="insight-card" style={{ marginTop: '0.75rem' }}>
          <div className="insight-content">
            <h3>{getActivityLabel(item.activity)}</h3>
            <p>{item.insight}</p>
          </div>
        </div>
      ))}

      {emotion_correlations.length > 0 && (
        <div style={{ marginTop: '1.5rem' }}>
          <h4 style={{ fontSize: '0.78rem', fontWeight: 500, marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
            Emocje — energia
          </h4>
          <div className="correlation-bar-container">
            {emotion_correlations.slice(0, 6).map(em => (
              <div key={em.emotion} className="correlation-item">
                <span className="correlation-label">{em.emotion}</span>
                <div className="correlation-bar-bg">
                  <div className="correlation-bar" style={{
                    width: `${(em.avg_energy / 5) * 100}%`,
                    backgroundColor: em.avg_energy >= 3.5 ? 'var(--energy-4)' : em.avg_energy >= 2.5 ? 'var(--energy-3)' : 'var(--energy-1)',
                  }}>
                    {em.avg_energy.toFixed(1)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
