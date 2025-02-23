import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
// *** Import nových alert komponentov
import { ErrorAlert } from './ui/ErrorAlert';
import { SuccessAlert } from './ui/SuccessAlert';

export const ImportAnalysis = () => {
  const [photosDir, setPhotosDir] = useState('D:\\napady\\fotky\\Photos');
  const [dataDir, setDataDir] = useState('D:\\napady\\fotky\\AnalysisData');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (log: string) => {
    setLogs((prevLogs) => [
      ...prevLogs,
      `${new Date().toLocaleTimeString()}: ${log}`,
    ]);
  };

  const handleRename = async () => {
    setIsLoading(true);
    setError(null);
    setMessage(null);
    addLog('Začínam premenovanie fotografií...');

    try {
      const response = await fetch('http://localhost:5000/api/rename', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ photos_dir: photosDir }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Chyba pri premenovaní fotografií');
      }

      setMessage(data.status);
      addLog(`Premenovanie dokončené: ${data.status}`);

      // Pridanie logov z backendu
      if (data.logs) {
        data.logs.forEach((log: string) => addLog(log));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Neznáma chyba';
      setError(errorMessage);
      addLog(`Chyba: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyze = async (force: boolean = false) => {
    setIsLoading(true);
    setError(null);
    setMessage(null);
    addLog(`Začínam analýzu fotografií${force ? ' (vynútená)' : ''}...`);

    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          photos_dir: photosDir,
          data_dir: dataDir,
          force,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Chyba pri analýze fotografií');
      }

      setMessage(data.status);
      addLog(`Analýza dokončená: ${data.status}`);

      // Pridanie logov z backendu
      if (data.logs) {
        data.logs.forEach((log: string) => addLog(log));
      }

      if (data.summary) {
        addLog('Sumár analýzy:');
        Object.entries(data.summary).forEach(([section, info]: [string, any]) => {
          addLog(`  ${section}:`);
          addLog(`    - Počet dní: ${info.dates.length}`);
          addLog(`    - Celkový počet meraní: ${info.total_measurements}`);
        });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Neznáma chyba';
      setError(errorMessage);
      addLog(`Chyba: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="flex p-4 gap-4 min-h-[calc(100vh-64px)]">
      {/* Ľavý panel s ovládacími prvkami */}
      <div className="w-1/2">
        <Card>
          <CardHeader>
            <CardTitle>Analýza fotografií strechy</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Adresár s fotografiami:
                </label>
                <input
                  type="text"
                  value={photosDir}
                  onChange={(e) => setPhotosDir(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Adresár pre analýzy:
                </label>
                <input
                  type="text"
                  value={dataDir}
                  onChange={(e) => setDataDir(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>

              <div className="flex gap-4">
                <button
                  onClick={handleRename}
                  disabled={isLoading}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
                >
                  {isLoading ? 'Spracovávam...' : 'Premenovať fotografie'}
                </button>

                <button
                  onClick={() => handleAnalyze(false)}
                  disabled={isLoading}
                  className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50"
                >
                  {isLoading ? 'Spracovávam...' : 'Analyzovať fotografie'}
                </button>

                <button
                  onClick={() => handleAnalyze(true)}
                  disabled={isLoading}
                  className="px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 disabled:opacity-50"
                >
                  {isLoading ? 'Spracovávam...' : 'Vynútiť analýzu'}
                </button>
              </div>

              {/* *** Použitie nových komponentov na chyby a úspešné správy *** */}
              <ErrorAlert error={error} />
              <SuccessAlert message={message} />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pravý panel s logmi */}
      <div className="w-1/2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Logy</CardTitle>
            <button
              onClick={clearLogs}
              className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Vyčistiť logy
            </button>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-100 p-4 rounded-md h-[600px] overflow-y-auto font-mono text-sm">
              {logs.map((log, index) => (
                <div key={index} className="whitespace-pre-wrap">
                  {log}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
