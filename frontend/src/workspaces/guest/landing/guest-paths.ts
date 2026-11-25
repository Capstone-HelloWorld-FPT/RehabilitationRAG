// Routes the landing page links to.
// TODO: "/ask" is a placeholder until the guest Q&A page (features/qa) exists.
// FRONT-END-ARCHITECTURE §4 puts guest Q&A on "/"; the team should confirm the final path.
export const guestPaths = {
  ask: "/ask",
  login: "/login",
} as const;
