import React, { useState, useRef } from 'react';
import { Upload, X, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { toast } from 'sonner';
import { useUploadDocument } from '@/hooks/useDocuments';

// Define interface that stores a reference to the file rather than extending it
interface FileWithPreview {
  id: string;
  file: File;
  preview?: string;
  progress?: number;
  status?: 'pending' | 'uploading' | 'processed' | 'error';
  error?: string;
}

const DocumentUpload: React.FC = () => {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const { mutateAsync: uploadDocument } = useUploadDocument();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // 20MB max file size in bytes
  const MAX_FILE_SIZE = 20 * 1024 * 1024;
  // Supported file types
  const SUPPORTED_FORMATS = ['application/pdf', 'text/plain', 'text/csv', 'text/markdown'];
  // Supported file extensions
  const SUPPORTED_EXTENSIONS = ['pdf', 'txt', 'csv', 'md', 'markdown'];

  const validateFile = (file: File): { valid: boolean, error?: string } => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return { valid: false, error: `File ${file.name} exceeds the maximum size of 20MB` };
    }
    
    // Check file type by MIME type
    if (!SUPPORTED_FORMATS.includes(file.type)) {
      return { valid: false, error: `File ${file.name} has an unsupported format` };
    }
    
    // Also validate by extension
    const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';
    if (!SUPPORTED_EXTENSIONS.includes(fileExtension)) {
      return { valid: false, error: `File ${file.name} has an unsupported extension` };
    }
    
    return { valid: true };
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const fileList = Array.from(e.dataTransfer.files);
      console.log("Dropped files:", fileList.map(f => ({ name: f.name, size: f.size, type: f.type })));
      addFiles(fileList);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const fileList = Array.from(e.target.files);
      console.log("Selected files:", fileList.map(f => ({ name: f.name, size: f.size, type: f.type })));
      addFiles(fileList);
      e.target.value = '';
    }
  };

  const addFiles = (newFiles: File[]) => {
    const filesToAdd: FileWithPreview[] = [];
    const errors: string[] = [];

    newFiles.forEach(file => {
      const validation = validateFile(file);
      
      if (validation.valid) {
        filesToAdd.push({
          id: crypto.randomUUID(),
          file: file,  // Store the actual file object
          status: 'pending',
          progress: 0
        });
      } else if (validation.error) {
        errors.push(validation.error);
      }
    });
    
    if (errors.length > 0) {
      errors.forEach(error => toast.error(error));
    }
    
    if (filesToAdd.length > 0) {
      setFiles(prev => [...prev, ...filesToAdd]);
    }
  };

  const removeFile = (id: string) => {
    setFiles(files.filter(file => file.id !== id));
  };

  const uploadFiles = async () => {
    // Filter only pending files
    const pendingFiles = files.filter(file => file.status === 'pending');
    
    if (pendingFiles.length === 0) return;
    
    // Create a copy of files to update progress
    const updatedFiles = [...files];
    
    // Process each file one by one
    for (const fileWrapper of pendingFiles) {
      const file = fileWrapper.file;
      
      try {
        // Validate file properties again before upload
        if (!file.name || file.size === undefined || isNaN(file.size)) {
          throw new Error("Invalid file: Missing name or size");
        }
        
        // Update status to uploading
        const fileIndex = updatedFiles.findIndex(f => f.id === fileWrapper.id);
        updatedFiles[fileIndex] = { ...updatedFiles[fileIndex], status: 'uploading' };
        setFiles([...updatedFiles]);
        
        // Simulated upload progress updates
        const progressInterval = setInterval(() => {
          setFiles(currentFiles => {
            const files = [...currentFiles];
            const idx = files.findIndex(f => f.id === fileWrapper.id);
            if (idx !== -1 && files[idx].progress !== undefined && files[idx].progress < 90) {
              files[idx] = { ...files[idx], progress: (files[idx].progress || 0) + 10 };
            }
            return files;
          });
        }, 300);
        
        // Upload the file
        const response = await uploadDocument(file);
        
        // Clear interval and update status
        clearInterval(progressInterval);
        setFiles(currentFiles => {
          const files = [...currentFiles];
          const idx = files.findIndex(f => f.id === fileWrapper.id);
          if (idx !== -1) {
            files[idx] = { ...files[idx], progress: 100, status: 'processed' };
          }
          return files;
        });
      } catch (error) {
        // Handle error
        const fileIndex = updatedFiles.findIndex(f => f.id === fileWrapper.id);
        updatedFiles[fileIndex] = { 
          ...updatedFiles[fileIndex], 
          status: 'error', 
          error: error instanceof Error ? error.message : 'Upload failed' 
        };
        setFiles([...updatedFiles]);
      }
    }
    
    // After 1 second, remove completed files from the list
    setTimeout(() => {
      setFiles(currentFiles => currentFiles.filter(f => f.status !== 'processed'));
    }, 1000);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processed':
        return <CheckCircle className="h-4 w-4 text-docflow-success" />;
      case 'uploading':
        return <FileText className="h-4 w-4 text-docflow-warning animate-pulse" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-docflow-error" />;
      default:
        return <FileText className="h-4 w-4 text-docflow-secondary" />;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-lg font-medium mb-4">Upload Documents</h2>
      
      <div 
        className={`border-2 border-dashed rounded-lg p-6 text-center ${
          isDragging ? 'border-docflow-accent bg-blue-50' : 'border-gray-300'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className="h-10 w-10 text-docflow-secondary mx-auto mb-2" />
        <p className="text-docflow-secondary mb-2">
          Drag and drop your documents here or browse
        </p>
        <p className="text-xs text-gray-400">Supports PDF, TXT, CSV, and Markdown (up to 20MB)</p>
        <input 
          type="file" 
          multiple 
          className="hidden" 
          onChange={handleFileChange}
          accept=".pdf,.txt,.csv,.md"
          id="fileInput"
          ref={fileInputRef}
        />
        <Button 
          variant="outline" 
          size="sm" 
          className="mt-4"
          onClick={() => fileInputRef.current?.click()}
        >
          Select Files
        </Button>
      </div>
      
      {files.length > 0 && (
        <>
          <div className="mt-6">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-medium">Document Queue ({files.length})</h3>
              {files.filter(f => f.status === 'pending').length > 0 && (
                <Button 
                  variant="default" 
                  size="sm" 
                  className="bg-docflow-accent hover:bg-docflow-primary"
                  onClick={uploadFiles}
                >
                  Start Upload
                </Button>
              )}
            </div>
            
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {files.map((fileWrapper) => (
                <div 
                  key={fileWrapper.id}
                  className="flex flex-col bg-gray-50 px-3 py-2 rounded-md"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="p-1.5 bg-docflow-light rounded-md">
                        {getStatusIcon(fileWrapper.status || 'pending')}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-docflow-dark font-medium truncate max-w-[200px]">
                          {fileWrapper.file.name || 'Unnamed file'}
                        </p>
                        <p className="text-xs text-docflow-secondary flex items-center">
                          {(!isNaN(fileWrapper.file.size) ? (fileWrapper.file.size / 1024).toFixed(1) : '0')} KB 
                          {fileWrapper.status === 'error' && (
                            <span className="text-docflow-error ml-2">{fileWrapper.error}</span>
                          )}
                        </p>
                      </div>
                    </div>
                    
                    <button 
                      onClick={() => removeFile(fileWrapper.id)}
                      className="p-1 hover:bg-gray-200 rounded"
                      disabled={fileWrapper.status === 'uploading'}
                    >
                      <X className="h-4 w-4 text-docflow-secondary" />
                    </button>
                  </div>
                  
                  {fileWrapper.status === 'uploading' && (
                    <div className="mt-2">
                      <Progress value={fileWrapper.progress} className="h-1" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DocumentUpload;
