import { render, screen } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router";

import { PublicLayout } from "@/app/layouts/PublicLayout";

import { LandingPage } from "@/workspaces/guest";

function renderLanding() {
  const router = createMemoryRouter(
    [
      {
        path: "/",
        element: <PublicLayout />,
        children: [{ index: true, element: <LandingPage /> }],
      },
    ],
    { initialEntries: ["/"] },
  );
  return render(<RouterProvider router={router} />);
}

describe("LandingPage", () => {
  it("has exactly one h1", () => {
    renderLanding();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("links the login buttons to /login", () => {
    renderLanding();
    const loginLinks = screen.getAllByRole("link", { name: /Đăng nhập/ });
    expect(loginLinks.length).toBeGreaterThan(0);
    for (const link of loginLinks) expect(link).toHaveAttribute("href", "/login");
  });

  it("shows the medical disclaimer", () => {
    renderLanding();
    expect(screen.getByText(/không thay thế chẩn đoán của bác sĩ/)).toBeInTheDocument();
  });

  it("uses the product name from vi.json, not the old Figma name", () => {
    renderLanding();
    expect(screen.queryByText(/RehabRAG/)).not.toBeInTheDocument();
    expect(screen.getAllByText(/RehabGraph-RAG/).length).toBeGreaterThan(0);
  });

  it("leaves out content that is out of scope (DESIGN.md §12.3)", () => {
    renderLanding();
    expect(screen.queryByText(/24\/7/)).not.toBeInTheDocument();
    expect(screen.queryByText(/phòng khám/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/vài giây/)).not.toBeInTheDocument();
  });
});
