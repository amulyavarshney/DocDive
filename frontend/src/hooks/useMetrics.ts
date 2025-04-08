import { useQuery } from '@tanstack/react-query';
import { metricsApi } from '../api/apiClient';

export function useMetricsSummary(days: number = 7, limit: number = 10) {
  return useQuery({
    queryKey: ['metricsSummary', days, limit],
    queryFn: () => metricsApi.getMetricsSummary(days, limit),
  });
}

export function useQueryVolume(days: number = 7) {
  return useQuery({
    queryKey: ['queryVolume', days],
    queryFn: () => metricsApi.getQueryVolume(days),
  });
}

export function useLatencyMetrics(days: number = 7) {
  return useQuery({
    queryKey: ['latencyMetrics', days],
    queryFn: () => metricsApi.getLatencyMetrics(days),
  });
}

export function useSuccessRate(days: number = 7) {
  return useQuery({
    queryKey: ['successRate', days],
    queryFn: () => metricsApi.getSuccessRate(days),
  });
}

export function useTopQueries(days: number = 7, limit: number = 10) {
  return useQuery({
    queryKey: ['topQueries', days, limit],
    queryFn: () => metricsApi.getTopQueries(days, limit),
  });
}

export function useTopDocuments(days: number = 7, limit: number = 10) {
  return useQuery({
    queryKey: ['topDocuments', days, limit],
    queryFn: () => metricsApi.getTopDocuments(days, limit),
  });
}
