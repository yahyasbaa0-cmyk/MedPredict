import React from 'react';
import { Loader2 } from 'lucide-react';

const Spinner = ({ size = 24, className = "text-primary" }) => {
  return (
    <div className="flex items-center justify-center p-4">
      <Loader2 size={size} className={`animate-spin ${className}`} />
    </div>
  );
};

export default Spinner;
