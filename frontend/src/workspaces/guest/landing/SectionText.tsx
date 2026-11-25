import type { ReactNode } from "react";

import { cn } from "@/shared/lib/utils";

type Tone = "light" | "dark";

// Eyebrow: small uppercase line above a heading (DESIGN.md §3.2).
// Peach only on dark backgrounds; on light ones it fails contrast (DESIGN.md §11.2), so teal-700.
export function Eyebrow({
  tone = "light",
  className,
  children,
}: {
  tone?: Tone;
  className?: string;
  children: ReactNode;
}) {
  return (
    <p
      className={cn(
        "text-eyebrow font-bold uppercase",
        tone === "dark" ? "text-peach-400" : "text-teal-700",
        className,
      )}
    >
      {children}
    </p>
  );
}

export function SectionTitle({
  id,
  tone = "light",
  className,
  children,
}: {
  id?: string;
  tone?: Tone;
  className?: string;
  children: ReactNode;
}) {
  return (
    <h2
      id={id}
      className={cn(
        "text-h3-lg sm:text-h2-sm lg:text-h2 font-bold",
        tone === "dark" ? "text-white" : "text-teal-900",
        className,
      )}
    >
      {children}
    </h2>
  );
}

export function Container({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div className={cn("max-w-content mx-auto w-full px-4 xl:px-0", className)}>{children}</div>
  );
}
