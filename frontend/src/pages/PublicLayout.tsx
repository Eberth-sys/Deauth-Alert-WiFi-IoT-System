// frontend/src/pages/PublicLayout.tsx


// -------------------- Importaciones --------------------
import { ReactNode } from "react";                // Tipo para prop `children`
import Footer from "../components/Footer";         // Footer reutilizable

// -------------------- Componente: PublicLayout --------------------
const PublicLayout = ({ children }: { children: ReactNode }) => {
  return (
    <div className="min-h-screen w-screen bg-gradient-to-br from-gray-900 via-gray-950 to-black text-white flex flex-col justify-between px-4">
      {/* Fondo con gradiente oscuro, texto blanco y diseño vertical: header, contenido y footer */}

      {/* Contenido principal centrado vertical y horizontalmente */}
      <main className="flex-1 flex items-center justify-center">
        <div className="w-full max-w-md bg-gray-900/80 backdrop-blur-md rounded-2xl shadow-lg border border-gray-700 px-6 py-8 space-y-6 animate-fadeInUp">
          
          {/* Encabezado refinado: título e instrucciones */}
          <header className="text-center mb-4 space-y-1">
          <h1 className="text-[12px] sm:text-[14px] font-medium text-cyan-300 text-center leading-tight">
            Sistema IoT – seguridad Wi-Fi 2,4 GHz
          </h1>
          </header>
          {/* Área dinámica: login, registro, recuperación, etc. */}
          {children}
        </div>
      </main>

      {/* Footer persistente en la parte inferior */}
      <Footer />
    </div>
  );
};

export default PublicLayout;

