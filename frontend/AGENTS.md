# Frontend overview

This frontend is a Next.js 16 application with React 19 and TypeScript. The main experience is a demo Kanban board built with local state and drag-and-drop interactions.

## Structure

- app/page.tsx renders the top-level page and mounts the Kanban board.
- components/KanbanBoard.tsx contains the board state, column rename logic, card add/delete logic, and drag-and-drop orchestration.
- components/KanbanColumn.tsx renders one column and hosts the add-card form.
- components/KanbanCard.tsx and KanbanCardPreview.tsx render card content.
- lib/kanban.ts contains the board data model and helper functions such as createId, initialData, and moveCard.
- tests and vitest setup live under src/test and the component test files.

## Development notes

- Keep changes simple and aligned with the existing component structure.
- Preserve the current demo behavior unless a task explicitly requires backend integration.
- When adding features, prefer small, focused updates over architectural rewrites.
