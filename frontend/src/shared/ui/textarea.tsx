import * as React from 'react';

import { cn } from './utils';

function Textarea({ className, ...props }: React.ComponentProps<'textarea'>) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        'resize-none border-border placeholder:text-muted-foreground flex field-sizing-content min-h-28 w-full rounded-md border bg-surface-subtle px-3 py-2 text-base text-foreground transition-[color,box-shadow,border-color] outline-none',
        'focus-visible:border-accent-strong focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:ring-offset-background',
        'aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive',
        'disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
      {...props}
    />
  );
}

export { Textarea };
