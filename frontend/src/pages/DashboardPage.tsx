import React from 'react';
import Header from '@/components/Header';
import StatusBar from '@/components/StatusBar';
import Dashboard from '@/components/Dashboard';
import Footer from '@/components/Footer';

const DashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-docflow-background flex flex-col">
      <Header />
      
      <div className="container mx-auto px-4 py-6 flex-grow">
        {/* Status Overview */}
        <StatusBar />
        
        {/* Main Content */}
        <div className="mt-6">
          <Dashboard />
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default DashboardPage;
