import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { NgsWorkbenchApp } from "./App";
import "./styles/theme.css";
import "./styles/base.css";

const root = document.getElementById("root");
if (!root) throw new Error("NGS Analysis Workbench root was not found.");

createRoot(root).render(
  <StrictMode>
    <NgsWorkbenchApp />
  </StrictMode>,
);
