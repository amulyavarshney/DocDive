import React, { useState, useContext } from 'react';
import { Send, File, Info, User, Copy, Clock, Settings, X, CheckCircle } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Slider } from "@/components/ui/slider";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import EmptyState from './EmptyState';
import { useDocuments } from '@/hooks/useDocuments';
import { useSubmitQuery } from '@/hooks/useQueries';
import { DocumentResponse, QueryResponse, QuerySource } from '@/types/api';
import { SelectedDocsContext } from '@/contexts/SelectedDocsContext';

const QAInterface: React.FC = () => {
  const { selectedDocIds, setSelectedDocIds } = useContext(SelectedDocsContext);
  const [question, setQuestion] = useState<string>('');
  const [messages, setMessages] = useState<QueryResponse[]>([]);
  const [topK, setTopK] = useState<number>(3);
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(0.7);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  
  const { data: documentList } = useDocuments(100, 0);
  const { mutateAsync: submitQuery } = useSubmitQuery();
  
  const handleSendQuestion = async () => {
    if (question.trim() === '') return;
    
    // Record start time for latency calculation
    const startTime = Date.now();
    
    setIsSubmitting(true);
    
    try {
      const documentIds = selectedDocIds.length > 0 ? selectedDocIds : [];
      
      const response = await submitQuery({
        query_text: question,
        document_ids: documentIds,
        top_k: topK,
        similarity_threshold: similarityThreshold
      });
      
      // Calculate latency (for display if API doesn't provide it)
      const latency = response.latency || (Date.now() - startTime) / 1000;
      
      // Add to messages
      setMessages(prev => [...prev, {...response, latency}]);
      
      // Clear question input
      setQuestion('');
    } catch (error) {
      console.error('Error sending question:', error);
      toast.error('Failed to process your question');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };
  
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 flex flex-col h-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-2">
        <h2 className="text-lg font-medium">Document Q&A</h2>
        
        <div className="flex items-center gap-2">
          {/* Advanced settings */}
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" size="sm" className="flex items-center gap-1">
                <Settings className="h-3.5 w-3.5" />
                <span>Settings</span>
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="space-y-4">
                <h4 className="font-medium">Search Parameters</h4>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <label className="text-sm font-medium">Top K Results</label>
                    <span className="text-sm text-docflow-secondary">{topK}</span>
                  </div>
                  <Slider 
                    min={1} 
                    max={10} 
                    step={1} 
                    value={[topK]} 
                    onValueChange={(value) => setTopK(value[0])} 
                  />
                  <p className="text-xs text-docflow-secondary">Number of top matching results to consider</p>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <label className="text-sm font-medium">Similarity Threshold</label>
                    <span className="text-sm text-docflow-secondary">{similarityThreshold.toFixed(1)}</span>
                  </div>
                  <Slider 
                    min={0.1} 
                    max={1.0}
                    step={0.1}
                    value={[similarityThreshold]} 
                    onValueChange={(value) => setSimilarityThreshold(value[0])} 
                  />
                  <p className="text-xs text-docflow-secondary">Minimum similarity score (0.1 - 1.0)</p>
                </div>
              </div>
            </PopoverContent>
          </Popover>
          
          {/* Document selector */}
          <Select
            value="document-selector"
            onValueChange={(value) => {
              if (value !== 'document-selector') {
                // Add or remove from selected docs
                if (selectedDocIds.includes(value)) {
                  setSelectedDocIds(selectedDocIds.filter(id => id !== value));
                } else {
                  setSelectedDocIds([...selectedDocIds, value]);
                }
              }
            }}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select documents" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="document-selector">Select documents</SelectItem>
              {documentList?.documents
                .filter(doc => doc.embedding_status === 'processed')
                .map(doc => (
                  <SelectItem key={doc.document_id} value={doc.document_id}>
                    <div className="flex items-center gap-2">
                      <File className="h-4 w-4" />
                      <span className="truncate max-w-[150px]">{doc.file_name}</span>
                      {selectedDocIds.includes(doc.document_id) && (
                        <CheckCircle className="h-3.5 w-3.5 ml-auto text-docflow-success" />
                      )}
                    </div>
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
        </div>
      </div>
      
      {/* Selected documents display */}
      {selectedDocIds.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {selectedDocIds.map(id => {
            const doc = documentList?.documents.find(d => d.document_id === id);
            return doc ? (
              <Badge key={id} variant="secondary" className="flex items-center gap-1 pl-2 pr-1 py-1">
                <span className="truncate max-w-[150px]">{doc.file_name}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-4 w-4 rounded-full ml-1 hover:bg-gray-200"
                  onClick={() => setSelectedDocIds(selectedDocIds.filter(docId => docId !== id))}
                >
                  <X className="h-2.5 w-2.5" />
                </Button>
              </Badge>
            ) : null;
          })}
          {selectedDocIds.length > 1 && (
            <Button
              variant="ghost"
              size="sm"
              className="text-xs text-docflow-secondary hover:text-docflow-primary"
              onClick={() => setSelectedDocIds([])}
            >
              Clear all
            </Button>
          )}
        </div>
      )}
      
      {/* Message display */}
      <ScrollArea className="flex-grow mb-4 border rounded-lg bg-gray-50">
        <div className="p-4">
          {messages.length > 0 ? (
            messages.map((message, index) => (
              <div key={message.query_id || index} className="mb-6 last:mb-0">
                {/* User question */}
                <div className="text-right mb-4">
                  <div className="inline-block p-3 rounded-lg max-w-[80%] bg-docflow-primary text-white rounded-tr-none">
                    <div className="flex items-center mb-1">
                      <User className="h-4 w-4 mr-1" />
                      <span className="text-xs font-medium">You</span>
                    </div>
                    <p className="text-sm">{message.query_text}</p>
                  </div>
                </div>
                
                {/* AI answer */}
                <div className="text-left mb-2">
                  <div className="inline-block p-3 rounded-lg max-w-[80%] bg-gray-100 text-docflow-dark rounded-tl-none">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center">
                        <Info className="h-4 w-4 mr-1" />
                        <span className="text-xs font-medium">AI Assistant</span>
                      </div>
                      <div className="flex items-center text-xs text-docflow-secondary">
                        <Clock className="h-3.5 w-3.5 mr-1" />
                        <span>{typeof message.latency === 'number' ? message.latency.toFixed(2) : '0.00'}s</span>
                      </div>
                    </div>
                    <p className="text-sm whitespace-pre-line">{message.answer}</p>
                    
                    <div className="flex justify-end mt-2">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6"
                              onClick={() => copyToClipboard(message.answer)}
                            >
                              <Copy className="h-3.5 w-3.5" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Copy to clipboard</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                  </div>
                </div>
                
                {/* Sources */}
                {message.sources && Array.isArray(message.sources) && message.sources.length > 0 && (
                  <div className="ml-4 mt-2 space-y-2">
                    <p className="text-xs font-medium text-docflow-secondary">Sources:</p>
                    {message.sources.map((source: QuerySource, idx: number) => (
                      source ? <SourceItem key={idx} source={source} /> : null
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="h-full flex items-center justify-center p-6">
              <EmptyState
                icon={<Info className="h-8 w-8 text-docflow-secondary" />}
                title="Ask your documents anything"
                description={selectedDocIds.length > 0 
                  ? "Ask a question about the selected documents to get started."
                  : "Select documents and ask questions to explore your content."}
              />
            </div>
          )}
        </div>
      </ScrollArea>
      
      {/* Input area */}
      <div className="relative">
        <Textarea
          placeholder="Ask a question about your documents..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="pr-12 resize-none"
          rows={3}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendQuestion();
            }
          }}
        />
        <Button 
          size="icon" 
          className="absolute right-2 bottom-2 rounded-full bg-docflow-accent hover:bg-docflow-primary"
          onClick={handleSendQuestion}
          disabled={!question.trim() || isSubmitting}
        >
          {isSubmitting ? (
            <span className="animate-spin">
              <Clock className="h-4 w-4" />
            </span>
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>
      <p className="text-xs text-docflow-secondary mt-2">
        Press Enter to send, Shift+Enter for a new line
      </p>
    </div>
  );
};

// Component to display a source item with context highlighting
const SourceItem: React.FC<{ source: QuerySource }> = ({ source }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 text-left">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center">
          <File className="h-3.5 w-3.5 mr-1 text-docflow-secondary" />
          <p className="text-xs text-docflow-secondary truncate max-w-[200px]">
            {source.file_name || 'Unnamed source'}
          </p>
        </div>
        <Badge variant="outline" className="text-xs py-0 h-5">
          Page: {(source.page !== undefined && source.page !== null) ? source.page+1 : 'N/A'}
        </Badge>
      </div>
      <p className="text-sm text-docflow-dark mt-1">
        {source.content ? highlightMatchedText(source.content, source.keywords) : 'No content available'}
      </p>
    </div>
  );
};

// Helper function to highlight matched text (simplified implementation)
const highlightMatchedText = (text: string, keywords: string) => {
  if (!text) return <div>No content available</div>;
  
  const keywordArray = [] // keywords.split(' ');
  let highlightedText = text;
  
  keywordArray.forEach(keyword => {
    const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
    highlightedText = highlightedText.replace(regex, `<span class="bg-yellow-100 px-0.5 rounded">$&</span>`);
  });
  
  return <div dangerouslySetInnerHTML={{ __html: highlightedText }} />;
};

export default QAInterface;
