import { createRoot } from "react-dom/client";

import { RunReviewApp } from "./inline/RunReviewApp";
import "./styles/theme.css";
import "./styles/base.css";
import "./styles/inline.css";

createRoot(document.getElementById("root")!).render(<RunReviewApp />);
