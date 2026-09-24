import React, { useState, useEffect } from 'react';
import { ArcTask, ArcSimulationResult } from '../types';
import { Play, Sparkles, RefreshCw, CheckCircle2, Eye, Grid, Palette, ChevronRight, Layers } from 'lucide-react';

const ARC_COLORS: Record<number, { bg: string; name: string; hex: string }> = {
  0: { bg: 'bg-[#000000]', name: 'Siyah (Zemin)', hex: '#000000' },
  1: { bg: 'bg-[#1E88E5]', name: 'Mavi', hex: '#1E88E5' },
  2: { bg: 'bg-[#D81B60]', name: 'Kırmızı', hex: '#D81B60' },
  3: { bg: 'bg-[#43A047]', name: 'Yeşil', hex: '#43A047' },
  4: { bg: 'bg-[#FDD835]', name: 'Sarı', hex: '#FDD835' },
  5: { bg: 'bg-[#8E8E8E]', name: 'Gri', hex: '#8E8E8E' },
  6: { bg: 'bg-[#8E24AA]', name: 'Macenta', hex: '#8E24AA' },
  7: { bg: 'bg-[#FB8C00]', name: 'Turuncu', hex: '#FB8C00' },
  8: { bg: 'bg-[#00ACC1]', name: 'Açık Mavi', hex: '#00ACC1' },
  9: { bg: 'bg-[#5D4037]', name: 'Kahverengi', hex: '#5D4037' },
};

export const ArcLab: React.FC = () => {
  const [tasks, setTasks] = useState<Array<{ id: string; set: string }>>([]);
  const [selectedSet, setSelectedSet] = useState<'evaluation' | 'training'>('evaluation');
  const [selectedTaskId, setSelectedTaskId] = useState<string>('');
  const [currentTask, setCurrentTask] = useState<ArcTask | null>(null);
  const [loading, setLoading] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<ArcSimulationResult | null>(null);

  // Interactive user grid
  const [interactiveGrid, setInteractiveGrid] = useState<number[][]>([]);
  const [selectedPaintColor, setSelectedPaintColor] = useState<number>(1);

  // Fetch tasks list
  useEffect(() => {
    async function loadTasks() {
      try {
        const res = await fetch(`/api/arc/tasks?set=${selectedSet}`);
        const data = await res.json();
        if (data.success && data.tasks.length > 0) {
          setTasks(data.tasks);
          setSelectedTaskId(data.tasks[0].id);
        }
      } catch (err) {
        console.error('Failed to load ARC tasks:', err);
      }
    }
    loadTasks();
  }, [selectedSet]);

  // Fetch selected task details
  useEffect(() => {
    if (!selectedTaskId) return;
    async function loadTaskDetail() {
      setLoading(true);
      setSimulationResult(null);
      try {
        const res = await fetch(`/api/arc/task/${selectedSet}/${selectedTaskId}`);
        const data = await res.json();
        if (data.success) {
          setCurrentTask(data.data);
          const initialTest = data.data.test[0]?.input || [[0]];
          setInteractiveGrid(initialTest.map((r: number[]) => [...r]));
        }
      } catch (err) {
        console.error('Failed to load task:', err);
      } finally {
        setLoading(false);
      }
    }
    loadTaskDetail();
  }, [selectedTaskId, selectedSet]);

  // Execute reasoning simulation
  const handleSimulate = async () => {
    if (!currentTask) return;
    setSimulating(true);
    try {
      const res = await fetch('/api/arc/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: currentTask })
      });
      const data = await res.json();
      if (data.success) {
        setSimulationResult(data);
        if (data.predictedGrid) {
          setInteractiveGrid(data.predictedGrid);
        }
      }
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleCellClick = (r: number, c: number) => {
    setInteractiveGrid(prev => {
      const next = prev.map(row => [...row]);
      next[r][c] = selectedPaintColor;
      return next;
    });
  };

  const renderGrid = (grid: number[][], interactive = false) => {
    if (!grid || grid.length === 0) return <span className="text-xs text-[#a89a78]">Boş ızgara</span>;
    const numRows = grid.length;
    const numCols = grid[0].length;

    return (
      <div
        className="inline-grid p-1.5 bg-[#16130e] border border-[#362f22] rounded shadow-inner"
        style={{
          gridTemplateColumns: `repeat(${numCols}, minmax(0, 1fr))`,
          gap: '1px'
        }}
      >
        {grid.map((row, r) =>
          row.map((val, c) => {
            const color = ARC_COLORS[val] || ARC_COLORS[0];
            return (
              <div
                key={`${r}-${c}`}
                onClick={() => interactive && handleCellClick(r, c)}
                className={`w-6 h-6 sm:w-7 sm:h-7 rounded-[2px] transition-transform flex items-center justify-center text-[9px] font-mono-code select-none ${
                  interactive ? 'cursor-pointer hover:scale-110 hover:z-10' : ''
                }`}
                style={{ backgroundColor: color.hex }}
                title={`(${r}, ${c}): Renk ${val} (${color.name})`}
              >
                {val !== 0 && (
                  <span className={val === 4 ? 'text-black font-bold' : 'text-white font-semibold'}>
                    {val}
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col space-y-6 w-full">
      {/* Top Header & Task Selector */}
      <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-[#3a2418] text-[#e08856] rounded-lg">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-serif-fraunces font-bold text-[#ece3cf]">
              ARC-AGI-2 Akıl Yürütme Laboratuvarı
            </h3>
            <p className="text-xs text-[#a89a78]">
              Nefs-i Müdrike melekeler zincirinin bulmaca ızgaraları üzerinde adım adım icrası.
            </p>
          </div>
        </div>

        {/* Set Switcher & Task Dropdown */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-1 bg-[#16130e] p-1 rounded-lg border border-[#362f22]">
            <button
              onClick={() => setSelectedSet('evaluation')}
              className={`px-3 py-1.5 text-xs rounded transition-colors ${
                selectedSet === 'evaluation'
                  ? 'bg-[#3a2418] text-[#e08856] font-semibold border border-[#e08856]/40'
                  : 'text-[#a89a78] hover:text-[#ece3cf]'
              }`}
            >
              Evaluation (120 Görev)
            </button>
            <button
              onClick={() => setSelectedSet('training')}
              className={`px-3 py-1.5 text-xs rounded transition-colors ${
                selectedSet === 'training'
                  ? 'bg-[#3a2418] text-[#e08856] font-semibold border border-[#e08856]/40'
                  : 'text-[#a89a78] hover:text-[#ece3cf]'
              }`}
            >
              Training (763 Görev)
            </button>
          </div>

          <select
            value={selectedTaskId}
            onChange={(e) => setSelectedTaskId(e.target.value)}
            className="bg-[#16130e] border border-[#362f22] rounded-lg px-3 py-2 text-xs font-mono-code text-[#ece3cf] focus:outline-none focus:border-[#e08856]"
          >
            {tasks.map(t => (
              <option key={t.id} value={t.id}>Görev ID: {t.id}</option>
            ))}
          </select>

          <button
            onClick={handleSimulate}
            disabled={simulating || loading}
            className="flex items-center gap-2 bg-[#e08856] hover:bg-[#d57743] text-[#16130e] font-semibold px-4 py-2 rounded-lg text-xs shadow-md transition-all disabled:opacity-50"
          >
            {simulating ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Melekeler Koşuyor...
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                Zihnî Akışı Başlat
              </>
            )}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-[#a89a78] bg-[#1c1810] rounded-xl border border-[#362f22]">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-[#e08856]" />
          Görev verisi yükleniyor...
        </div>
      ) : currentTask ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Training Examples & Pairs */}
          <div className="lg:col-span-7 space-y-6">
            <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-4">
              <div className="flex items-center justify-between border-b border-[#362f22] pb-3">
                <span className="text-sm font-semibold text-[#ece3cf] flex items-center gap-2">
                  <Grid className="w-4 h-4 text-[#e08856]" />
                  Eğitim Örnekleri (Müşahede Çiftleri: {currentTask.train.length})
                </span>
                <span className="text-xs text-[#a89a78] font-mono-code">Girdi ➔ Çıktı</span>
              </div>

              <div className="space-y-5">
                {currentTask.train.map((pair, idx) => (
                  <div key={idx} className="bg-[#16130e] p-3 rounded-lg border border-[#362f22] space-y-2">
                    <span className="text-[11px] font-mono-code text-[#a89a78]">Örnek #{idx + 1}</span>
                    <div className="flex flex-wrap items-center gap-4">
                      <div>
                        <span className="text-[10px] text-[#6f6449] block mb-1">
                          Girdi ({pair.input.length}x{pair.input[0]?.length})
                        </span>
                        {renderGrid(pair.input)}
                      </div>
                      <ChevronRight className="w-5 h-5 text-[#6f6449] hidden sm:block" />
                      <div>
                        <span className="text-[10px] text-[#6f6449] block mb-1">
                          Hedef Çıktı ({pair.output.length}x{pair.output[0]?.length})
                        </span>
                        {renderGrid(pair.output)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Test Input & Prediction */}
            <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-4">
              <div className="flex items-center justify-between border-b border-[#362f22] pb-3">
                <span className="text-sm font-semibold text-[#ece3cf] flex items-center gap-2">
                  <Eye className="w-4 h-4 text-[#7ba05b]" />
                  Test Vakası ve Modelin İntacı
                </span>
                <span className="text-xs text-[#a89a78]">Çözüm Matrisi</span>
              </div>

              <div className="flex flex-wrap items-start gap-6">
                <div>
                  <span className="text-xs text-[#a89a78] font-mono-code block mb-1.5">
                    Test Girdisi
                  </span>
                  {renderGrid(currentTask.test[0]?.input || [[0]])}
                </div>

                <ChevronRight className="w-5 h-5 text-[#6f6449] mt-6 hidden sm:block" />

                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-mono-code text-[#e08856]">
                      {simulationResult ? 'Model İntacı (Muhakeme & Tafsil)' : 'Etkileşimli Tuval'}
                    </span>
                    <button
                      onClick={() => {
                        const init = currentTask.test[0]?.input || [[0]];
                        setInteractiveGrid(init.map(r => [...r]));
                      }}
                      className="text-[10px] text-[#a89a78] hover:text-[#ece3cf] flex items-center gap-1"
                    >
                      <RefreshCw className="w-2.5 h-2.5" /> Sıfırla
                    </button>
                  </div>
                  {renderGrid(interactiveGrid, true)}
                </div>

                {/* If test output is available in training tasks */}
                {currentTask.test[0]?.output && (
                  <div>
                    <span className="text-xs text-[#7ba05b] font-mono-code block mb-1.5">
                      Doğru Çözüm (Zemin Gerçeği)
                    </span>
                    {renderGrid(currentTask.test[0].output)}
                  </div>
                )}
              </div>

              {/* Palette */}
              <div className="bg-[#16130e] p-3 rounded-lg border border-[#362f22] space-y-2 mt-4">
                <span className="text-[11px] font-mono-code text-[#a89a78] flex items-center gap-1.5">
                  <Palette className="w-3.5 h-3.5" />
                  Renk Paleti (Hücreye tıklayarak boyayabilirsiniz):
                </span>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(ARC_COLORS).map(([val, info]) => {
                    const num = Number(val);
                    return (
                      <button
                        key={val}
                        onClick={() => setSelectedPaintColor(num)}
                        className={`w-7 h-7 rounded flex items-center justify-center text-xs font-bold transition-transform ${
                          selectedPaintColor === num ? 'ring-2 ring-[#ece3cf] scale-110' : 'opacity-80 hover:opacity-100'
                        }`}
                        style={{ backgroundColor: info.hex }}
                        title={`${num}: ${info.name}`}
                      >
                        <span className={num === 4 ? 'text-black' : 'text-white'}>{num}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Reasoning Trace */}
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-4 sticky top-4">
              <div className="flex items-center justify-between border-b border-[#362f22] pb-3">
                <h4 className="text-sm font-semibold text-[#ece3cf] flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-[#e08856]" />
                  Zihnî Meleke İcra Silsilesi
                </h4>
                {simulationResult && (
                  <span className="text-xs px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                    {simulationResult.elapsedMs} ms
                  </span>
                )}
              </div>

              {simulationResult ? (
                <div className="space-y-4">
                  {/* Invariant / Rule detected */}
                  <div className="bg-[#16130e] p-3.5 rounded-lg border border-[#362f22] space-y-1.5">
                    <span className="text-[10px] font-mono-code text-[#e08856] uppercase tracking-wider">
                      İstihraç Edilen Kaide &amp; İnvariant
                    </span>
                    <p className="text-sm font-semibold text-[#ece3cf]">
                      {simulationResult.detectedRule}
                    </p>
                    <div className="flex items-center justify-between text-xs text-[#a89a78] pt-1">
                      <span>Sadakat Güveni: %{(simulationResult.accuracyConfidence * 100).toFixed(1)}</span>
                      <span>Fubini-Study: {simulationResult.fubiniStudyMetric}</span>
                    </div>
                  </div>

                  {/* Step by step faculty execution trace */}
                  <div className="space-y-2.5 max-h-[420px] overflow-y-auto pr-1">
                    {simulationResult.trace.map((step, idx) => (
                      <div
                        key={idx}
                        className="bg-[#16130e] border border-[#362f22] p-3 rounded-lg space-y-1 hover:border-[#6f6449] transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-mono-code text-[#a89a78]">
                            {step.tier}
                          </span>
                          <span className="text-[10px] font-mono-code text-[#6f6449]">
                            {step.sure}
                          </span>
                        </div>
                        <h5 className="text-xs font-bold text-[#e08856]">
                          {step.meleke}
                        </h5>
                        <p className="text-xs text-[#ece3cf] leading-relaxed">
                          {step.eylem}
                        </p>
                      </div>
                    ))}
                  </div>

                  <div className="bg-[#3a2418]/50 border border-[#e08856]/40 p-3 rounded-lg flex items-center gap-2 text-xs text-[#ece3cf]">
                    <CheckCircle2 className="w-4 h-4 text-[#e08856] flex-shrink-0" />
                    <span>Fermân 2-Ĵ deterministik okumasıyla intaç tamamlandı.</span>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-[#a89a78] space-y-3">
                  <Play className="w-8 h-8 text-[#6f6449] mx-auto opacity-50" />
                  <p className="text-xs leading-relaxed">
                    Yukarıdaki <strong>"Zihnî Akışı Başlat"</strong> düğmesine tıklayarak 43 melekeden oluşan idrak zincirini bu görev üzerinde koşturabilirsiniz.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
