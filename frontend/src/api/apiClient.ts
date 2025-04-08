import axios from 'axios';
import { 
  DocumentList, 
  DocumentResponse, 
  QueryRequest, 
  QueryResponse, 
  QueryHistory,
  MetricsSummary,
  DailyQueryVolume,
  AverageLatency,
  SuccessRate,
  TopQueries,
  TopDocuments
} from '../types/api';

// Configure axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Document API
export const documentApi = {
  uploadDocument: async (file: File): Promise<DocumentResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await apiClient.post<DocumentResponse>('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        // Extract the detail message from the API error response
        const errorMessage = error.response.data?.detail || 'Upload failed';
        throw new Error(errorMessage);
      }
      throw error;
    }
  },
  
  getDocuments: async (limit: number = 10, skip: number = 0): Promise<DocumentList> => {
    const response = await apiClient.get<DocumentList>(`/documents?limit=${limit}&skip=${skip}`);
    return response.data;
  },
  
  getDocumentDetails: async (documentId: string): Promise<DocumentResponse> => {
    const response = await apiClient.get<DocumentResponse>(`/documents/${documentId}`);
    return response.data;
  },
  
  deleteDocument: async (documentId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/documents/${documentId}`);
    return response.data;
  },
  
  getDocumentStats: async (): Promise<{ total: number, processed: number, pending: number, error: number }> => {
    const response = await apiClient.get<{ total: number, processed: number, pending: number, error: number }>('/documents/stats');
    return response.data;
  },
  
  getDocumentTypeDistribution: async (): Promise<{ type: string, count: number }[]> => {
    const response = await apiClient.get<{ type: string, count: number }[]>('/documents/types');
    return response.data;
  }
};

// Query API
export const queryApi = {
  submitQuery: async (queryRequest: QueryRequest): Promise<QueryResponse> => {
    const response = await apiClient.post<QueryResponse>('/query', queryRequest);
    return response.data;
  },
  
  getQueryHistory: async (limit: number = 10, skip: number = 0, sort: string | null = null): Promise<QueryHistory> => {
    const response = await apiClient.get<QueryHistory>(`/queries?limit=${limit}&skip=${skip}&sort=${sort}`);
    return response.data;
  },
  
  getQueryDetails: async (queryId: string): Promise<QueryResponse> => {
    const response = await apiClient.get<QueryResponse>(`/queries/${queryId}`);
    return response.data;
  }
};

// Metrics API
export const metricsApi = {
  getMetricsSummary: async (days: number = 7, limit: number = 10): Promise<MetricsSummary> => {
    const response = await apiClient.get<MetricsSummary>(`/metrics/summary?days=${days}&limit=${limit}`);
    return response.data;
  },
  
  getQueryVolume: async (days: number = 7): Promise<DailyQueryVolume[]> => {
    const response = await apiClient.get<DailyQueryVolume[]>(`/metrics/query-volume?days=${days}`);
    return response.data;
  },
  
  getLatencyMetrics: async (days: number = 7): Promise<AverageLatency[]> => {
    const response = await apiClient.get<AverageLatency[]>(`/metrics/latency?days=${days}`);
    return response.data;
  },
  
  getSuccessRate: async (days: number = 7): Promise<SuccessRate[]> => {
    const response = await apiClient.get<SuccessRate[]>(`/metrics/success-rate?days=${days}`);
    return response.data;
  },
  
  getTopQueries: async (days: number = 7, limit: number = 10): Promise<TopQueries[]> => {
    const response = await apiClient.get<TopQueries[]>(`/metrics/top-queries?days=${days}&limit=${limit}`);
    return response.data;
  },
  
  getTopDocuments: async (days: number = 7, limit: number = 10): Promise<TopDocuments[]> => {
    const response = await apiClient.get<TopDocuments[]>(`/metrics/top-documents?days=${days}&limit=${limit}`);
    return response.data;
  }
};

// System API
export const systemApi = {
  runDiagnostics: async (): Promise<any> => {
    const response = await apiClient.get('/diagnostics');
    return response.data;
  },
  
  resetChromaDB: async (): Promise<any> => {
    const response = await apiClient.delete('/reset-chromadb');
    return response.data;
  },
  
  resetMongoDB: async (): Promise<any> => {
    const response = await apiClient.delete('/reset-mongodb');
    return response.data;
  },
  
  runLocustTest: async (): Promise<any> => {
    const response = await apiClient.post('/run-locust');
    return response.data;
  },

  healthCheck: async (): Promise<any> => {
    const response = await apiClient.get('/');
    return response.data;
  }
};

export default apiClient;
