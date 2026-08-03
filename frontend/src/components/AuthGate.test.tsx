import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthGate } from "@/components/AuthGate";

beforeEach(() => {
  window.localStorage.clear();
});

describe("AuthGate", () => {
  it("shows the login form when there is no saved session", () => {
    render(<AuthGate />);
    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
  });

  it("signs in and shows the board", async () => {
    render(<AuthGate />);
    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(/signed in as/i)).toBeInTheDocument();
    expect(screen.getByText("user")).toBeInTheDocument();
  });
});
