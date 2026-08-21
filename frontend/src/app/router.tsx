import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "../components/layout/AppShell";
import { HomePage } from "../pages/HomePage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { ComparisonPage } from "../pages/ComparisonPage";
import { ExperimentsPage } from "../pages/ExperimentsPage";
import { WorkspacePage } from "../pages/WorkspacePage";
import { ModelInsightsPage } from "../pages/ModelInsightsPage";
import { MathematicsPage } from "../pages/MathematicsPage";
import { AboutPage } from "../pages/AboutPage";
import { MathematicalAnalysisPage } from "../pages/MathematicalAnalysisPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    errorElement: <NotFoundPage />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "workspace", element: <WorkspacePage /> },
      { path: "workspace/images/:imageId/mathematical-analysis", element: <MathematicalAnalysisPage /> },
      { path: "compare", element: <ComparisonPage /> },
      { path: "mathematics", element: <MathematicsPage /> },
      { path: "model-insights", element: <ModelInsightsPage /> },
      { path: "experiments", element: <ExperimentsPage /> },
      { path: "experiments/:experimentId", element: <ExperimentsPage /> },
      { path: "about", element: <AboutPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
