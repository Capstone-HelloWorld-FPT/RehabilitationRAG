import type { ReactNode } from "react";

import { cn } from "@/shared/lib/utils";

type AccordionItemProps = {
  question: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
  className?: string;
};

// FAQ row (DESIGN.md §9.4). Built on native <details>/<summary> so it works with the
// keyboard and screen readers without adding @radix-ui/react-accordion.
// The +/− sign uses teal, not peach: peach on white fails contrast (DESIGN.md §11).
export function AccordionItem({ question, children, defaultOpen, className }: AccordionItemProps) {
  return (
    <details
      open={defaultOpen}
      className={cn("group border-border-warm-2 border-b py-4.5", className)}
    >
      <summary className="focus-visible:ring-ring flex cursor-pointer list-none items-center justify-between gap-4 rounded-sm text-base font-bold text-teal-900 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none [&::-webkit-details-marker]:hidden">
        <span>{question}</span>
        <span aria-hidden="true" className="text-[22px] leading-none font-bold">
          <span className="group-open:hidden">+</span>
          <span className="hidden group-open:inline">−</span>
        </span>
      </summary>
      <div className="text-body text-muted-foreground pt-2">{children}</div>
    </details>
  );
}
