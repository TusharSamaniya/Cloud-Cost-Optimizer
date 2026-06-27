import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './context/ThemeContext';
import { useAuth } from './hooks/useAuth';
import DashboardLayout from './layouts/DashboardLayout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

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
            {/* The index route renders at the exactly '/' path inside the Outlet */}
            <Route index element={<div>Main Dashboard Content (Coming Soon)</div>} />
            <Route path="resources" element={<div>Resources Page</div>} />
            <Route path="recommendations" element={<div>Recommendations Page</div>} />
            <Route path="anomalies" element={<div>Anomalies Page</div>} />
            <Route path="forecast" element={<div>Forecast Page</div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;