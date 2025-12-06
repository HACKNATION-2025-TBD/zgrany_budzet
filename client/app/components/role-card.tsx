import { Link } from "react-router";
import { ChevronRight } from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface RoleCardProps {
  to: string;
  icon: LucideIcon;
  title: string;
  description: string;
}

export function RoleCard({
  to,
  icon: Icon,
  title,
  description,
}: RoleCardProps) {
  return (
    <Link to={to} className="bg-primary rounded-md py-4 px-2 group">
      <div className="flex items-center justify-between gap-3">
        <div className="grid grid-cols-[auto_1fr] gap-4 items-center">
          <Icon width={40} height={40} className="text-primary-foreground" />
          <div className="grid gap-2">
            <div className="font-medium">{title}</div>
            <div className="text-sm">{description}</div>
          </div>
        </div>
        <ChevronRight className="text-primary-foreground transition-transform group-hover:translate-x-[5px]" />
      </div>
    </Link>
  );
}
