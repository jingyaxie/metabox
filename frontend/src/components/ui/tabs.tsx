import React, { useState } from "react";

export function Tabs({ defaultValue, children }: { defaultValue: string; children: React.ReactNode }) {
  const [active, setActive] = useState(defaultValue);
  return (
    <div>
      {React.Children.map(children, (child: any) => {
        if (child.type === TabsList) {
          return React.cloneElement(child, { active, setActive });
        }
        return null;
      })}
      {React.Children.map(children, (child: any) => {
        if (child.type === TabsContent && child.props.value === active) {
          return child;
        }
        return null;
      })}
    </div>
  );
}

export function TabsList({ children, active, setActive }: any) {
  return <div className="flex border-b mb-2">{React.Children.map(children, (child: any) => React.cloneElement(child, { active, setActive }))}</div>;
}

export function TabsTrigger({ value, children, active, setActive }: any) {
  const isActive = active === value;
  return (
    <button
      className={`px-4 py-2 -mb-px border-b-2 ${isActive ? "border-blue-600 text-blue-600" : "border-transparent text-gray-600"}`}
      onClick={() => setActive(value)}
      type="button"
    >
      {children}
    </button>
  );
}

export function TabsContent({ value, children }: { value: string; children: React.ReactNode }) {
  return <div>{children}</div>;
} 