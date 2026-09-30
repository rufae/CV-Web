import { MessageCircle, X } from 'lucide-react';

import { Button } from '@/shared/ui/button';

interface ChatLauncherProps {
  open: boolean;
  onToggle: () => void;
}

export function ChatLauncher({ open, onToggle }: ChatLauncherProps) {
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Button
        onClick={onToggle}
        aria-label={open ? 'Cerrar el asistente' : 'Abrir el asistente'}
        aria-expanded={open}
        className="h-14 w-14 rounded-full bg-accent text-accent-foreground shadow-lg transition-all duration-300 hover:bg-accent/90 hover:shadow-xl glow-pulse"
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </Button>
    </div>
  );
}
