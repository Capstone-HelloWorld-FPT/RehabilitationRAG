import { createBrowserRouter } from "react-router";

import { LoginPage } from "@/features/auth";
import { ComingSoonPage, LandingPage } from "@/workspaces/guest";

import { PublicLayout } from "./layouts/PublicLayout";

// FRONT-END-ARCHITECTURE §4. Only the guest pages and login exist so far.
// TODO: replace the "/ask" placeholder with the features/qa page.
export const router = createBrowserRouter([
  // Login has its own two-panel layout, so it sits outside PublicLayout.
  { path: "/login", element: <LoginPage /> },
  {
    path: "/",
    element: <PublicLayout />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: "ask", element: <ComingSoonPage /> },
      { path: "*", element: <ComingSoonPage variant="notFound" /> },
    ],
  },
]);
