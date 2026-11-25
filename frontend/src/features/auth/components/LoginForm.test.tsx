import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router";

import { LoginPage } from "../pages/LoginPage";
import { LoginForm } from "./LoginForm";

describe("LoginForm", () => {
  it("requires both fields and does not submit when they are empty", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<LoginForm onSubmit={onSubmit} />);

    await userEvent.click(screen.getByRole("button", { name: /Đăng nhập/ }));

    expect(await screen.findByText(/Chưa nhập email hoặc số điện thoại/)).toBeInTheDocument();
    expect(screen.getByText(/Chưa nhập mật khẩu/)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits the trimmed identifier and the password", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<LoginForm onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText("Email hoặc số điện thoại"), "  user@example.com ");
    await userEvent.type(screen.getByLabelText("Mật khẩu"), "secret");
    await userEvent.click(screen.getByRole("button", { name: /Đăng nhập/ }));

    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith({ identifier: "user@example.com", password: "secret" }),
    );
  });

  it("shows a translated message when login fails", async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error("LOGIN_UNAVAILABLE"));
    render(<LoginForm onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText("Email hoặc số điện thoại"), "user@example.com");
    await userEvent.type(screen.getByLabelText("Mật khẩu"), "secret");
    await userEvent.click(screen.getByRole("button", { name: /Đăng nhập/ }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/hệ thống đang được xây dựng/);
  });

  it("toggles password visibility", async () => {
    render(<LoginForm onSubmit={vi.fn()} />);
    const password = screen.getByLabelText("Mật khẩu");
    expect(password).toHaveAttribute("type", "password");

    await userEvent.click(screen.getByRole("button", { name: "Hiện mật khẩu" }));
    expect(password).toHaveAttribute("type", "text");
  });
});

describe("LoginPage", () => {
  it("has one h1 and no Google / sign-up options (out of scope)", () => {
    const router = createMemoryRouter([{ path: "/login", element: <LoginPage /> }], {
      initialEntries: ["/login"],
    });
    render(<RouterProvider router={router} />);

    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.queryByText(/Google/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Đăng ký/)).not.toBeInTheDocument();
  });
});
