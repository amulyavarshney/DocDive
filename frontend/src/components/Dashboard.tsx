import React, { useState } from 'react';
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useTopQueries, useTopDocuments } from '@/hooks/useMetrics';
import { useDocumentTypeDistribution } from '@/hooks/useDocuments';
import SystemStatusWidget from './SystemStatusWidget';
import QueryHistoryWidget from './QueryHistoryWidget';

// Badge component for the dashboard
const Badge = ({ className, children }: { className?: string; children: React.ReactNode }) => {
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${className}`}>
      {children}
    </span>
  );
};

const Dashboard: React.FC = () => {
  const [timeframe, setTimeframe] = useState<number>(7);
  const { data: topQueries, isLoading: isQueriesLoading } = useTopQueries(timeframe);
  const { data: topDocuments, isLoading: isDocumentsLoading } = useTopDocuments(timeframe);
  const { data: typeDistribution, isLoading: isTypeDistributionLoading} = useDocumentTypeDistribution();

  const documentTypeData = React.useMemo(() => {
    if (!typeDistribution || typeDistribution.length === 0) {
      return [{ name: 'No data', value: 1 }];
    }
    return typeDistribution.map(item => ({
      name: item.type.toUpperCase(),
      value: item.count
    }));
  }, [typeDistribution]);

  const COLORS = ['#0ea5e9', '#64748b', '#10b981', '#f59e0b'];

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">      
        {/* Donut Chart */}
        <div className="dashboard-card">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Document Types</h3>
            <div className="text-xs text-docflow-secondary">Total: {documentTypeData.reduce((sum, item) => sum + item.value, 0)} Documents</div>
          </div>
          <div className="h-64 flex items-center justify-center">
            {isTypeDistributionLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={documentTypeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    fill="#8884d8"
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {documentTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
        
        {/* System Status Widget */}
        <SystemStatusWidget />
        
        {/* Top Queries */}
        <div className="dashboard-card">
          <h3 className="font-medium mb-4">Top Queries</h3>
          
          {isQueriesLoading ? (
            <div className="space-y-3">
              {Array(5).fill(0).map((_, idx) => (
                <Skeleton key={idx} className="h-12 w-full" />
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {(topQueries || []).map((query, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3 truncate max-w-[70%]">
                    <div className="w-6 h-6 rounded-full bg-docflow-accent flex items-center justify-center text-white text-xs font-medium">
                      {index + 1}
                    </div>
                    <p className="font-medium truncate">{query.query_text}</p>
                  </div>
                  <Badge className="bg-gray-200 text-gray-700">{query.count} queries</Badge>
                </div>
              ))}
            </div>
          )}
          
          <div className="mt-4 text-center">
            <Button variant="outline" size="sm" onClick={() => window.location.href = '/query'}>Add a new query</Button>
          </div>
        </div>
        
        {/* Most Used Documents */}
        <div className="dashboard-card col-span-2 md:col-span-1">
          <h3 className="font-medium mb-4">Most Queried Documents</h3>
          
          {isDocumentsLoading ? (
            <div className="space-y-3">
              {Array(5).fill(0).map((_, idx) => (
                <Skeleton key={idx} className="h-12 w-full" />
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {(topDocuments || []).map((doc, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3 truncate max-w-[70%]">
                    <div className="w-6 h-6 rounded-full bg-docflow-primary flex items-center justify-center text-white text-xs font-medium">
                      {index + 1}
                    </div>
                    <div className="truncate">
                      <p className="font-medium truncate">{doc.file_name}</p>
                      <p className="text-xs text-docflow-secondary truncate">{doc.document_id}</p>
                    </div>
                  </div>
                  <Badge className="bg-gray-200 text-gray-700">{doc.count} queries</Badge>
                </div>
              ))}
            </div>
          )}
          
          <div className="mt-4 text-center">
            <Button variant="outline" size="sm" onClick={() => window.location.href = '/documents'}>View All Documents</Button>
          </div>
        </div>
      </div>
      
      {/* Query History Widget */}
      <div className="mt-6">
        <QueryHistoryWidget />
      </div>
    </>
  );
};

export default Dashboard;
