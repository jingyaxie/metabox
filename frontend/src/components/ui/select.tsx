import React from "react";

export function Select({ children, ...props }: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className="border rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-400" {...props}>{children}</select>;
}

export function SelectTrigger({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className="border rounded px-3 py-2 cursor-pointer" {...props}>{children}</div>;
}

export function SelectValue({ children, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return <span className="text-gray-700" {...props}>{children}</span>;
}

export function SelectContent({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className="absolute z-10 mt-1 w-full bg-white border rounded shadow-lg" {...props}>{children}</div>;
}

export function SelectItem({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className="px-4 py-2 hover:bg-blue-100 cursor-pointer" {...props}>{children}</div>;
} 