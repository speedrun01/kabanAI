"use client";

import { useState } from "react";

type LoginFormProps = {
  onSubmit: (username: string, password: string) => Promise<void>;
};

export const LoginForm = ({ onSubmit }: LoginFormProps) => {
  const [username, setUsername] = useState("user");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await onSubmit(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--surface)] px-6 py-12">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-3xl border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)]"
      >
        <h1 className="text-2xl font-semibold text-[var(--navy-dark)]">Sign in</h1>
        <p className="mt-2 text-sm text-[var(--gray-text)]">Use user / password to open the board.</p>
        <label className="mt-6 block text-sm font-medium text-[var(--navy-dark)]" htmlFor="username">
          Username
        </label>
        <input
          id="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          className="mt-2 w-full rounded-2xl border border-[var(--stroke)] px-4 py-3"
        />
        <label className="mt-4 block text-sm font-medium text-[var(--navy-dark)]" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="mt-2 w-full rounded-2xl border border-[var(--stroke)] px-4 py-3"
        />
        {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-6 w-full rounded-2xl bg-[var(--primary-blue)] px-4 py-3 font-semibold text-white"
        >
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </div>
  );
};
