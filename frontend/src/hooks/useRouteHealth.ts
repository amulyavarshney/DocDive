import { useState, useCallback } from 'react';
import { documentApi, queryApi, metricsApi, systemApi } from '@/api/apiClient';

export interface RouteHealth {
  category: string;
  name: string;
  endpoint: string;
  status: 'healthy' | 'degraded' | 'error' | 'unknown';
  responseTime: number;
  statusCode?: number;
  error?: string;
  lastChecked: Date;
}

export interface RouteHealthSummary {
  allRoutes: RouteHealth[];
  healthyCount: number;
  degradedCount: number;
  errorCount: number;
  unknownCount: number;
  overallStatus: 'healthy' | 'degraded' | 'error';
  lastChecked: Date;
}

export const useRouteHealth = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [healthSummary, setHealthSummary] = useState<RouteHealthSummary | null>(null);

  const checkRouteHealth = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    const routeChecks: RouteHealth[] = [];
    let healthyCount = 0;
    let degradedCount = 0;
    let errorCount = 0;
    let unknownCount = 0;
    
    const checkEndpoint = async (category: string, name: string, endpoint: string, checkFn: () => Promise<any>) => {
      const startTime = Date.now();
      let status: 'healthy' | 'degraded' | 'error' | 'unknown' = 'unknown';
      let statusCode: number | undefined = undefined;
      let errorMsg: string | undefined = undefined;
      
      try {
        const response = await checkFn();
        const responseTime = Date.now() - startTime;
        
        // Assume successful response means healthy
        status = 'healthy';
        if (responseTime > 2000) {
          // Consider slow responses (>2s) as degraded
          status = 'degraded';
        }
        
        routeChecks.push({
          category,
          name,
          endpoint,
          status,
          responseTime,
          statusCode: 200, // Assume 200 for successful responses
          lastChecked: new Date()
        });
        
        if (status === 'healthy') healthyCount++;
        else if (status === 'degraded') degradedCount++;
        
      } catch (err: any) {
        const responseTime = Date.now() - startTime;
        status = 'error';
        errorMsg = err.message;
        statusCode = err.response?.status;
        
        routeChecks.push({
          category,
          name,
          endpoint,
          status,
          responseTime,
          statusCode,
          error: errorMsg,
          lastChecked: new Date()
        });
        
        errorCount++;
      }
    };
    
    try {
      // Documents API Routes
      await checkEndpoint('documents', 'Document List', '/api/documents', 
        () => documentApi.getDocuments(10, 0));
      
      await checkEndpoint('documents', 'Document Stats', '/api/documents/stats',
        () => documentApi.getDocumentStats());
      
      await checkEndpoint('documents', 'Document Types', '/api/documents/types',
        () => documentApi.getDocumentTypeDistribution());
      
      // Query API Routes
      await checkEndpoint('queries', 'Query History', '/api/queries',
        () => queryApi.getQueryHistory(10, 0, 'desc'));
      
      // Metrics API Routes
      await checkEndpoint('metrics', 'Metrics Summary', '/api/metrics/summary',
        () => metricsApi.getMetricsSummary(7, 10));
      
      await checkEndpoint('metrics', 'Query Volume', '/api/metrics/query-volume',
        () => metricsApi.getQueryVolume(7));
      
      await checkEndpoint('metrics', 'Query Latency', '/api/metrics/latency',
        () => metricsApi.getLatencyMetrics(7));
        
      await checkEndpoint('metrics', 'Success Rate', '/api/metrics/success-rate',
        () => metricsApi.getSuccessRate(7));
      
      await checkEndpoint('metrics', 'Top Queries', '/api/metrics/top-queries',
        () => metricsApi.getTopQueries(7, 10));
      
      await checkEndpoint('metrics', 'Top Documents', '/api/metrics/top-documents',
        () => metricsApi.getTopDocuments(7, 10));
      
      // System API Routes
      await checkEndpoint('system', 'Health Check', '/',
        () => systemApi.healthCheck());
      
      await checkEndpoint('system', 'Diagnostics', '/api/diagnostics',
        () => systemApi.runDiagnostics());
      
      // Determine overall system status
      let overallStatus: 'healthy' | 'degraded' | 'error';
      if (errorCount > 0) {
        overallStatus = 'error';
      } else if (degradedCount > 0) {
        overallStatus = 'degraded';
      } else {
        overallStatus = 'healthy';
      }
      
      const summary: RouteHealthSummary = {
        allRoutes: routeChecks,
        healthyCount,
        degradedCount,
        errorCount,
        unknownCount,
        overallStatus,
        lastChecked: new Date()
      };
      
      setHealthSummary(summary);
      return summary;
      
    } catch (err: any) {
      setError('Failed to complete route health check');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  return { checkRouteHealth, isLoading, error, healthSummary };
}; 