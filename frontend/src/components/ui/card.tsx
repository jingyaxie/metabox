import React from "react";

export function Card({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className="bg-white rounded-lg shadow p-4" {...props}>{children}</div>;
}

export function CardHeader({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className="mb-2 font-bold text-lg" {...props}>{children}</div>;
}

export function CardTitle({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className="text-xl font-semibold" {...props}>{children}</div>;
}

export function CardContent({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className="text-gray-700" {...props}>{children}</div>;
} 