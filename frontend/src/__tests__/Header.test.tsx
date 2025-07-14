import { render, screen, fireEvent } from "@testing-library/react";
import { Header } from "@/components/Header";
import "@testing-library/jest-dom";

describe("Header", () => {
  it("renders logo text and navigation links", () => {
    render(<Header />);

    expect(screen.getByText("MovieApp")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /Home/i }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole("link", { name: /Movies/i }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole("link", { name: /Reviews/i }).length).toBeGreaterThan(0);
  });

  it("toggles mobile menu when hamburger button is clicked", () => {
    render(<Header />);
    const toggleButton = screen.getByLabelText(/toggle navigation menu/i);
    const mobileNav = document.getElementById("mobile-menu")!;

    // Closed state
    expect(mobileNav).toHaveClass("max-h-0");

    // Open
    fireEvent.click(toggleButton);
    expect(mobileNav).toHaveClass("max-h-96");

    // Close again
    fireEvent.click(toggleButton);
    expect(mobileNav).toHaveClass("max-h-0");
  });
}); 