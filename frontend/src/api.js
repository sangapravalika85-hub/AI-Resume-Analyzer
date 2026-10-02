import axios from 'axios';

// Keep the default aligned with the local FastAPI server. VITE_API_URL may
// override it for deployments without changing any page component.
export default axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000' });
