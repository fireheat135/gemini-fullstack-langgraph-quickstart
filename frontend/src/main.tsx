import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./global.css";
import App from "./App.tsx";

// エラーハンドリング追加
window.addEventListener('error', (e) => {
  console.error('Global error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
  console.error('Unhandled promise rejection:', e.reason);
});

const root = document.getElementById("root");
if (!root) {
  throw new Error("Root element not found");
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>
);
