// Links to sections of the guest landing page. Plain "/#id" hrefs: on "/" the browser only
// scrolls, from any other page it loads "/" and jumps to the section.
export const landingNavLinks = [
  { href: "/", labelKey: "nav.home" },
  { href: "/#about", labelKey: "nav.about" },
  { href: "/#features", labelKey: "nav.features" },
  { href: "/#how-it-works", labelKey: "nav.howItWorks" },
  { href: "/#faq", labelKey: "nav.faq" },
] as const;
