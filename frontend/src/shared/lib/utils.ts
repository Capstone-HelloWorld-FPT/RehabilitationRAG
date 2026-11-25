import { clsx, type ClassValue } from "clsx";
import { extendTailwindMerge } from "tailwind-merge";

// Teach tailwind-merge the custom font sizes from index.css (DESIGN.md §3.2). Without this,
// `text-body` and `text-muted-foreground` look like two colors and one of them is dropped.
const twMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      "font-size": [
        {
          text: [
            "display",
            "h2",
            "h2-sm",
            "h3-lg",
            "logo",
            "h3",
            "body",
            "body-sm",
            "caption",
            "eyebrow",
            "stat",
          ],
        },
      ],
    },
  },
});

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
