"use client";

import { BrowserRouter } from "react-router-dom";

import { AppRoutes } from "@studio/routes";
import "@studio/index.css";

/** Mountable entry for Next.js (@audira/web) and Vite (@audira/studio). */
export function StudioApp() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
