import React, { createContext, useState, ReactNode } from 'react';

// Define the context type
interface SelectedDocsContextType {
  selectedDocIds: string[];
  setSelectedDocIds: React.Dispatch<React.SetStateAction<string[]>>;
}

// Create context with default values
export const SelectedDocsContext = createContext<SelectedDocsContextType>({
  selectedDocIds: [],
  setSelectedDocIds: () => {},
});

// Create provider component
interface SelectedDocsProviderProps {
  children: ReactNode;
}

export const SelectedDocsProvider: React.FC<SelectedDocsProviderProps> = ({ children }) => {
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);

  return (
    <SelectedDocsContext.Provider value={{ selectedDocIds, setSelectedDocIds }}>
      {children}
    </SelectedDocsContext.Provider>
  );
}; 