import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200 py-4 px-6">
      <div className="container mx-auto text-center text-sm text-docflow-secondary">
        <div className="flex items-center justify-center space-x-2">
          <span className="font-semibold text-docflow-primary">DocDive</span>
          <span className="text-docflow-secondary">&copy;</span>
          <span className="text-docflow-secondary">{new Date().getFullYear()}</span>
          <span className="text-docflow-secondary">|</span>
          <span className="text-docflow-secondary">Developed by</span>
          <span className="font-medium text-docflow-accent">Amulya Varshney</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 