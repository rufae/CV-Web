const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export type ValidationError = 'name' | 'email' | 'message';

/** Devuelve el código de error para que el componente lo traduzca. */
export function validateForm(formData: {
  name: string;
  email: string;
  message: string;
}): ValidationError | null {
  if (formData.name.trim() === '' || formData.name.length > 100) {
    return 'name';
  }
  if (!EMAIL_PATTERN.test(formData.email)) {
    return 'email';
  }
  if (formData.message.trim() === '' || formData.message.length > 2000) {
    return 'message';
  }
  return null;
}
