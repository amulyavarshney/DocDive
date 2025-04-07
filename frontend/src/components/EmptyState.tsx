
import React, { ReactNode } from 'react';
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  buttonText?: string;
  buttonAction?: () => void;
  isLoading?: boolean;
  secondaryButton?: {
    text: string;
    action: () => void;
  }
}

const EmptyState: React.FC<EmptyStateProps> = ({ 
  icon, 
  title, 
  description,
  buttonText,
  buttonAction,
  isLoading = false,
  secondaryButton
}) => {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="p-4 bg-gray-50 rounded-full mb-4">
          <Skeleton className="h-10 w-10 rounded-full" />
        </div>
        <Skeleton className="h-6 w-40 mb-2" />
        <Skeleton className="h-4 w-64 mb-6" />
        
        {buttonText && (
          <Skeleton className="h-9 w-24" />
        )}
      </div>
    );
  }
  
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="p-4 bg-gray-50 rounded-full mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-medium text-docflow-dark mb-2">{title}</h3>
      <p className="text-docflow-secondary text-center max-w-md mb-6">{description}</p>
      
      <div className="flex gap-3">
        {buttonText && buttonAction && (
          <Button onClick={buttonAction}>{buttonText}</Button>
        )}
        
        {secondaryButton && (
          <Button variant="outline" onClick={secondaryButton.action}>
            {secondaryButton.text}
          </Button>
        )}
      </div>
    </div>
  );
};

export default EmptyState;
