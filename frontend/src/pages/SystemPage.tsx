import React, { useState } from "react";
import Header from "@/components/Header";
import StatusBar from "@/components/StatusBar";
import Footer from "@/components/Footer";
import {
  useDiagnostics,
  useResetChromaDB,
  useResetMongoDB,
  useLocustTest,
} from "../hooks/useSystem";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Database,
  Server,
  Activity,
  PlayCircle,
  Clock,
  Settings,
} from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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

const SystemPage: React.FC = () => {
  const {
    runDiagnostics,
    isLoading: isDiagnosticsLoading,
    diagnostics,
  } = useDiagnostics();
  const { resetChromaDB, isLoading: isChromaResetLoading } = useResetChromaDB();
  const { resetMongoDB, isLoading: isMongoResetLoading } = useResetMongoDB();
  const { runLocustTest, isLoading: isLocustLoading } = useLocustTest();

  const [showChromaDialog, setShowChromaDialog] = useState(false);
  const [showMongoDialog, setShowMongoDialog] = useState(false);
  const [showLocustDialog, setShowLocustDialog] = useState(false);
  const [resetSuccess, setResetSuccess] = useState<{
    message: string;
    type: string;
  } | null>(null);
  const [testSuccess, setTestSuccess] = useState<{
    message: string;
    type: string;
  } | null>(null);
  
  // Load test configuration state
  const [loadTestConfig, setLoadTestConfig] = useState({
    target_url: import.meta.env.VITE_API_URL,
    num_users: 10,
    spawn_rate: 2,
    run_time: '1m'
  });

  const handleRunDiagnostics = async () => {
    try {
      await runDiagnostics();
    } catch (error) {
      console.error("Diagnostics failed:", error);
    }
  };

  const handleResetChromaDB = async () => {
    try {
      const result = await resetChromaDB();
      setShowChromaDialog(false);
      setResetSuccess({
        message:
          "ChromaDB reset successful. You'll need to re-embed all documents.",
        type: "chroma",
      });
    } catch (error) {
      console.error("ChromaDB reset failed:", error);
    }
  };

  const handleResetMongoDB = async () => {
    try {
      const result = await resetMongoDB();
      setShowMongoDialog(false);
      setResetSuccess({
        message:
          "MongoDB reset successful. All document and query data has been cleared.",
        type: "mongo",
      });
    } catch (error) {
      console.error("MongoDB reset failed:", error);
    }
  };

  const handleRunLocustTest = async () => {
    try {
      setShowLocustDialog(false);
      const result = await runLocustTest(loadTestConfig);

      if (result.status === "success" && result.url) {
        // Open Locust UI in a new tab
        window.open(result.url, "_blank");
      }

      setTestSuccess({
        message:
          `Locust started successfully. Testing against ${loadTestConfig.target_url}. Opening the Locust web interface in a new tab.`,
        type: "locust",
      });
    } catch (error) {
      console.error("Locust test failed:", error);
    }
  };

  // Handler for input changes
  const handleConfigChange = (field: string, value: string | number) => {
    setLoadTestConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const renderServiceStatus = (name: string, service: string) => {
    if (isDiagnosticsLoading) {
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
          {/* <Badge className="bg-gray-300 text-gray-800">Unknown status</Badge> */}
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
    <div className="min-h-screen bg-docflow-background flex flex-col">
      <Header />

      <div className="container mx-auto px-4 py-6 flex-grow">
        {/* Status Overview */}
        <StatusBar />

        {/* Main Content */}
        <div className="mt-6">
          <h1 className="text-2xl font-bold">System Administration</h1>

          <div className="container mx-auto py-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Diagnostics Card */}
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
                </div>
                <CardFooter>
                  <Button
                    onClick={handleRunDiagnostics}
                    disabled={isDiagnosticsLoading}
                    className="w-full"
                  >
                    {isDiagnosticsLoading && (
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    Run Diagnostics
                  </Button>
                </CardFooter>
              </Card>

              {/* Reset Options Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Reset Options
                  </CardTitle>
                  <CardDescription>
                    Reset database and vector store
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-medium mb-2">Reset ChromaDB</h3>
                    <p className="text-sm text-gray-500 mb-2">
                      This will create a backup of the existing ChromaDB and
                      create a new empty one. You'll need to re-embed all
                      documents after this operation.
                    </p>
                    <Dialog
                      open={showChromaDialog}
                      onOpenChange={setShowChromaDialog}
                    >
                      <DialogTrigger asChild>
                        <Button variant="outline" className="w-full">
                          Reset ChromaDB
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Reset ChromaDB</DialogTitle>
                          <DialogDescription>
                            Are you sure you want to reset ChromaDB? This will
                            require re-embedding all documents.
                          </DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                          <Button
                            variant="outline"
                            onClick={() => setShowChromaDialog(false)}
                          >
                            Cancel
                          </Button>
                          <Button
                            variant="destructive"
                            onClick={handleResetChromaDB}
                            disabled={isChromaResetLoading}
                          >
                            {isChromaResetLoading && (
                              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                            )}
                            Reset ChromaDB
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>

                  <div>
                    <h3 className="font-medium mb-2">Reset MongoDB</h3>
                    <p className="text-sm text-gray-500 mb-2">
                      This will drop all collections in MongoDB and recreate
                      them with proper indexes. All document and query data will
                      be lost.
                    </p>
                    <Dialog
                      open={showMongoDialog}
                      onOpenChange={setShowMongoDialog}
                    >
                      <DialogTrigger asChild>
                        <Button variant="outline" className="w-full">
                          Reset MongoDB
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Reset MongoDB</DialogTitle>
                          <DialogDescription>
                            Are you sure you want to reset MongoDB? This will
                            delete all stored documents and queries.
                          </DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                          <Button
                            variant="outline"
                            onClick={() => setShowMongoDialog(false)}
                          >
                            Cancel
                          </Button>
                          <Button
                            variant="destructive"
                            onClick={handleResetMongoDB}
                            disabled={isMongoResetLoading}
                          >
                            {isMongoResetLoading && (
                              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                            )}
                            Reset MongoDB
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                </CardContent>
              </Card>

              {/* Load Testing Card */}
              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Load Testing
                  </CardTitle>
                  <CardDescription>
                    Run performance and load tests on the system
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-medium mb-2">Locust Load Test</h3>
                    <p className="text-sm text-gray-500 mb-4">
                      Configure and run a load test against your deployed backend. The results will be displayed in the Locust web interface.
                    </p>
                    <Dialog
                      open={showLocustDialog}
                      onOpenChange={setShowLocustDialog}
                    >
                      <DialogTrigger asChild>
                        <Button
                          variant="outline"
                          className="w-full flex items-center justify-center"
                        >
                          <Settings className="mr-2 h-4 w-4" />
                          Configure Load Test
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Configure Load Test</DialogTitle>
                          <DialogDescription>
                            Set up your load test parameters to target your deployed backend.
                          </DialogDescription>
                        </DialogHeader>
                        <div className="grid gap-4 py-4">
                          <div className="grid gap-2">
                            <Label htmlFor="target_url">Target API URL</Label>
                            <Input
                              id="target_url"
                              placeholder="https://api.example.com"
                              value={loadTestConfig.target_url}
                              onChange={(e) => handleConfigChange('target_url', e.target.value)}
                            />
                            <p className="text-sm text-gray-500">
                              The backend API URL to test against
                            </p>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="grid gap-2">
                              <Label htmlFor="num_users">Number of Users</Label>
                              <Input
                                id="num_users"
                                type="number"
                                min="1"
                                max="100"
                                value={loadTestConfig.num_users}
                                onChange={(e) => handleConfigChange('num_users', parseInt(e.target.value))}
                              />
                            </div>
                            <div className="grid gap-2">
                              <Label htmlFor="spawn_rate">Spawn Rate</Label>
                              <Input
                                id="spawn_rate"
                                type="number"
                                min="1"
                                max="50"
                                value={loadTestConfig.spawn_rate}
                                onChange={(e) => handleConfigChange('spawn_rate', parseInt(e.target.value))}
                              />
                            </div>
                          </div>
                          <div className="grid gap-2">
                            <Label htmlFor="run_time">Run Time</Label>
                            <Select 
                              value={loadTestConfig.run_time} 
                              onValueChange={(value) => handleConfigChange('run_time', value)}
                            >
                              <SelectTrigger id="run_time">
                                <SelectValue placeholder="Select duration" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="30s">30 seconds</SelectItem>
                                <SelectItem value="1m">1 minute</SelectItem>
                                <SelectItem value="5m">5 minutes</SelectItem>
                                <SelectItem value="10m">10 minutes</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        <DialogFooter>
                          <Button
                            variant="outline"
                            onClick={() => setShowLocustDialog(false)}
                          >
                            Cancel
                          </Button>
                          <Button
                            onClick={handleRunLocustTest}
                            disabled={isLocustLoading}
                          >
                            {isLocustLoading && (
                              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                            )}
                            Start Load Test
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Success message */}
            {resetSuccess && (
              <Alert className="mt-6" variant="default">
                <CheckCircle className="h-4 w-4" />
                <AlertTitle>Success</AlertTitle>
                <AlertDescription>{resetSuccess.message}</AlertDescription>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setResetSuccess(null)}
                  className="ml-auto"
                >
                  Dismiss
                </Button>
              </Alert>
            )}

            {/* Test Success message */}
            {testSuccess && (
              <Alert className="mt-6" variant="default">
                <CheckCircle className="h-4 w-4" />
                <AlertTitle>Test Started</AlertTitle>
                <AlertDescription>{testSuccess.message}</AlertDescription>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setTestSuccess(null)}
                  className="ml-auto"
                >
                  Dismiss
                </Button>
              </Alert>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default SystemPage;
