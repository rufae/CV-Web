import { cva } from 'class-variance-authority';

export const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-semibold transition-[color,background-color,border-color,box-shadow,filter] duration-150 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive:
          'bg-destructive text-destructive-foreground hover:bg-destructive/90 focus-visible:ring-destructive/40',
        outline:
          'border border-border bg-surface text-foreground hover:bg-surface-subtle hover:border-accent/40',
        secondary:
          'border border-border bg-surface text-foreground hover:bg-surface-subtle hover:border-accent/40',
        ghost: 'hover:bg-surface-subtle hover:text-foreground',
        link: 'text-accent-strong underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-11 px-4 sm:h-10 has-[>svg]:px-3',
        sm: 'h-10 rounded-md gap-1.5 px-3 sm:h-9 has-[>svg]:px-2.5',
        lg: 'h-12 rounded-md px-6 sm:h-11 has-[>svg]:px-4',
        icon: 'size-11 rounded-md sm:size-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
);
