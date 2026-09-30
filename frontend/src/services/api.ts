import axios from 'axios';

console.log('API URL:', import.meta.env.VITE_API_URL);

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const askRafa = async (message: string) => {
  try {
    const response = await api.post('/ask', { message });
    return response.data.response;
  } catch (error) {
    console.error('Error al consultar el backend:', error);
    return 'Ocurrió un error al conectar con Rafael. Intenta de nuevo más tarde.';
  }
};

export const sendContactForm = async (formData: { name: string; email: string; message: string }) => {
  try {
    const response = await api.post('/contact', formData);
    return response.data;
  } catch (error) {
    console.error('Error enviando formulario:', error);
    throw error;
  }
};

export default api;
