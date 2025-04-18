//frontend\src\main.tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App.tsx';
import LogsPage from './pages/LogsPage.tsx';
import ReportsPage from './pages/ReportsPage.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="/reportes" element={<ReportsPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
