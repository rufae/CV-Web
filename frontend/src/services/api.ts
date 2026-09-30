const API_URL = import.meta.env.VITE_API_URL ?? '';

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return (await response.json()) as T;
}

export const askRafa = async (message: string): Promise<string> => {
  try {
    const data = await postJson<{ response: string }>('/ask', { message });
    return data.response;
  } catch (error) {
    console.error('Error al consultar el backend:', error);
    return 'Ocurrió un error al conectar con Rafael. Intenta de nuevo más tarde.';
  }
};

export const sendContactForm = async (formData: {
  name: string;
  email: string;
  message: string;
}): Promise<{ status: string }> => {
  return postJson<{ status: string }>('/contact', formData);
};
