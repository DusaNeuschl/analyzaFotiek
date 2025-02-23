import { useState, useEffect } from 'react';
import { Navigation } from '../components/Navigation';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { PhotoAnalysisChart } from '../components/PhotoAnalysisChart';

const PhotoAnalysisPage = () => {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAnalysis() {
      try {
        // Upravte URL endpointu podľa vašej konfigurácie
        const res = await fetch("http://localhost:5000/api/illumination");
        if (!res.ok) {
          throw new Error("Chyba pri načítaní dát z analýzy fotiek");
        }
        const json = await res.json();
        // Ak endpoint vracia dáta pre viacero sekcií, vyberte tú, ktorú chcete zobrazovať.
        // Napríklad, ak chcete zobraziť dáta pre "Východo-juhovýchodná strana (109°)":
        setData(json["Východo-juhovýchodná strana (109°)"]);
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
