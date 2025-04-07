// Document Models
export interface DocumentBase {
  document_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
}

export interface DocumentResponse extends DocumentBase {
  upload_date: string;
  embedding_status: "pending" | "processed" | "error";
  chunk_count?: number;
}

export interface DocumentList {
  documents: DocumentResponse[];
  total: number;
}

export interface DocumentStats {
  total: number;
  processed: number;
  pending: number;
  error: number;
}

export interface DocumentTypeDistribution {
  type: string;
  count: number;
}

// Query Models
export interface QueryRequest {
  query_text: string;
  top_k?: number;
  similarity_threshold?: number;
  document_ids?: string[];
}

export interface QuerySource {
  document_id: string;
  file_name: string;
  content: string;
  keywords: string;
  score: number;
  page?: number;
  position?: number;
}

export interface QueryResponse {
  query_id: string;
  query_text: string;
  document_ids: string[];
  answer: string;
  sources: QuerySource[];
  latency: number;
  timestamp: string;
}

export interface QueryLog extends QueryResponse {
  status: string;
  error_message?: string;
}

export interface QueryHistory {
  queries: QueryLog[];
  total: number;
}

// Metrics Models
export interface DailyQueryVolume {
  date: string;
  count: number;
}

export interface AverageLatency {
  date: string;
  avg_latency: number;
}

export interface SuccessRate {
  date: string;
  success_rate: number;
}

export interface TopQueries {
  query_text: string;
  count: number;
}

export interface TopDocuments {
  document_id: string;
  file_name: string;
  count: number;
}

export interface MetricsSummary {
  query_volume: DailyQueryVolume[];
  latency: AverageLatency[];
  success_rate: SuccessRate[];
  top_queries: TopQueries[];
  top_documents: TopDocuments[];
}
