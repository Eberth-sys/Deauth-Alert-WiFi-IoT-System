import { useEffect, useState } from 'react';

const LogViewer = () => {
  const [logFiles, setLogFiles] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [logContent, setLogContent] = useState<string>('');

  const backendBaseUrl = 'http://192.168.255.132:8000';

  useEffect(() => {
    // Obtener la lista de archivos de logs
    fetch(`${backendBaseUrl}/logs/`)
      .then((res) => res.json())
      .then((data) => setLogFiles(data))
      .catch((err) => console.error('Error al obtener la lista de logs:', err));
  }, []);

  const handleFileClick = (filename: string) => {
    setSelectedFile(filename);
    // Obtener el contenido del archivo seleccionado
    fetch(`${backendBaseUrl}/logs/${filename}`)
      .then((res) => res.text())
      .then((text) => setLogContent(text))
      .catch((err) => console.error('Error al obtener el contenido del log:', err));
  };

  const handleDownload = (filename: string) => {
    // Descargar el archivo seleccionado
    fetch(`${backendBaseUrl}/logs/download/${filename}`)
      .then((res) => res.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch((err) => console.error('Error al descargar el log:', err));
  };

  return (
    <div className="flex flex-col md:flex-row gap-4">
      {/* Lista de archivos */}
      <div className="w-full md:w-1/3 bg-gray-800 p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-2">Archivos de Logs</h2>
        <ul className="space-y-2">
          {logFiles.map((filename) => (
            <li key={filename} className="flex items-center justify-between">
              <button
                onClick={() => handleFileClick(filename)}
                className="text-blue-400 hover:underline"
              >
                {filename}
              </button>
              <button
                onClick={() => handleDownload(filename)}
                className="text-green-400 hover:underline"
              >
                Descargar
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* Contenido del archivo */}
      <div className="w-full md:w-2/3 bg-gray-800 p-4 rounded-lg shadow overflow-auto">
        <h2 className="text-lg font-semibold mb-2">
          Contenido de: {selectedFile || 'Ninguno'}
        </h2>
        <pre className="whitespace-pre-wrap text-sm text-gray-200">
          {logContent || 'Selecciona un archivo para ver su contenido.'}
        </pre>
      </div>
    </div>
  );
};

export default LogViewer;
