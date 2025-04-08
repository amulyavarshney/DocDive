import React from 'react';
import Header from '@/components/Header';
import StatusBar from '@/components/StatusBar';
import MetricsDashboard from '@/components/MetricsDashboard';
import Footer from '@/components/Footer';

const MetricsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-docflow-background flex flex-col">
      <Header />
      
      <div className="container mx-auto px-4 py-6 flex-grow">
        {/* Status Overview */}
        <StatusBar />
        
        {/* Main Content */}
        <div className="mt-6">
          {/* <h1 className="text-2xl font-bold mb-6">Metrics Dashboard</h1> */}
          
          <MetricsDashboard />
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default MetricsPage;
