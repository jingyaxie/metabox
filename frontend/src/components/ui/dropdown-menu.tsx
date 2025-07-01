import * as React from "react"
import { cn } from "../../utils/cn"

interface DropdownMenuProps {
  children: React.ReactNode
}

interface DropdownMenuTriggerProps {
  children: React.ReactNode
}

interface DropdownMenuContentProps {
  children: React.ReactNode
  align?: "start" | "center" | "end"
  className?: string
}

interface DropdownMenuItemProps {
  children: React.ReactNode
  onClick?: (e: React.MouseEvent) => void
  className?: string
}

interface DropdownMenuSeparatorProps {
  className?: string
}

const DropdownMenu: React.FC<DropdownMenuProps> = ({ children }) => {
  return <div className="relative">{children}</div>
}

const DropdownMenuTrigger: React.FC<DropdownMenuTriggerProps> = ({ children }) => {
  return <div className="relative">{children}</div>
}

const DropdownMenuContent: React.FC<DropdownMenuContentProps> = ({ 
  children, 
  align = "center", 
  className 
}) => {
  return (
    <div className={cn(
      "absolute z-50 mt-2 min-w-[8rem] rounded-md border bg-white p-1 shadow-lg",
      align === "start" && "left-0",
      align === "center" && "left-1/2 transform -translate-x-1/2",
      align === "end" && "right-0",
      className
    )}>
      {children}
    </div>
  )
}

const DropdownMenuItem: React.FC<DropdownMenuItemProps> = ({ 
  children, 
  onClick, 
  className 
}) => {
  return (
    <button
      onClick={onClick}
      className={cn(
        "relative flex w-full cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-gray-100 focus:bg-gray-100",
        className
      )}
    >
      {children}
    </button>
  )
}

const DropdownMenuSeparator: React.FC<DropdownMenuSeparatorProps> = ({ className }) => {
  return <div className={cn("my-1 h-px bg-gray-200", className)} />
}

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} 