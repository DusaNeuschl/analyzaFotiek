import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Registrácia potrebných modulov z Chart.js
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// Typ pre jednotlivé meranie
export type Measurement = {
  datetime: string;
  image_name: string;
  average_brightness: number;
  brightness_variation: number;
  shadow_percentage: number;
  heat_map_file: string;
};

// Typ pre analyzované dáta – štruktúra podľa JSON súboru
export type AnalysisData = {
  name: string;
  dates: {
    [date: string]: Measurement[];
  };
};

export type PhotoAnalysisChartProps = {
  data: AnalysisData | null;
};

export const PhotoAnalysisChart: React.FC<PhotoAnalysisChartProps> = ({ data }) => {
  if (!data || !data.dates) {
    return <p>Žiadne dáta na zobrazenie</p>;
  }

  // Zlúčenie všetkých meraní zo všetkých dní do jedného poľa
  const measurements: Measurement[] = Object.values(data.dates).flat();

  // Zoradenie meraní podľa času
  measurements.sort(
    (a, b) => new Date(a.datetime).getTime() - new Date(b.datetime).getTime()
  );

  // Vytvorenie labelov (časové značky) a datasetov pre jednotlivé metriky
  const labels = measurements.map((m) =>
    new Date(m.datetime).toLocaleString()
  );
  const avgBrightness = measurements.map((m) => m.average_brightness);
  const brightnessVariation = measurements.map((m) => m.brightness_variation);
  const shadowPercentage = measurements.map((m) => m.shadow_percentage);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Priemerná jasnosť',
        data: avgBrightness,
        fill: false,
        borderColor: 'rgba(75,192,192,1)',
        tension: 0.1,
      },
      {
        label: 'Variabilita jasu',
        data: brightnessVariation,
        fill: false,
        borderColor: 'rgba(255,159,64,1)',
        tension: 0.1,
      },
      {
        label: 'Percento tieňov',
        data: shadowPercentage,
        fill: false,
        borderColor: 'rgba(153,102,255,1)',
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      title: { display: true, text: `Analýza dát z fotiek – ${data.name}` },
    },
    scales: {
      x: {
        title: { display: true, text: 'Čas' },
      },
      y: {
        title: { display: true, text: 'Hodnota' },
      },
    },
  };

  return <Line data={chartData} options={options} />;
};
