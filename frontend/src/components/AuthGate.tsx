"use client";

import { useEffect, useState } from "react";
import { clearAuth, getStoredAuth, loadBoard, login, persistAuth, saveBoard } from "@/lib/api";
import { initialData, type BoardData } from "@/lib/kanban";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";

export const AuthGate = () => {
  const [auth, setAuth] = useState<ReturnType<typeof getStoredAuth>>(null);
  const [board, setBoard] = useState<BoardData>(initialData);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedAuth = getStoredAuth();
    if (!storedAuth) {
      setIsLoading(false);
      return;
    }

    setAuth(storedAuth);
    loadBoard(storedAuth.token)
      .then((nextBoard) => setBoard(nextBoard))
      .catch(() => setBoard(initialData))
      .finally(() => setIsLoading(false));
  }, []);

  const handleLogin = async (username: string, password: string) => {
    const nextAuth = await login(username, password);
    const session = { token: nextAuth.token, username: nextAuth.user.username };
    persistAuth(session);
    setAuth(session);
    const nextBoard = await loadBoard(nextAuth.token);
    setBoard(nextBoard);
  };

  const handleLogout = () => {
    clearAuth();
    setAuth(null);
    setBoard(initialData);
  };

  if (isLoading) {
    return <div className="flex min-h-screen items-center justify-center">Loading...</div>;
  }

  if (!auth) {
    return <LoginForm onSubmit={handleLogin} />;
  }

  return (
    <KanbanBoard
      board={board}
      onBoardChange={setBoard}
      auth={auth}
      onLogout={handleLogout}
      onSave={async (nextBoard) => {
        setBoard(nextBoard);
        await saveBoard(auth.token, nextBoard);
      }}
    />
  );
};
