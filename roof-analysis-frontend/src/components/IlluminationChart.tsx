// src/components/IlluminationChart.tsx
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

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// Typy pre merania
type Measurement = {
  datetime: string;
  image_name: string;
  average_brightness: number;
  brightness_variation: number;
  shadow_percentage: number;
  heat_map_file: string;
};

type AnalysisData = {
  name: string;
  dates: {
    [date: string]: Measurement[];
  };
};

type IlluminationChartProps = {
  data: AnalysisData;
};

export const IlluminationChart: React.FC<IlluminationChartProps> = ({ data }) => {
  // Zlúčenie všetkých meraní zo všetkých dní do jedného poľa
  const measurements: Measurement[] = Object.values(data.dates).flat();

  // Zoradenie meraní podľa času
  measurements.sort(
    (a, b) => new Date(a.datetime).getTime() - new Date(b.datetime).getTime()
  );

  // Vytvorenie labelov (časové značky) a dát (priemerná jasnosť)
  const labels = measurements.map((m) =>
    new Date(m.datetime).toLocaleString()
  );
  const brightnessData = measurements.map(
    (m) => m.average_brightness
  );

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Priemerná jasnosť',
        data: brightnessData,
        fill: false,
        borderColor: 'rgba(75,192,192,1)',
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `Vývoj osvetlenia pre ${data.name}`,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Čas',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Priemerná jasnosť',
        },
      },
    },
  };

  return <Line data={chartData} options={options} />;
};
