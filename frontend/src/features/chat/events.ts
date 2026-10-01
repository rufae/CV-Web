/** Evento global para lanzar un prompt al asistente embebido del hero. */
export const CHAT_PROMPT_EVENT = 'cvweb:chat-prompt';

export function askAssistant(prompt: string): void {
  if (typeof window === 'undefined') {
    return;
  }
  window.dispatchEvent(new CustomEvent<string>(CHAT_PROMPT_EVENT, { detail: prompt }));
}
