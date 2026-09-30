import { MessageCircle, X } from 'lucide-react';

import { Button } from '@/shared/ui/button';
import { useI18n } from '@/shared/lib/i18n';

interface ChatLauncherProps {
  open: boolean;
  onToggle: () => void;
}

export function ChatLauncher({ open, onToggle }: ChatLauncherProps) {
  const { t } = useI18n();
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Button
        onClick={onToggle}
        aria-label={open ? t.chat.close : t.chat.open}
        aria-expanded={open}
        data-chat-launcher
        className="glow-pulse h-14 w-14 rounded-full bg-accent text-accent-foreground shadow-lg transition-all duration-300 hover:bg-accent/90 hover:shadow-xl motion-reduce:animate-none"
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </Button>
    </div>
  );
}
