const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateForm(formData: {
  name: string;
  email: string;
  message: string;
}): string | null {
  if (formData.name.trim() === '' || formData.name.length > 100) {
    return 'Indica tu nombre (máximo 100 caracteres).';
  }
  if (!EMAIL_PATTERN.test(formData.email)) {
    return 'El email no parece válido.';
  }
  if (formData.message.trim() === '' || formData.message.length > 2000) {
    return 'Escribe un mensaje (máximo 2000 caracteres).';
  }
  return null;
}
