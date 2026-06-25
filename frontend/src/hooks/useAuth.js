import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

// Step 9: A clean hook so components just call `const { user } = useAuth();`
export const useAuth = () => {
  return useContext(AuthContext);
};