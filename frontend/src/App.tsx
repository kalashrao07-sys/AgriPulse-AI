import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { FarmProvider } from './hooks/useFarm';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Advisor from './pages/Advisor';
import CropHealth from './pages/CropHealth';
import Weather from './pages/Weather';
import Timeline from './pages/Timeline';
import FarmSetup from './pages/FarmSetup';

export default function App() {
  return (
    <FarmProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/setup" element={<FarmSetup />} />
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/advisor" element={<Advisor />} />
            <Route path="/crop-health" element={<CropHealth />} />
            <Route path="/weather" element={<Weather />} />
            <Route path="/timeline" element={<Timeline />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </FarmProvider>
  );
}
