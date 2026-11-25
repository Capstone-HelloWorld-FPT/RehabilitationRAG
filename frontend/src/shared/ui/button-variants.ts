import { cva, type VariantProps } from "class-variance-authority";

// shadcn-style button classes (DESIGN.md §9.1, §13). Kept in a separate file so links
// (<Link>, <a>) can look like buttons without needing @radix-ui/react-slot.
// Hover / focus / disabled states are DESIGN.md proposals: Figma has none yet.
export const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-sm text-sm font-bold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        accent: "bg-accent text-accent-foreground hover:bg-accent/90",
        ghost: "hover:bg-white/10",
        link: "text-primary underline underline-offset-4 hover:no-underline",
      },
      size: {
        default: "h-11 px-6",
        icon: "size-11",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

export type ButtonVariantProps = VariantProps<typeof buttonVariants>;
