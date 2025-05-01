//frontend\src\App.tsx

// -------------------- Importaciones --------------------
import DashboardPage from "./pages/DashboardPage";      // Página principal del panel
import Footer from "./components/Footer";                // Footer reutilizable
import LogoutButton from "./components/LogoutButton";    // Botón de cierre de sesión visible en pantalla

// -------------------- Componente principal --------------------
function App() {
  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col font-inter text-gray-100">
      
      {/* 🧭 Header fijo superior con título y botón de logout */}
      <header className="sticky top-0 z-40 bg-gray-900/80 backdrop-blur border-b border-gray-800 py-4 shadow-md relative">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-center text-blue-400">
          🛜 Monitor de seguridad Wi-Fi 2,4 Ghz 🔐
        </h1>
        <LogoutButton />  {/* Botón logout arriba a la derecha */}
      </header>

      {/* 📦 Contenido principal del dashboard */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-screen-xl mx-auto px-4 sm:px-8 py-6">
          <DashboardPage />
        </div>
      </main>

      {/* 🧭 Botones flotantes para escritorio (solo visibles en sm+) */}
      <div className="fixed z-50 right-6 top-24 flex flex-col gap-3 sm:flex hidden">
        <a
          href="/logs"
          className="flex items-center gap-2 bg-white text-gray-800 px-4 py-2 rounded-full shadow-lg font-semibold hover:bg-gray-200 transition-all duration-300"
        >
          <span className="text-lg">📜</span>
          <span>Ver BLE logs</span>
        </a>
        <a
          href="/reportes"
          className="flex items-center gap-2 bg-white text-gray-800 px-4 py-2 rounded-full shadow-lg font-semibold hover:bg-gray-200 transition-all duration-300"
        >
          <span className="text-lg">📅</span>
          <span>Ver reportes</span>
        </a>
        <a
          href="/estadisticas"
          className="flex items-center gap-2 bg-white text-gray-800 px-4 py-2 rounded-full shadow-lg font-semibold hover:bg-gray-200 transition-all duration-300"
        >
          <span className="text-lg">📈</span>
          <span>Estadísticas</span>
        </a>
      </div>

      {/* 📱 Menú móvil inferior con accesos rápidos */}
      <div className="fixed z-50 bottom-4 left-1/2 -translate-x-1/2 w-[95%] flex justify-around sm:hidden">
        <a
          href="/logs"
          className="bg-white text-gray-800 px-3 py-2 rounded-full shadow-md text-sm font-semibold flex items-center gap-1"
        >
          📜
        </a>
        <a
          href="/reportes"
          className="bg-white text-gray-800 px-3 py-2 rounded-full shadow-md text-sm font-semibold flex items-center gap-1"
        >
          📅
        </a>
        <a
          href="/estadisticas"
          className="bg-white text-gray-800 px-3 py-2 rounded-full shadow-md text-sm font-semibold flex items-center gap-1"
        >
          📈
        </a>
      </div>

      {/* 📄 Footer fijo inferior */}
      <Footer />
    </div>
  );
}

export default App;
