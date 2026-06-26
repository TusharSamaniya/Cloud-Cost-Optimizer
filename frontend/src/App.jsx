import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './context/ThemeContext';
import { useAuth } from './hooks/useAuth';
import DashboardLayout from './layouts/DashboardLayout';

// Step 4: PrivateRoute logic
const PrivateRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
  
};

// Temporary placeholder components so the router works immediately
const PlaceholderLogin = () => <div className="p-8">Login Page (Coming Soon)</div>;
const PlaceholderDashboard = () => <div>Main Dashboard Content (Coming Soon)</div>;

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        {/* Step 10: Global toast notifications */}
        <Toaster position="top-right" toastOptions={{ className: 'dark:bg-gray-800 dark:text-white' }} />
        
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<PlaceholderLogin />} />
          <Route path="/register" element={<div className="p-8">Register Page</div>} />

          {/* Protected Routes wrapped in DashboardLayout */}
          <Route path="/" element={
            <PrivateRoute>
              <DashboardLayout />
            </PrivateRoute>
          }>
            {/* The index route renders at the exactly '/' path inside the Outlet */}
            <Route index element={<PlaceholderDashboard />} />
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