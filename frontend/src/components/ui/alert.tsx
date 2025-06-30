import React from "react";

export function Alert({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-2 rounded" {...props}>{children}</div>;
}

export function AlertDescription({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className="text-yellow-800 text-sm" {...props}>{children}</div>;
} 