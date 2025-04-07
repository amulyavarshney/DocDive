import React, { useState } from 'react';
import Header from '@/components/Header';
import StatusBar from '@/components/StatusBar';
import DocumentUpload from '@/components/DocumentUpload';
import DocumentBrowser from '@/components/DocumentBrowser';
import QAInterface from '@/components/QAInterface';
import Dashboard from '@/components/Dashboard';
import Footer from '@/components/Footer';

const Index = () => {
  const [activeTab, setActiveTab] = useState('documents');

  return (
    <div className="min-h-screen bg-docflow-background flex flex-col">
      <Header />
      
      <div className="container mx-auto px-4 py-6 flex-grow">
        {/* Status Overview */}
        <StatusBar />
        
        {/* Main Content */}
        <div className="mt-6">
          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <div className="flex space-x-6">
              <button 
                className={activeTab === 'documents' ? 'tab-button-active' : 'tab-button-inactive'}
                onClick={() => setActiveTab('documents')}
              >
                Documents
              </button>
              <button 
                className={activeTab === 'qa' ? 'tab-button-active' : 'tab-button-inactive'}
                onClick={() => setActiveTab('qa')}
              >
                Q&A
              </button>
              <button 
                className={activeTab === 'metrics' ? 'tab-button-active' : 'tab-button-inactive'}
                onClick={() => setActiveTab('metrics')}
              >
                Analytics
              </button>
            </div>
          </div>
          
          {/* Tab Content */}
          {activeTab === 'documents' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div>
                <DocumentUpload />
              </div>
              <div className="lg:col-span-2">
                <DocumentBrowser />
              </div>
            </div>
          )}
          
          {activeTab === 'qa' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <QAInterface />
              </div>
              <div>
                <DocumentBrowser />
              </div>
            </div>
          )}
          
          {activeTab === 'metrics' && (
            <div>
              <Dashboard />
            </div>
          )}
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default Index;
