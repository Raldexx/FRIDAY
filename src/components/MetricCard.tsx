import { Card } from '@/components/ui/Card';
import { colorForPct } from '@/lib/utils';

interface ArtistTC {
  cardBg:      string;
  cardBorder:  string;
  textPrimary: string;
  textMuted:   string;
  sparkline:   string;
  accent:      string;
}

interface MetricCardProps {
  label:      string;
  value:      string;
  sub?:       string;
  color:      string;
  history:    number[];
  onClick?:   () => void;
  children?:  React.ReactNode;
  tc?:        ArtistTC | null;
}

export function MetricCard({ label, value, sub, color, history, onClick, children, tc }: MetricCardProps) {
  const pct = parseFloat(value);
  const danger = colorForPct(pct);

  const labelColor = tc ? tc.accent : color;
  const barColor   = tc ? tc.sparkline : (danger || color);
  const bigNumColor = tc ? tc.textPrimary : (danger || undefined);
  const subColor   = tc ? tc.textMuted : undefined;

  return (
    <Card clickable={!!onClick} hover onClick={onClick} tc={tc} className="relative flex flex-col gap-1.5">
      {/* Label */}
      <div className="text-[9px] font-bold tracking-[0.12em] uppercase" style={{ color: labelColor }}>
        {label}
      </div>

      {/* Big number */}
      <div
        className="text-[38px] font-extrabold leading-none tracking-tight"
        style={{ color: bigNumColor || (tc ? tc.textPrimary : '#1a1a1a') }}
      >
        {value}
      </div>

      {sub && (
        <div className="text-[10px]" style={{ color: subColor || undefined }}>
          <span className={tc ? '' : 'text-black/30 dark:text-white/30'}>{sub}</span>
        </div>
      )}

      {onClick && (
        <div className="absolute top-3 right-3 text-[10px] font-bold" style={{ color: tc ? 'rgba(255,255,255,0.2)' : undefined }}>
          <span className={tc ? '' : 'text-black/20 dark:text-white/20'}>↗</span>
        </div>
      )}

      {/* Sparkline */}
      <div className="flex items-end gap-[2px] h-6 mt-1">
        {history.slice(-20).map((v, i) => {
          const max = Math.max(...history.slice(-20), 1);
          const h = Math.max(2, (v / max) * 24);
          const opacity = 0.3 + (v / max) * 0.7;
          return (
            <div
              key={i}
              className="flex-1 rounded-[2px_2px_0_0] transition-all duration-300"
              style={{ height: h, background: barColor, opacity }}
            />
          );
        })}
      </div>

      {children}
    </Card>
  );
}
