import React, { useEffect, useState } from "react";
import { useRouteHealth, RouteHealth } from "@/hooks/useRouteHealth";
import { CardTitle } from "@/components/ui/card";
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Clock,
  Activity,
  RefreshCw,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";

// Badge component for the dashboard
const Badge = ({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) => {
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${className}`}>
      {children}
    </span>
  );
};

const RouteHealthWidget: React.FC = () => {
  const { checkRouteHealth, isLoading, error, healthSummary } =
    useRouteHealth();
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    // Initial health check
    checkRouteHealth().catch((err) => {
      console.error("Failed to check route health:", err);
    });

    // Setup auto-refresh if enabled
    let intervalId: NodeJS.Timeout | null = null;
    if (autoRefresh) {
      intervalId = setInterval(() => {
        checkRouteHealth().catch((err) => {
          console.error("Auto-refresh health check failed:", err);
        });
      }, 30000); // Refresh every 30 seconds
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [checkRouteHealth, autoRefresh]);

  const toggleCategory = (category: string) => {
    if (expandedCategory === category) {
      setExpandedCategory(null);
    } else {
      setExpandedCategory(category);
    }
  };

  const getStatusIcon = (status: RouteHealth["status"]) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="h-5 w-5 text-docflow-success" />;
      case "degraded":
        return <Clock className="h-5 w-5 text-docflow-warning" />;
      case "error":
        return <XCircle className="h-5 w-5 text-docflow-error" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-docflow-warning" />;
    }
  };

  const getStatusClass = (status: RouteHealth["status"]) => {
    switch (status) {
      case "healthy":
        return "bg-green-100 text-green-800";
      case "degraded":
        return "bg-yellow-100 text-yellow-800";
      case "error":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatResponseTime = (ms: number) => {
    if (ms < 1000) {
      return `${ms}ms`;
    }
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const renderRouteItem = (route: RouteHealth) => {
    return (
      <div
        key={`${route.category}-${route.name}`}
        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2"
      >
        <div className="flex items-center">
          <div
            className={`p-2 ${
              route.status === "healthy"
                ? "bg-green-100"
                : route.status === "degraded"
                ? "bg-yellow-100"
                : "bg-red-100"
            } rounded-md mr-3`}
          >
            {getStatusIcon(route.status)}
          </div>
          <div>
            <span className="font-medium">{route.name}</span>
            <div className="text-xs text-gray-500">{route.endpoint}</div>
          </div>
        </div>
        <div className="flex items-center">
          <span className="text-xs text-gray-500 mr-3">
            {formatResponseTime(route.responseTime)}
          </span>
          <Badge className={getStatusClass(route.status)}>
            {route.status.charAt(0).toUpperCase() + route.status.slice(1)}
          </Badge>
        </div>
      </div>
    );
  };

  const getCategoryStatusSummary = (category: string) => {
    if (!healthSummary) return { healthy: 0, degraded: 0, error: 0, total: 0 };

    const routes = healthSummary.allRoutes.filter(
      (route) => route.category === category
    );
    const healthy = routes.filter((route) => route.status === "healthy").length;
    const degraded = routes.filter(
      (route) => route.status === "degraded"
    ).length;
    const error = routes.filter((route) => route.status === "error").length;

    return { healthy, degraded, error, total: routes.length };
  };

  const renderCategoryGroup = (
    category: string,
    categoryDisplayName: string
  ) => {
    if (!healthSummary) return null;

    const categoryRoutes = healthSummary.allRoutes.filter(
      (route) => route.category === category
    );
    if (categoryRoutes.length === 0) return null;

    const { healthy, degraded, error, total } =
      getCategoryStatusSummary(category);
    const isExpanded = expandedCategory === category;

    let statusColor = "text-docflow-success";
    if (error > 0) statusColor = "text-docflow-error";
    else if (degraded > 0) statusColor = "text-docflow-warning";

    return (
      <div className="mb-4">
        <div
          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100"
          onClick={() => toggleCategory(category)}
        >
          <div className="flex items-center">
            <span className="font-medium">{categoryDisplayName}</span>
          </div>
          <div className="flex items-center">
            <span className={`text-sm ${statusColor} mr-2`}>
              {healthy}/{total} healthy
            </span>
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </div>
        </div>

        {isExpanded && (
          <div className="mt-2 pl-3">
            {categoryRoutes.map((route) => renderRouteItem(route))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="dashboard-card">
      <div className="flex items-center justify-between mb-4">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Activity className="h-5 w-5 text-docflow-primary" />
          <h3 className="font-medium">API Route Health</h3>
        </CardTitle>

        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            className={`text-xs ${autoRefresh ? "bg-gray-100" : ""}`}
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? "Auto-refresh On" : "Auto-refresh Off"}
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="text-xs"
            onClick={() => checkRouteHealth()}
            disabled={isLoading}
          >
            <RefreshCw
              className={`h-3 w-3 mr-1 ${isLoading ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>
      </div>

      {isLoading && !healthSummary && (
        <div className="flex justify-center items-center p-10">
          <RefreshCw className="animate-spin h-6 w-6 text-docflow-primary" />
          <span className="ml-2">Checking API routes...</span>
        </div>
      )}

      {error && !healthSummary && (
        <div className="bg-red-50 p-4 rounded-lg text-red-800">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2" />
            <span>Failed to check API routes: {error}</span>
          </div>
        </div>
      )}

      {healthSummary && (
        <>
          <div className="flex justify-between items-center mb-4 bg-gray-50 p-3 rounded-lg">
            <div className="flex gap-3">
              <div className="flex items-center">
                <Badge className="bg-green-100 text-green-800 mr-1">
                  {healthSummary.healthyCount}
                </Badge>
                <span className="text-xs">Healthy</span>
              </div>

              <div className="flex items-center">
                <Badge className="bg-yellow-100 text-yellow-800 mr-1">
                  {healthSummary.degradedCount}
                </Badge>
                <span className="text-xs">Degraded</span>
              </div>

              <div className="flex items-center">
                <Badge className="bg-red-100 text-red-800 mr-1">
                  {healthSummary.errorCount}
                </Badge>
                <span className="text-xs">Error</span>
              </div>
            </div>

            <div className="text-xs text-gray-500">
              Last checked: {healthSummary.lastChecked.toLocaleTimeString()}
            </div>
          </div>

          <div className="space-y-3">
            {renderCategoryGroup("documents", "Document API")}
            {renderCategoryGroup("queries", "Query API")}
            {renderCategoryGroup("metrics", "Metrics API")}
            {renderCategoryGroup("system", "System API")}
          </div>
        </>
      )}
    </div>
  );
};

export default RouteHealthWidget;
