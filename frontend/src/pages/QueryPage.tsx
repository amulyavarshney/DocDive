import React from 'react';
import Header from '@/components/Header';
import StatusBar from '@/components/StatusBar';
import QAInterface from '@/components/QAInterface';
import DocumentList from '@/components/DocumentList';
import { SelectedDocsProvider } from '@/contexts/SelectedDocsContext';
import Footer from '@/components/Footer';

const QueryPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-docflow-background flex flex-col">
      <Header />
      
      <div className="container mx-auto px-4 py-6 flex-grow">
        {/* Status Overview */}
        <StatusBar />
        
        {/* Main Content */}
        <div className="mt-6">
          {/* <h1 className="text-2xl font-bold mb-6">Document Q&A</h1> */}
          
          <SelectedDocsProvider>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <QAInterface />
              </div>
              <div>
                <DocumentList />
              </div>
            </div>
          </SelectedDocsProvider>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default QueryPage;
