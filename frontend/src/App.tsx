import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import FactoryPage from './pages/FactoryPage';
import DashboardPage from './pages/DashboardPage';

export default function App() {
  return (
    <div className="factory-bg min-h-screen flex">
      {/* Sidebar lateral fixa */}
      <Sidebar />

      {/* Conteúdo principal */}
      <main className="flex-1 ml-64 p-6 overflow-x-hidden">
        <Routes>
          <Route path="/" element={<FactoryPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </main>
    </div>
  );
}
