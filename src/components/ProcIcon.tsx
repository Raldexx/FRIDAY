import { useEffect, useState } from 'react';

// exe path -> icon data URL (null = no icon available)
const cache = new Map<string, string | null>();
// Icons are extracted one at a time: every extraction starts a short-lived PowerShell on the Rust side
let queue: Promise<unknown> = Promise.resolve();

function loadIcon(exe: string): Promise<string | null> {
  const job = queue.then(async () => {
    if (cache.has(exe)) return cache.get(exe) ?? null;
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      cache.set(exe, (await invoke<string | null>('get_process_icon', { exe })) ?? null);
    } catch {
      cache.set(exe, null); // browser / demo mode or extraction failed
    }
    return cache.get(exe) ?? null;
  });
  queue = job.catch(() => null);
  return job;
}

interface ProcIconProps { exe?: string | null; name: string; }

export function ProcIcon({ exe, name }: ProcIconProps) {
  const [src, setSrc] = useState<string | null>(exe ? cache.get(exe) ?? null : null);

  useEffect(() => {
    let alive = true;
    if (!exe) { setSrc(null); return; }
    if (cache.has(exe)) { setSrc(cache.get(exe) ?? null); return; }
    loadIcon(exe).then(icon => { if (alive) setSrc(icon); });
    return () => { alive = false; };
  }, [exe]);

  if (src) return <img src={src} alt="" width={16} height={16} className="w-4 h-4 flex-shrink-0 object-contain" draggable={false} />;
  // No icon (yet): small letter tile so the rows stay aligned
  return (
    <div className="w-4 h-4 flex-shrink-0 rounded-sm bg-black/[0.06] dark:bg-white/[0.1] flex items-center justify-center text-[8px] font-bold text-black/40 dark:text-white/40">
      {name.charAt(0).toUpperCase()}
    </div>
  );
}
