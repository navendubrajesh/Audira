import { Navigate, Route, Routes, useParams } from "react-router-dom";

import { CategoryWorkspace } from "@studio/components/shell/category-workspace";
import {
  DEFAULT_CATEGORY,
  LEGACY_TAB_REDIRECTS,
  resolveCategorySlug,
} from "@studio/config/categories";
import { getDefaultContextId } from "@studio/config/modules";
import type { ModuleId } from "@studio/types";

function LegacyTabRedirect({ module }: { module: ModuleId }) {
  const { contextId, tab } = useParams();
  const category = resolveCategorySlug(tab);
  return <Navigate to={`/${module}/${contextId}/${category}`} replace />;
}

function LegacyEngagementRedirect({ module }: { module: ModuleId }) {
  const defaultId = getDefaultContextId(module);
  return <Navigate to={`/${module}/${defaultId}/engagement-community`} replace />;
}

export function VerticalModuleRoutes({ module }: { module: ModuleId }) {
  const defaultId = getDefaultContextId(module);

  return (
    <Routes>
      <Route index element={<Navigate to={`${defaultId}/${DEFAULT_CATEGORY}`} replace />} />
      <Route path=":contextId" element={<Navigate to={DEFAULT_CATEGORY} replace />} />

      {Object.keys(LEGACY_TAB_REDIRECTS).map((legacy) => (
        <Route
          key={legacy}
          path={`:contextId/${legacy}`}
          element={<LegacyTabRedirect module={module} />}
        />
      ))}

      <Route path="engagement/*" element={<LegacyEngagementRedirect module={module} />} />

      <Route path=":contextId/:tab" element={<CategoryWorkspace module={module} />} />
    </Routes>
  );
}
