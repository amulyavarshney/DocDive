import React from 'react';
import Header from '@/components/Header';
import StatusBar from '@/components/StatusBar';
import DocumentUpload from '@/components/DocumentUpload';
import DocumentBrowser from '@/components/DocumentBrowser';
import Footer from '@/components/Footer';

const DocumentsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-docflow-background flex flex-col">
      <Header />
      
      <div className="container mx-auto px-4 py-6 flex-grow">
        {/* Status Overview */}
        <StatusBar />
        
        {/* Main Content */}
        <div className="mt-6">
          <h1 className="text-2xl font-bold mb-6">Document Management</h1>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div>
              <DocumentUpload />
            </div>
            <div className="lg:col-span-2">
              <DocumentBrowser />
            </div>
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default DocumentsPage;
