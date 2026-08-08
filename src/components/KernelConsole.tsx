import React, { useState } from 'react';
import { ExecutionLog } from '../types';
import { Terminal, Trash2, Pause, Play, Filter } from 'lucide-react';

interface KernelConsoleProps {
  logs: ExecutionLog[];
  onClearLogs: () => void;
}

export const KernelConsole: React.FC<KernelConsoleProps> = ({ logs, onClearLogs }) => {
  const [filter, setFilter] = useState<'all' | 'info' | 'warn' | 'dispatch'>('all');
  const [isPaused, setIsPaused] = useState<boolean>(false);

  const filteredLogs = logs.filter((log) => {
    if (filter === 'all') return true;
    return log.level === filter;
  });

  return (
    <section className="h-32 border border-[#2A2A2D] bg-[#050507] p-2.5 rounded font-mono text-[#E4E3E0] flex flex-col shrink-0">
      {/* Console Header */}
      <div className="text-[10px] text-white/40 uppercase mb-1.5 flex justify-between items-center border-b border-[#2A2A2D]/60 pb-1">
        <div className="flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-[#00FFD0]" />
          <span className="font-bold text-white/80">DRIVER_KERNEL_LOGS</span>
          <span className="text-[9px] text-[#00FFD0]">[{filteredLogs.length} LOGS]</span>
        </div>

        {/* Console Controls */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-[#0F0F12] border border-[#2A2A2D] px-1 py-0.5 rounded text-[9px]">
            <button
              onClick={() => setFilter('all')}
              className={`px-1.5 py-0.2 rounded ${filter === 'all' ? 'text-[#00FFD0] font-bold' : 'text-white/40 hover:text-white'}`}
            >
              Tümü
            </button>
            <button
              onClick={() => setFilter('info')}
              className={`px-1.5 py-0.2 rounded ${filter === 'info' ? 'text-[#38BDF8] font-bold' : 'text-white/40 hover:text-white'}`}
            >
              Info
            </button>
            <button
              onClick={() => setFilter('dispatch')}
              className={`px-1.5 py-0.2 rounded ${filter === 'dispatch' ? 'text-[#A78BFA] font-bold' : 'text-white/40 hover:text-white'}`}
            >
              Hook/Dispatch
            </button>
            <button
              onClick={() => setFilter('warn')}
              className={`px-1.5 py-0.2 rounded ${filter === 'warn' ? 'text-[#F27D26] font-bold' : 'text-white/40 hover:text-white'}`}
            >
              Swap Warning
            </button>
          </div>

          <button
            onClick={() => setIsPaused(!isPaused)}
            className="p-1 hover:bg-white/10 rounded text-white/60 transition-colors"
            title={isPaused ? 'Log Akışını Başlat' : 'Log Akışını Duraklat'}
          >
            {isPaused ? <Play className="w-3 h-3 text-[#00FFD0]" /> : <Pause className="w-3 h-3" />}
          </button>

          <button
            onClick={onClearLogs}
            className="p-1 hover:bg-white/10 rounded text-white/60 transition-colors"
            title="Logları Temizle"
          >
            <Trash2 className="w-3 h-3 text-red-400" />
          </button>
        </div>
      </div>

      {/* Log Stream */}
      <div className="flex-1 overflow-y-auto space-y-0.5 text-[10px] leading-tight pr-1">
        {filteredLogs.length === 0 ? (
          <div className="text-white/30 italic py-2">Sürücü log akışı temiz.</div>
        ) : (
          filteredLogs.map((log) => {
            let colorClass = 'text-white/60';
            if (log.level === 'warn') colorClass = 'text-[#F27D26] font-semibold';
            if (log.level === 'dispatch') colorClass = 'text-[#A78BFA] font-semibold';
            if (log.level === 'success') colorClass = 'text-[#00FFD0] font-bold';
            if (log.level === 'info') colorClass = 'text-[#38BDF8]';

            return (
              <div key={log.id} className="flex items-start gap-2 hover:bg-white/5 py-0.5 px-1 rounded font-mono">
                <span className="text-white/30 shrink-0">[{log.timestamp}]</span>
                <span className={`${colorClass} flex-1`}>{log.message}</span>
                {log.details && <span className="text-white/40 text-[9px] shrink-0 font-mono">{log.details}</span>}
              </div>
            );
          })
        )}
      </div>
    </section>
  );
};
