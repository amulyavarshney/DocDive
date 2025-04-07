import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentApi } from '../api/apiClient';
import { toast } from 'sonner';

export function useDocuments(limit: number = 10, skip: number = 0) {
  return useQuery({
    queryKey: ['documents', limit, skip],
    queryFn: () => documentApi.getDocuments(limit, skip),
  });
}

export function useDocumentStats() {
  return useQuery({
    queryKey: ['documentStats'],
    queryFn: () => documentApi.getDocumentStats(),
  });
}

export function useDocumentTypeDistribution() {
  return useQuery({
    queryKey: ['documentTypes'],
    queryFn: () => documentApi.getDocumentTypeDistribution(),
  });
}

export function useDocumentDetails(documentId: string | null) {
  return useQuery({
    queryKey: ['document', documentId],
    queryFn: () => documentId ? documentApi.getDocumentDetails(documentId) : null,
    enabled: !!documentId,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: documentApi.uploadDocument,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      toast.success(`Document ${data.file_name} uploaded successfully`);
    },
    onError: (error: Error) => {
      const errorMessage = error.message || 'An unknown error occurred';
      console.error('Upload error:', errorMessage);
      
      if (errorMessage.includes('size exceeds')) {
        toast.error(`File size error: ${errorMessage}`);
      } else if (errorMessage.includes('Unsupported file type')) {
        toast.error(`File type error: ${errorMessage}`);
      } else {
        toast.error(`Upload failed: ${errorMessage}`);
      }
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: documentApi.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      toast.success('Document deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(`Delete failed: ${error.message}`);
    },
  });
}
