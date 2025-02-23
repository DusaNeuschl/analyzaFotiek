// src/components/HeatMapDisplay.tsx
import React from 'react';

type HeatMapDisplayProps = {
  filename: string;
};

export const HeatMapDisplay: React.FC<HeatMapDisplayProps> = ({ filename }) => {
  // Konštrukcia URL pre načítanie heat mapy z BE
  const imageUrl = `http://localhost:5000/api/heatmap/${filename}`;

  return (
    <div>
      <h3>Heat Map: {filename}</h3>
      <img src={imageUrl} alt={`Heat map ${filename}`} style={{ maxWidth: '100%' }} />
    </div>
  );
};
