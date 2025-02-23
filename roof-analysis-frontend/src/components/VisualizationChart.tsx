import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

type SummaryData = {
  [section: string]: {
    dates: string[];
    total_measurements: number;
  }
};

type VisualizationChartProps = {
  data: SummaryData;
};

export const VisualizationChart: React.FC<VisualizationChartProps> = ({ data }) => {
  const labels = Object.keys(data);
  const totalMeasurements = labels.map(label => data[label].total_measurements);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Celkový počet meraní',
        data: totalMeasurements,
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
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
        text: 'Celkový počet meraní pre jednotlivé sekcie strechy',
      },
    },
  };

  return <Bar data={chartData} options={options} />;
};
