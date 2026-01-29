import type { ReactNode } from "react";
import { Header } from "./Header";

interface LayoutProps {
  children: ReactNode;
  onReset: () => void;
}

export function Layout({ children, onReset }: LayoutProps) {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <Header onReset={onReset} />
      <main className="flex-1 overflow-hidden relative flex flex-col">
        {children}
      </main>
    </div>
  );
}
