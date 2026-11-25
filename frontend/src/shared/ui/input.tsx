import type { ComponentProps } from "react";

import { cn } from "@/shared/lib/utils";

// Text field (DESIGN.md §9.2): 48px high, 4px radius, 1px --input border (the app background is
// white, so the border-less Figma landing input would vanish). Placeholder uses text-muted
// (5.0:1), not Figma's #8AA09D which fails contrast (DESIGN.md §11.2). Always pair with a <label>.
export function Input({ className, type = "text", ...props }: ComponentProps<"input">) {
  return (
    <input
      type={type}
      className={cn(
        "border-input text-body-sm text-foreground placeholder:text-muted-foreground focus-visible:ring-ring aria-invalid:border-destructive h-12 w-full rounded-sm border bg-white px-4 transition-colors focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}
