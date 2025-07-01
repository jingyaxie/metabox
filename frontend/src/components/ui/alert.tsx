import React from "react";

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'destructive';
}

export function Alert({ className = "", variant = 'default', children, ...props }: AlertProps) {
  const variants = {
    default: "border border-gray-200 bg-white text-gray-900",
    destructive: "border border-red-200 bg-red-50 text-red-900"
  };
  
  const combinedClasses = `rounded-lg border p-4 ${variants[variant]} ${className}`;
  
  return (
    <div className={combinedClasses} {...props}>
      {children}
    </div>
  );
}

export function AlertDescription({ className = "", children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={`text-sm ${className}`} {...props}>
      {children}
    </p>
  );
} 