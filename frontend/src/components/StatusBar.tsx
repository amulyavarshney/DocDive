import React from 'react';
import { CheckCircle, AlertCircle, Clock, FileText } from 'lucide-react';
import { useDocumentStats } from '@/hooks/useDocuments';

interface StatusBarProps {
  // These props are now optional since we'll use the API data
  totalDocuments?: number;
  processedDocuments?: number;
  pendingDocuments?: number;
  errorDocuments?: number;
}

const StatusBar: React.FC<StatusBarProps> = (props) => {
  // Fetch document stats from API
  const { data: documentStats, isLoading } = useDocumentStats();
  
  // Use the API data if available, otherwise fall back to props
  const totalDocuments = documentStats?.total ?? props.totalDocuments ?? 0;
  const processedDocuments = documentStats?.processed ?? props.processedDocuments ?? 0;
  const pendingDocuments = documentStats?.pending ?? props.pendingDocuments ?? 0;
  const errorDocuments = documentStats?.error ?? props.errorDocuments ?? 0;

  const calculatePercentage = (value: number) => {
    if (totalDocuments === 0) return 0;
    return Math.round((value / totalDocuments) * 100);
  };

  // Use skeleton UI while loading
  if (isLoading && !props.totalDocuments) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-4 grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex items-center space-x-3 py-2 px-4 rounded-lg border border-gray-100">
            <div className="p-2 bg-gray-100 rounded-lg animate-pulse h-9 w-9"></div>
            <div className="w-full">
              <div className="h-4 bg-gray-100 rounded w-2/3 mb-2 animate-pulse"></div>
              <div className="h-6 bg-gray-100 rounded w-1/3 animate-pulse"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-4 grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="flex items-center space-x-3 py-2 px-4 rounded-lg border border-gray-100">
        <div className="p-2 bg-blue-50 rounded-lg">
          <FileText className="h-5 w-5 text-docflow-primary" />
        </div>
        <div>
          <p className="text-sm text-docflow-secondary">Total Documents</p>
          <p className="text-xl font-semibold text-docflow-dark">{totalDocuments}</p>
        </div>
      </div>
      
      <div className="flex items-center space-x-3 py-2 px-4 rounded-lg border border-gray-100">
        <div className="p-2 bg-green-50 rounded-lg">
          <CheckCircle className="h-5 w-5 text-docflow-success" />
        </div>
        <div>
          <p className="text-sm text-docflow-secondary">Processed</p>
          <p className="text-xl font-semibold text-docflow-dark">
            {processedDocuments} 
            <span className="text-sm ml-1 text-docflow-secondary">
              ({calculatePercentage(processedDocuments)}%)
            </span>
          </p>
        </div>
      </div>
      
      <div className="flex items-center space-x-3 py-2 px-4 rounded-lg border border-gray-100">
        <div className="p-2 bg-yellow-50 rounded-lg">
          <Clock className="h-5 w-5 text-docflow-warning" />
        </div>
        <div>
          <p className="text-sm text-docflow-secondary">Pending</p>
          <p className="text-xl font-semibold text-docflow-dark">
            {pendingDocuments}
            <span className="text-sm ml-1 text-docflow-secondary">
              ({calculatePercentage(pendingDocuments)}%)
            </span>
          </p>
        </div>
      </div>
      
      <div className="flex items-center space-x-3 py-2 px-4 rounded-lg border border-gray-100">
        <div className="p-2 bg-red-50 rounded-lg">
          <AlertCircle className="h-5 w-5 text-docflow-error" />
        </div>
        <div>
          <p className="text-sm text-docflow-secondary">Errors</p>
          <p className="text-xl font-semibold text-docflow-dark">
            {errorDocuments}
            <span className="text-sm ml-1 text-docflow-secondary">
              ({calculatePercentage(errorDocuments)}%)
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default StatusBar;
