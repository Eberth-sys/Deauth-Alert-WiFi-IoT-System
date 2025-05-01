//frontend\src\pages\PublicLayout.tsx

// -------------------- Importaciones --------------------
import { ReactNode } from "react";              // Tipo para prop `children`
import Footer from "../components/Footer";       // Footer reutilizable

// -------------------- Componente: PublicLayout --------------------
const PublicLayout = ({ children }: { children: ReactNode }) => {
  return (
    <div className="min-h-screen w-screen bg-gray-900 text-white flex flex-col justify-between px-4">
      {/* Contenedor principal: fondo oscuro y distribución vertical */}
      
      {/* Contenido principal centrado */}
      <main className="flex-1 flex items-center justify-center">
        <div className="w-full max-w-md bg-gray-800 rounded-xl shadow-xl p-6 space-y-4 border border-gray-700">
          
          {/* Encabezado del formulario */}
          <header className="text-center">
            <h1 className="text-2xl font-extrabold text-blue-400">🔐 Sistema de autenticación</h1>
            <p className="text-sm text-gray-400">Accede al panel IoT</p>
          </header>

          {/* Área para contenido: login, registro, recuperación */}
          {children}
        </div>
      </main>

      {/* Footer fijo en la parte inferior */}
      <Footer />
    </div>
  );
};

export default PublicLayout;
