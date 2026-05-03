import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';
import type { CheckIn } from '../utils/constants';
import { ENERGY_COLORS, getActivityLabel } from '../utils/constants';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

interface Props {
  checkins: CheckIn[];
  title?: string;
}

export default function EnergyChart({ checkins, title = 'Energia w ciągu dnia' }: Props) {
  if (checkins.length === 0) {
    return (
      <div className="card">
        <h3 className="card-title">{title}</h3>
        <div className="empty-state"><p>Brak danych. Dodaj check-in, aby zobaczyć wykres.</p></div>
      </div>
    );
  }

  const sorted = [...checkins].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  const labels = sorted.map(c => {
    const d = new Date(c.timestamp);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
  });

  const data = {
    labels,
    datasets: [
      {
        label: 'Energia',
        data: sorted.map(c => c.energy_level),
        borderColor: '#c49a6c',
        backgroundColor: 'rgba(196, 154, 108, 0.08)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: sorted.map(c => ENERGY_COLORS[c.energy_level]),
        pointBorderColor: sorted.map(c => ENERGY_COLORS[c.energy_level]),
        pointRadius: 6,
        pointHoverRadius: 9,
        borderWidth: 2,
      },
      {
        label: 'Fokus',
        data: sorted.map(c => c.focus_level),
        borderColor: '#7a6350',
        fill: false,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 7,
        borderWidth: 1.5,
        borderDash: [4, 4],
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: { min: 0, max: 5.5, ticks: { stepSize: 1, color: '#7a6350' }, grid: { color: 'rgba(176,154,130,0.06)' } },
      x: { ticks: { color: '#7a6350' }, grid: { color: 'rgba(176,154,130,0.03)' } },
    },
    plugins: {
      legend: { labels: { color: '#b09a82' } },
      tooltip: {
        callbacks: {
          afterLabel: (context: any) => {
            const c = sorted[context.dataIndex];
            const lines: string[] = [`Aktywność: ${getActivityLabel(c.activity)}`];
            if (c.emotions?.length) lines.push(`Emocje: ${c.emotions.join(', ')}`);
            if (c.note) lines.push(`Notatka: ${c.note}`);
            return lines;
          },
        },
      },
    },
  };

  return (
    <div className="card">
      <h3 className="card-title">{title}</h3>
      <div style={{ height: 280 }}>
        <Line data={data} options={options} />
      </div>
    </div>
  );
}
