// frontend/src/App.tsx
import AlertHeatmapTable from './components/AlertHeatmapTable'

function App() {
  return (
    /* 
      h-screen w-screen => ocupa todo el alto y ancho de la ventana
      flex flex-col => para poder ubicar el header arriba y el contenido en main
    */
    <div className="bg-gray-900 h-screen w-screen flex flex-col">
      {/* Cabecera */}
      <header className="py-6">
        <h1 className="text-4xl font-extrabold text-center text-blue-400">
          Dashboard IoT – Alertas
        </h1>
      </header>

      {/* Contenido principal */}
      <main className="flex-1 overflow-y-auto">
        {/* El overflow-y-auto permite scroll si el contenido es más grande que la pantalla */}
        <AlertHeatmapTable />
      </main>
    </div>
  )
}

export default App
