// src/pages/illumination.tsx
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Navigation } from '../components/Navigation';
import { IlluminationChart } from '../components/IlluminationChart';

const IlluminationPage = () => {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchIllumination() {
      try {
        // Načítanie dát z BE endpointu /api/illumination
        const res = await fetch("http://localhost:5000/api/illumination");
        if (!res.ok) {
          throw new Error("Chyba pri načítaní dát z analýzy osvetlenia");
        }
        const json = await res.json();
        setData(json);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Neznáma chyba";
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    }
    fetchIllumination();
  }, []);

  return (
    <div>
      <Navigation />
      <div className="container mx-auto p-4">
        <Card>
          <CardHeader>
            <CardTitle>Analýza osvetlenia strechy</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div>Načítavam dáta...</div>
            ) : error ? (
              <div className="text-red-600">{error}</div>
            ) : (
              <div>
                <IlluminationChart data={data} />
                <pre className="mt-4">{JSON.stringify(data, null, 2)}</pre>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default IlluminationPage;
