import "@testing-library/jest-dom";
import React from "react";
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const jest: any;

// Mock Next.js dynamic imports for Image and Link
jest.mock("next/image", () => ({
  __esModule: true,
  default: (props: any) => {
    // eslint-disable-next-line @next/next/no-img-element
    return React.createElement("img", { ...props, alt: props.alt || "image" });
  },
}));

jest.mock("next/link", () => {
  return ({ children, href, ...rest }: any) =>
    React.createElement("a", { href, ...rest }, children);
});

jest.mock("@/lib/supabase", () => {
  const authMock = {
    getSession: () => Promise.resolve({ data: { session: null } }),
    onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } }),
    signInWithOAuth: jest.fn(),
    signOut: jest.fn(),
  };
  return {
    supabase: {
      auth: authMock,
    },
  };
});

export {}; 