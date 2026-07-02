import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { useAuthStore } from "@studio/store/auth-store";

export function AuthCallbackPage() {
  const navigate = useNavigate();
  const signInWithToken = useAuthStore((s) => s.signInWithToken);

  useEffect(() => {
    const hash = window.location.hash.replace(/^#/, "");
    const params = new URLSearchParams(hash);
    const token = params.get("token");
    if (token) {
      void signInWithToken(token).then(() => navigate("/home", { replace: true }));
    } else {
      navigate("/login", { replace: true });
    }
  }, [navigate, signInWithToken]);

  return <GlobalStatePanel variant="loading" />;
}
