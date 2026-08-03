import type { BoardData } from "@/lib/kanban";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const buildUrl = (path: string) => `${API_BASE_URL}${path}`;

type AuthSession = {
  token: string;
  username: string;
};

type LoginResponse = {
  token: string;
  user: {
    username: string;
  };
};

export const getStoredAuth = (): AuthSession | null => {
  if (typeof window === "undefined") {
    return null;
  }

  const token = window.localStorage.getItem("pm-token");
  const username = window.localStorage.getItem("pm-username");

  if (!token || !username) {
    return null;
  }

  return { token, username };
};

export const persistAuth = ({ token, username }: AuthSession) => {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem("pm-token", token);
  window.localStorage.setItem("pm-username", username);
};

export const clearAuth = () => {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem("pm-token");
  window.localStorage.removeItem("pm-username");
};

export const login = async (username: string, password: string): Promise<LoginResponse> => {
  const response = await fetch(buildUrl("/api/auth/login"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error("Unable to sign in");
  }

  return response.json();
};

export const loadBoard = async (token: string): Promise<BoardData> => {
  const response = await fetch(buildUrl("/api/board"), {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Unable to load board");
  }

  return response.json();
};

export const saveBoard = async (token: string, board: BoardData): Promise<BoardData> => {
  const response = await fetch(buildUrl("/api/board"), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(board),
  });

  if (!response.ok) {
    throw new Error("Unable to save board");
  }

  return response.json();
};
