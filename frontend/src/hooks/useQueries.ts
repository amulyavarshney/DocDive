import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryApi } from '../api/apiClient';
import { QueryRequest } from '../types/api';
import { toast } from 'sonner';

export function useQueryHistory(limit: number = 10, skip: number = 0, sort: string | null = null) {
  return useQuery({
    queryKey: ['queryHistory', limit, skip, sort],
    queryFn: () => queryApi.getQueryHistory(limit, skip, sort),
    refetchInterval: 60000, // Auto-refresh every minute
  });
}

export function useQueryDetails(queryId: string | null) {
  return useQuery({
    queryKey: ['query', queryId],
    queryFn: () => queryId ? queryApi.getQueryDetails(queryId) : null,
    enabled: !!queryId,
  });
}

export function useSubmitQuery() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (queryRequest: QueryRequest) => queryApi.submitQuery(queryRequest),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queryHistory'] });
    },
    onError: (error: Error) => {
      toast.error(`Query failed: ${error.message}`);
    },
  });
}
