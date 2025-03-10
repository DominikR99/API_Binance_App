import axios from 'axios';

// Funkcja do pobierania tokena CSRF
const getCsrfToken = async () => {
  try {
    await axios.get('http://127.0.0.1:8000/api/csrf-token/', { withCredentials: true });
  } catch (error) {
    console.error("CSRF Token fetch failed", error);
  }
};

export default getCsrfToken;