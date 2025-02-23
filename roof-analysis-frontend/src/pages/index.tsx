// src/pages/index.tsx
import { ImportAnalysis } from '../components/ImportAnalysis';
import { Navigation } from '../components/Navigation';

export default function Home() {
  return (
    <div>
      <Navigation />
      <ImportAnalysis />
    </div>
  );
}