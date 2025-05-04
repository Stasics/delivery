const API_URL = 'http://localhost:8000';

async function makeRequest(endpoint, method, body = null) {
  const url = `${API_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : null
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка запроса');
    }

    return await response.json();
  } catch (error) {
    console.error('Ошибка запроса:', error);
    throw error;
  }
}