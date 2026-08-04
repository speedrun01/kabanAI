"use client";

import { useState } from "react";
import type { BoardData } from "@/lib/kanban";

type AIChatPanelProps = {
  board: BoardData;
  token: string;
  onBoardChange?: (nextBoard: BoardData) => void;
};

export const AIChatPanel = ({ board, token, onBoardChange }: AIChatPanelProps) => {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!message.trim()) {
      return;
    }

    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";

    setIsSending(true);
    try {
      const response = await fetch(`${apiBaseUrl}/api/ai/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: message.trim(),
          history: [],
          board: {
            columns: board.columns,
            cards: board.cards,
          },
        }),
      });

      const payload = await response.json();
      setReply(payload.reply);
      if (payload.update_board && payload.board_update && onBoardChange) {
        onBoardChange({
          columns: payload.board_update.columns as BoardData["columns"],
          cards: payload.board_update.cards as BoardData["cards"],
        });
      }
    } finally {
      setIsSending(false);
      setMessage("");
    }
  };

  return (
    <aside className="rounded-3xl border border-[var(--stroke)] bg-white p-5 shadow-[var(--shadow)]">
      <h2 className="text-lg font-semibold text-[var(--navy-dark)]">AI Assistant</h2>
      <p className="mt-2 text-sm text-[var(--gray-text)]">
        Ask for a board update or get help summarizing the current work.
      </p>
      <form onSubmit={handleSubmit} className="mt-4 space-y-3">
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          rows={4}
          className="w-full rounded-2xl border border-[var(--stroke)] p-3 text-sm"
          placeholder="Ask the assistant about the board"
        />
        <button
          type="submit"
          disabled={isSending}
          className="w-full rounded-2xl border border-[var(--secondary-purple)] bg-[var(--secondary-purple)] px-4 py-3 font-semibold text-white shadow-[0_8px_24px_rgba(117,57,145,0.25)] transition hover:brightness-110"
        >
          {isSending ? "Thinking..." : "Send"}
        </button>
      </form>
      {reply ? (
        <div className="mt-4 rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] p-3 text-sm text-[var(--navy-dark)]">
          {reply}
        </div>
      ) : null}
      <p className="mt-3 text-xs text-[var(--gray-text)]">
        Current board columns: {board.columns.length}
      </p>
    </aside>
  );
};
