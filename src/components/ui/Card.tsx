import { cn } from '@/lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  clickable?: boolean;
  hover?: boolean;
  onClick?: () => void;
  artistTheme?: 'madison' | 'simge' | null;
}

export function Card({ children, className, clickable, hover, onClick, artistTheme }: CardProps) {
  const base = artistTheme === 'madison'
    ? 'bg-[#2d1b4e]/80 border-purple-700/30 text-white'
    : artistTheme === 'simge'
    ? 'bg-[#1e3a5f]/80 border-blue-700/30 text-white'
    : 'bg-white dark:bg-[#1c1c1e] border-black/[0.06] dark:border-white/[0.07]';

  return (
    <div
      onClick={onClick}
      className={cn(
        'rounded-none-none border p-3.5 transition-all duration-150',
        base,
        hover && !artistTheme && 'hover:bg-black/[0.02] dark:hover:bg-white/[0.03]',
        hover && artistTheme && 'hover:opacity-90',
        clickable && 'cursor-pointer',
        className,
      )}
    >
      {children}
    </div>
  );
}

interface SectionLabelProps {
  children: React.ReactNode;
  className?: string;
}

export function SectionLabel({ children, className }: SectionLabelProps) {
  return (
    <div className={cn('text-[9px] font-bold tracking-[0.14em] text-black/30 dark:text-white/30 mb-2', className)}>
      {children}
    </div>
  );
}
