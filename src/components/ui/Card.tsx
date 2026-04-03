import { cn } from '@/lib/utils';

interface ArtistTC {
  cardBg:     string;
  cardBorder: string;
  textPrimary:string;
  textMuted:  string;
}

interface CardProps {
  children:    React.ReactNode;
  className?:  string;
  clickable?:  boolean;
  hover?:      boolean;
  onClick?:    () => void;
  artistTheme?: 'madison' | 'icardi' | null;
  tc?:         ArtistTC | null;
}

export function Card({ children, className, clickable, hover, onClick, artistTheme, tc }: CardProps) {
  const inlineStyle = tc ? {
    background: tc.cardBg,
    borderColor: tc.cardBorder,
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
  } : undefined;

  return (
    <div
      onClick={onClick}
      style={inlineStyle}
      className={cn(
        'rounded-2xl border p-3.5 transition-all duration-150',
        !tc && 'bg-white dark:bg-[#1c1c1e] border-black/[0.06] dark:border-white/[0.07]',
        hover && !tc && 'hover:bg-black/[0.02] dark:hover:bg-white/[0.03]',
        hover && tc && 'hover:opacity-90',
        clickable && 'cursor-pointer',
        className,
      )}
    >
      {children}
    </div>
  );
}

interface SectionLabelProps {
  children:  React.ReactNode;
  className?: string;
  color?:    string;
}

export function SectionLabel({ children, className, color }: SectionLabelProps) {
  return (
    <div
      className={cn('text-[9px] font-bold tracking-[0.14em] mb-2', className)}
      style={{ color: color || undefined }}
    >
      {!color && <span className="text-black/30 dark:text-white/30">{children}</span>}
      {color && children}
    </div>
  );
}
