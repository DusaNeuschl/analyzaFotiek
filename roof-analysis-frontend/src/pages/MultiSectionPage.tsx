// src/pages/multi-sections.tsx
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Navigation } from '../components/Navigation';
import { SingleSectionChart } from '../components/SingleSectionChart';

const MultiSectionPage = () => {
  const [sectionsData, setSectionsData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSections() {
      try {
        // Zavolajte BE endpoint, ktorý vracia všetky sekcie v JSON
        const res = await fetch('http://localhost:5000/api/illumination');
        if (!res.ok) {
          throw new Error('Chyba pri načítaní dát z analýzy osvetlenia');
        }
        const json = await res.json();
        setSectionsData(json);
        // Predvolene vyberieme prvú sekciu, ak existuje
        const keys = Object.keys(json);
        if (keys.length > 0) {
          setSelectedSection(keys[0]);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Neznáma chyba';
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    }
    fetchSections();
  }, []);

  const handleSectionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedSection(e.target.value);
  };

  return (
    <div>
      <Navigation />
      <div className="container mx-auto p-4">
        <Card>
          <CardHeader>
            <CardTitle>Vizualizácia Osvetlenia - Viac Sekcií</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div>Načítavam dáta...</div>
            ) : error ? (
              <div className="text-red-600">{error}</div>
            ) : sectionsData ? (
              <div>
                {/* Rozbaľovací zoznam na výber sekcie */}
                <div className="mb-4">
                  <label className="mr-2 font-semibold">Vyberte sekciu:</label>
                  <select
                    value={selectedSection || ''}
                    onChange={handleSectionChange}
                    className="border p-1"
                  >
                    {Object.keys(sectionsData).map((section) => (
                      <option key={section} value={section}>
                        {section}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Zobrazenie grafu len pre vybranú sekciu */}
                {selectedSection && (
                  <SingleSectionChart
                    sectionName={selectedSection}
                    data={sectionsData[selectedSection]}
                  />
                )}

                {/* Pre kontrolu aj JSON výstup */}
                <pre className="mt-4">
                  {JSON.stringify(sectionsData[selectedSection || ''], null, 2)}
                </pre>
              </div>
            ) : (
              <div>Žiadne dáta neboli načítané.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MultiSectionPage;
