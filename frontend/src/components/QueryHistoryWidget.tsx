import React, { useState } from 'react';
import { useQueryHistory } from '@/hooks/useQueries';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { MessagesSquare, ChevronDown, ChevronUp, Timer, Link as LinkIcon, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { formatDistanceToNow } from 'date-fns';


const QueryHistoryWidget: React.FC = () => {
  const [queryLimit, setQueryLimit] = useState(5);
  const { data: queryHistory, isLoading, refetch } = useQueryHistory(queryLimit, 0, "desc");
  const [expandedQueries, setExpandedQueries] = useState<Record<string, boolean>>({});
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  const toggleQueryExpand = (queryId: string) => {
    setExpandedQueries(prev => ({
      ...prev,
      [queryId]: !prev[queryId]
    }));
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch (error) {
      return 'Unknown time';
    }
  };

  const handleLoadMore = async () => {
    setIsLoadingMore(true);
    setQueryLimit(prev => prev + 5);
    await refetch();
    setIsLoadingMore(false);
  };

  return (
    <Card className="col-span-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <MessagesSquare className="h-4 w-4" />
          Recent Queries
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {Array(5).fill(0).map((_, idx) => (
              <Skeleton key={idx} className="h-20 w-full" />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {queryHistory?.queries.length === 0 ? (
              <div className="text-center py-6 text-gray-500">
                No queries have been made yet
              </div>
            ) : (
              queryHistory?.queries.map((query) => (
                <Collapsible 
                  key={query.query_id} 
                  open={expandedQueries[query.query_id]} 
                  onOpenChange={() => toggleQueryExpand(query.query_id)}
                  className="border rounded-lg overflow-hidden"
                >
                  <div className="bg-gray-50 p-3">
                    <CollapsibleTrigger asChild>
                      <div className="flex justify-between items-center cursor-pointer">
                        <div className="flex-1">
                          <div className="font-medium truncate mb-1">{query.query_text}</div>
                          <div className="flex items-center text-xs text-gray-500 space-x-3">
                            <span className="flex items-center">
                              <Timer className="h-3 w-3 mr-1" />
                              {formatTimestamp(query.timestamp)}
                            </span>
                            <Badge variant="outline" className="text-xs">
                              {query.status === 'completed' ? 'Success' : query.status}
                            </Badge>
                            {query.latency && (
                              <span>{(query.latency / 1000).toFixed(2)}s</span>
                            )}
                          </div>
                        </div>
                        <Button variant="ghost" size="sm" className="ml-2 p-0 h-8 w-8">
                          {expandedQueries[query.query_id] ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </CollapsibleTrigger>
                  </div>
                  
                  <CollapsibleContent>
                    <div className="p-3 border-t">
                      <div className="mb-4">
                        <h4 className="text-sm font-medium mb-2">Answer</h4>
                        <div className="text-sm bg-white p-3 rounded border">
                          {query.answer}
                        </div>
                      </div>
                      
                      {query.sources && query.sources.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium mb-2">Sources</h4>
                          <div className="space-y-2">
                            {query.sources.map((source, idx) => (
                              <div key={idx} className="flex items-start text-sm">
                                <LinkIcon className="h-3 w-3 mt-1 mr-2 text-gray-400" />
                                <div>
                                  <div className="font-medium">{source.file_name || 'Unnamed document'}</div>
                                  <div className="text-xs text-gray-500">
                                    {source.content && source.content.substring(0, 100)}
                                    {source.content && source.content.length > 100 ? '...' : ''}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              ))
            )}
          </div>
        )}
        
        <div className="mt-4 pt-2 border-t text-center">
          {queryHistory && queryHistory.total > queryLimit ? (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleLoadMore}
              disabled={isLoadingMore}
            >
              {isLoadingMore && <RefreshCw className="mr-2 h-4 w-4 animate-spin" />}
              Load More Queries
            </Button>
          ) : (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => window.location.href = '/query'}
            >
              Go to Query Page
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default QueryHistoryWidget; 