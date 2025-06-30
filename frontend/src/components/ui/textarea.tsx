import React from "react";

export function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className="border rounded px-3 py-2 w-full min-h-[80px] focus:outline-none focus:ring-2 focus:ring-blue-400" {...props} />;
} 