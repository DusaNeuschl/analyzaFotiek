import { useState, useEffect } from 'react';
import { Navigation } from '../components/Navigation';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { PhotoAnalysisChart, AnalysisData } from '../components/PhotoAnalysisChart';
import { HeatMapDisplay } from '../components/HeatMapDisplay';

const PhotoAnalysisPage = () => {
  const [data, setData] = useState<AnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [heatMapFile, setHeatMapFile] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAnalysis() {
      try {
        const res = await fetch("http://localhost:5000/api/illumination");
        if (!res.ok) {
          throw new Error("Chyba pri načítaní dát z analýzy fotiek");
        }
        const json = await res.json();
        // Vyberáme dáta pre sekciu "Východo-juhovýchodná strana (109°)"
        const sectionData = json["Východo-juhovýchodná strana (109°)"];
        if (!sectionData) {
          throw new Error("Dáta pre požadovanú sekciu neboli nájdené");
        }
        setData(sectionData);
        // Ak existuje aspoň jedno meranie, nastavíme heat map file z prvého merania dňa
        const days = Object.keys(sectionData.dates);
        if (days.length > 0 && sectionData.dates[days[0]].length > 0) {
          setHeatMapFile(sectionData.dates[days[0]][0].heat_map_file);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Neznáma chyba";
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    }
    fetchAnalysis();
  }, []);

  return (
    <div>
      <Navigation />
      <div className="container mx-auto p-4">
        <Card>
          <CardHeader>
            <CardTitle>Analýza dát z fotiek</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div>Načítavam dáta...</div>
            ) : error ? (
              <div className="text-red-600">{error}</div>
            ) : data ? (
              <div>
                <PhotoAnalysisChart data={data} />
                <pre className="mt-4">{JSON.stringify(data, null, 2)}</pre>
                {heatMapFile && (
                  <HeatMapDisplay filename={heatMapFile} />
                )}
              </div>
            ) : (
              <div>Žiadne dáta.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PhotoAnalysisPage;
