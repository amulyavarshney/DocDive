import React, { useEffect } from "react";
import { useDiagnostics, useHealthCheck } from "@/hooks/useSystem";
import { Card, CardTitle } from "@/components/ui/card";
import { Clock, CheckCircle, AlertTriangle, Server } from "lucide-react";
import { Link } from "react-router-dom";

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

const SystemStatusWidget: React.FC = () => {
  const { health, isLoading: healthLoading, error, checkHealth } = useHealthCheck();
  const { runDiagnostics, diagnostics, isLoading: diagnosticsLoading } = useDiagnostics();

  useEffect(() => {
    runDiagnostics().catch((err) => {
      console.error("Failed to fetch system diagnostics:", err);
    });
  }, []);

  const renderServiceStatus = (name: string, service: string) => {
    if (diagnosticsLoading) {
      return (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-md mr-3">
              <Clock className="h-5 w-5 text-docflow-warning" />
            </div>
            <span className="font-medium">{name}</span>
          </div>
          <Badge className="bg-yellow-100 text-yellow-800">Checking</Badge>
        </div>
      );
    }

    if (!diagnostics || !diagnostics.diagnostics) {
      return (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-md mr-3">
              <AlertTriangle className="h-5 w-5 text-docflow-warning" />
            </div>
            <span className="font-medium">{name}</span>
          </div>
          <Badge className="bg-gray-300 text-gray-800">Unknown status</Badge>
        </div>
      );
    }

    const serviceStatus = diagnostics.diagnostics[service.toLowerCase()];

    if (serviceStatus?.status === "connected") {
      return (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-md mr-3">
              <CheckCircle className="h-5 w-5 text-docflow-success" />
            </div>
            <span className="font-medium">{name}</span>
          </div>
          <Badge className="bg-green-100 text-green-800">Connected</Badge>
        </div>
      );
    } else {
      return (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-md mr-3">
              <AlertTriangle className="h-5 w-5 text-docflow-error" />
            </div>
            <span className="font-medium">{name}</span>
          </div>
          <Badge className="bg-red-100 text-red-800">
            {serviceStatus?.message || "Not connected"}
          </Badge>
        </div>
      );
    }
  };

  return (
    <Card>
      {/* System Status */}
      <div className="dashboard-card col-span-2 md:col-span-1">
        <CardTitle className="text-sm mb-4 font-medium flex items-center gap-2">
          <Server className="h-5 w-5 text-docflow-primary" />
          <h3 className="font-medium">System Status</h3>
        </CardTitle>

        <div className="space-y-4">
          {renderServiceStatus("Azure OpenAI", "azure_openai")}

          {renderServiceStatus("ChromaDB", "chroma_db")}

          {renderServiceStatus("MongoDB", "mongodb")}
        </div>
        <div className="mt-4 pt-2 border-t">
          <Link
            to="/settings"
            className="text-xs text-docflow-accent hover:text-docflow-accent/80 hover:underline flex justify-end"
          >
            System Administration →
          </Link>
        </div>
      </div>
    </Card>
  );
};

export default SystemStatusWidget;