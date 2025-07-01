import React, { useState, useRef, useEffect } from "react";

interface SelectProps {
  value?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
}

export function Select({ value, onValueChange, children }: SelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState(value || '');
  const selectRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (newValue: string) => {
    setSelectedValue(newValue);
    onValueChange?.(newValue);
    setIsOpen(false);
  };

  return (
    <div ref={selectRef} className="relative">
      {React.Children.map(children, (child: any) => {
        if (child.type === SelectTrigger) {
          return React.cloneElement(child, { 
            isOpen, 
            setIsOpen, 
            selectedValue 
          });
        }
        if (child.type === SelectContent && isOpen) {
          return React.cloneElement(child, { 
            onSelect: handleSelect,
            selectedValue 
          });
        }
        return null;
      })}
    </div>
  );
}

interface SelectTriggerProps {
  children: React.ReactNode;
  isOpen?: boolean;
  setIsOpen?: (open: boolean) => void;
  selectedValue?: string;
}

export function SelectTrigger({ children, isOpen, setIsOpen, selectedValue }: SelectTriggerProps) {
  return (
    <button
      type="button"
      className="flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-background placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
      onClick={() => setIsOpen?.(!isOpen)}
    >
      <span>{selectedValue || children}</span>
      <svg className="h-4 w-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  );
}

interface SelectContentProps {
  children: React.ReactNode;
  onSelect?: (value: string) => void;
  selectedValue?: string;
}

export function SelectContent({ children, onSelect, selectedValue }: SelectContentProps) {
  return (
    <div className="absolute top-full z-50 mt-1 w-full rounded-md border border-gray-200 bg-white shadow-lg">
      <div className="p-1">
        {React.Children.map(children, (child: any) => {
          if (child.type === SelectItem) {
            return React.cloneElement(child, { 
              onSelect, 
              isSelected: child.props.value === selectedValue 
            });
          }
          return child;
        })}
      </div>
    </div>
  );
}

interface SelectItemProps {
  value: string;
  children: React.ReactNode;
  onSelect?: (value: string) => void;
  isSelected?: boolean;
}

export function SelectItem({ value, children, onSelect, isSelected }: SelectItemProps) {
  return (
    <button
      type="button"
      className={`relative flex w-full cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-gray-100 focus:bg-gray-100 ${
        isSelected ? 'bg-gray-100' : ''
      }`}
      onClick={() => onSelect?.(value)}
    >
      {children}
    </button>
  );
}

export function SelectValue({ children }: { children: React.ReactNode }) {
  return <span>{children}</span>;
} 