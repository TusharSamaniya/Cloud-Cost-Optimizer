import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './context/ThemeContext';
import { useAuth } from './hooks/useAuth';
import DashboardLayout from './layouts/DashboardLayout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ResourcesPage from './pages/ResourcesPage';
import RecommendationsPage from './pages/RecommendationsPage';
import AnomaliesPage from './pages/AnomaliesPage';

// Step 4: PrivateRoute logic
const PrivateRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        {/* Step 10: Global toast notifications */}
        <Toaster position="top-right" toastOptions={{ className: 'dark:bg-gray-800 dark:text-white' }} />
        
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes wrapped in DashboardLayout */}
          <Route path="/" element={
            <PrivateRoute>
              <DashboardLayout />
            </PrivateRoute>
          }>
            {/* These are the correct, single route definitions */}
            <Route index element={<DashboardPage />} />
            <Route path="resources" element={<ResourcesPage />} />
            
            {/* Swapped the placeholders for the real components here: */}
            <Route path="recommendations" element={<RecommendationsPage />} />
            <Route path="anomalies" element={<AnomaliesPage />} />
            
            <Route path="forecast" element={<div>Forecast Page</div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;