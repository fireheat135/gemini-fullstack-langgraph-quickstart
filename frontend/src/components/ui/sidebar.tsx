import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const sidebarVariants = cva(
  "flex h-screen w-64 flex-col border-r bg-sidebar text-sidebar-foreground glass-effect",
  {
    variants: {
      variant: {
        default: "bg-sidebar",
        floating: "bg-sidebar/95 backdrop-blur-lg border border-sidebar-border rounded-lg m-2 h-[calc(100vh-1rem)]",
        minimal: "border-none bg-transparent",
      },
      size: {
        default: "w-64",
        sm: "w-52",
        lg: "w-72",
        xl: "w-80",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

interface SidebarProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof sidebarVariants> {}

const Sidebar = React.forwardRef<HTMLDivElement, SidebarProps>(
  ({ className, variant, size, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(sidebarVariants({ variant, size }), className)}
      {...props}
    />
  )
)
Sidebar.displayName = "Sidebar"

const SidebarHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex h-16 items-center border-b border-sidebar-border px-6", className)}
    {...props}
  />
))
SidebarHeader.displayName = "SidebarHeader"

const SidebarContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex-1 overflow-auto scrollbar-thin py-4", className)}
    {...props}
  />
))
SidebarContent.displayName = "SidebarContent"

const SidebarFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("border-t border-sidebar-border p-4", className)}
    {...props}
  />
))
SidebarFooter.displayName = "SidebarFooter"

const SidebarGroup = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("px-3 py-2", className)}
    {...props}
  />
))
SidebarGroup.displayName = "SidebarGroup"

const SidebarGroupLabel = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "mb-2 px-3 text-xs font-semibold uppercase tracking-wide text-sidebar-foreground/70",
      className
    )}
    {...props}
  />
))
SidebarGroupLabel.displayName = "SidebarGroupLabel"

const SidebarGroupContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("space-y-1", className)}
    {...props}
  />
))
SidebarGroupContent.displayName = "SidebarGroupContent"

const sidebarMenuItemVariants = cva(
  "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring",
  {
    variants: {
      variant: {
        default: "text-sidebar-foreground",
        active: "bg-sidebar-accent text-sidebar-accent-foreground shadow-sm",
        ghost: "hover:bg-sidebar-accent/50",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

interface SidebarMenuItemProps
  extends React.HTMLAttributes<HTMLElement>,
    VariantProps<typeof sidebarMenuItemVariants> {
  asChild?: boolean
}

const SidebarMenuItem = React.forwardRef<HTMLElement, SidebarMenuItemProps>(
  ({ className, variant, asChild = false, ...props }, ref) => {
    const Comp = asChild ? "div" : "button"
    return (
      <Comp
        ref={ref as any}
        className={cn(sidebarMenuItemVariants({ variant }), className)}
        {...props}
      />
    )
  }
)
SidebarMenuItem.displayName = "SidebarMenuItem"

const SidebarMenuIcon = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex h-5 w-5 items-center justify-center [&_svg]:h-4 [&_svg]:w-4", className)}
    {...props}
  />
))
SidebarMenuIcon.displayName = "SidebarMenuIcon"

const SidebarMenuBadge = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-sidebar-primary px-1.5 text-xs font-medium text-sidebar-primary-foreground",
      className
    )}
    {...props}
  />
))
SidebarMenuBadge.displayName = "SidebarMenuBadge"

export {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenuItem,
  SidebarMenuIcon,
  SidebarMenuBadge,
  sidebarVariants,
  sidebarMenuItemVariants,
}