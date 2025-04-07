import { useState, useEffect } from 'react';
import { systemApi } from '@/api/apiClient';

// Hook for checking API health
export const useHealthCheck = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<any>(null);

  const checkHealth = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await systemApi.healthCheck();
      setHealth(response);
      return response;
    } catch (err: any) {
      setError(err.message || 'Health check failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Automatically check health on component mount
  useEffect(() => {
    checkHealth().catch(err => {
      console.error("Health check failed:", err);
    });
  }, []);

  return { checkHealth, isLoading, error, health };
};

// Hook for running system diagnostics
export const useDiagnostics = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [diagnostics, setDiagnostics] = useState<any>(null);

  const runDiagnostics = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await systemApi.runDiagnostics();
      setDiagnostics(response);
      return response;
    } catch (err: any) {
      setError(err.message || 'Failed to run diagnostics');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { runDiagnostics, isLoading, error, diagnostics };
};

// Hook for resetting ChromaDB
export const useResetChromaDB = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const resetChromaDB = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await systemApi.resetChromaDB();
      setResult(response);
      return response;
    } catch (err: any) {
      setError(err.message || 'Failed to reset ChromaDB');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { resetChromaDB, isLoading, error, result };
};

// Hook for resetting MongoDB
export const useResetMongoDB = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const resetMongoDB = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await systemApi.resetMongoDB();
      setResult(response);
      return response;
    } catch (err: any) {
      setError(err.message || 'Failed to reset MongoDB');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { resetMongoDB, isLoading, error, result };
};

// Hook for running Locust load tests
export const useLocustTest = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const runLocustTest = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await systemApi.runLocustTest();
      setResult(response);
      return response;
    } catch (err: any) {
      setError(err.message || 'Failed to run Locust test');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { runLocustTest, isLoading, error, result };
}; 