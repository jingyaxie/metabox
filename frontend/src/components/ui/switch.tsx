import React from "react";

export function Switch({ checked, onChange, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="inline-flex items-center cursor-pointer">
      <input
        type="checkbox"
        className="sr-only peer"
        checked={checked}
        onChange={onChange}
        {...props}
      />
      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-400 rounded-full peer dark:bg-gray-700 peer-checked:bg-blue-600 transition"></div>
      <span className="ml-2 text-sm text-gray-700">{props['aria-label']}</span>
    </label>
  );
} 