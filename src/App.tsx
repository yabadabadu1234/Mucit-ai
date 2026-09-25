import React, { useState, useEffect } from 'react';
import { Meleke } from './types';
import { FacultyMap } from './components/FacultyMap';
import { ArcLab } from './components/ArcLab';
import { QuantumSimulator } from './components/QuantumSimulator';
import { MizanTelemetry } from './components/MizanTelemetry';
import { TreatisesReader } from './components/TreatisesReader';
import { CommandCenter } from './components/CommandCenter';
import { InferenceChat } from './components/InferenceChat';
import { Compass, Grid, Atom, Activity, BookOpen, Terminal, Sparkles, MessageSquare } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'console' | 'map' | 'arc' | 'quantum' | 'mizan' | 'docs'>('chat');
  const [melekeler, setMelekeler] = useState<Meleke[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadInitial() {
      try {
        const res = await fetch('/api/melekeler');
        const data = await res.json();
        if (data.success) {
          setMelekeler(data.melekeler);
        }
      } catch (err) {
        console.error('Failed to load faculties:', err);
      } finally {
        setLoading(false);
      }
    }
    loadInitial();
  }, []);

  return (
    <div className="min-h-screen bg-[#16130e] text-[#ece3cf] flex flex-col">
      {/* Top Header Bar */}
      <header className="border-b border-[#362f22] bg-[#1c1810]/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#3a2418] border border-[#e08856]/50 flex items-center justify-center text-[#e08856] shadow-md">
              <span className="text-xl font-serif-fraunces font-bold">ن</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-serif-fraunces font-bold tracking-tight text-[#ece3cf]">
                  Mucit-AI &middot; Nefs-i Müdrike
                </h1>
                <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-[#3a2418] text-[#e08856] border border-[#e08856]/30">
                  v1.0 &middot; 43 Meleke
                </span>
              </div>
              <p className="text-xs text-[#a89a78] hidden sm:block">
                Bilişsel Meleke Haritası, ARC-AGI-2 Akıl Yürütme Laboratuvarı ve Kuantum İdrak Paneli
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1.5 bg-[#16130e] p-1 rounded-xl border border-[#362f22]">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'chat'
                  ? 'bg-[#3a2418] text-[#e08856] border border-[#e08856]/40 shadow-sm'
                  : 'text-[#a89a78] hover:text-[#ece3cf]'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5 text-[#e08856]" />
              <span>Sual &amp; Çıkarım (Dil Modeli)</span>
            </button>

            <button
              onClick={() => setActiveTab('console')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'console'
                  ? 'bg-[#3a2418] text-[#e08856] border border-[#e08856]/40 shadow-sm'
                  : 'text-[#a89a78] hover:text-[#ece3cf]'
              }`}
            >
              <Terminal className="w-3.5 h-3.5 text-[#e08856]" />
              <span>Kumanda &amp; Canlı Konsol</span>
            </button>

            <button
              onClick={() => setActiveTab('map')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'map'
                  ? 'bg-[#3a2418] text-[#e08856] border border-[#e08856]/40 shadow-sm'
                  : 'text-[#a89a78] hover:text-[#ece3cf]'
              }`}
            >
              <Compass className="w-3.5 h-3.5" />
              <span>Meleke Haritası</span>
            </button>

            <button
              onClick={() => setActiveTab('arc')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'arc'
                  ? 'bg-[#3a2418] text-[#e08856] border border-[#e08856]/40 shadow-sm'
                  : 'text-[#a89a78] hover:text-[#ece3cf]'
              }`}
            >
              <Grid className="w-3.5 h-3.5" />
              <span>ARC-AGI-2 Lab</span>
            </button>

            <button
              onClick={() => setActiveTab('quantum')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'quantum'
                  ? 'bg-[#3a2418] text-[#e08856] border border-[#e08856]/40 shadow-sm'
                  : 'text-[#a89a78] hover:text-[#ece3cf]'
              }`}
            >
              <Atom className="w-3.5 h-3.5" />
              <span>Qudit &amp; KAN-NQS</span>
            </button>

            <button
              onClick={() => setActiveTab('mizan')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'mizan'
                  ? 'bg-[#3a2418] text-[#e08856] border border-[#e08856]/40 shadow-sm'
                  : 'text-[#a89a78] hover:text-[#ece3cf]'
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              <span>Mîzân Telemetri</span>
            </button>

            <button
              onClick={() => setActiveTab('docs')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'docs'
                  ? 'bg-[#3a2418] text-[#e08856] border border-[#e08856]/40 shadow-sm'
                  : 'text-[#a89a78] hover:text-[#ece3cf]'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Külliyat</span>
            </button>
          </nav>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-[#a89a78]">
            <Sparkles className="w-8 h-8 text-[#e08856] animate-pulse mb-3" />
            <p className="text-sm">Nefs-i Müdrike melekeleri yükleniyor...</p>
          </div>
        ) : (
          <>
            {activeTab === 'chat' && <InferenceChat />}
            {activeTab === 'console' && <CommandCenter />}
            {activeTab === 'map' && <FacultyMap melekeler={melekeler} />}
            {activeTab === 'arc' && <ArcLab />}
            {activeTab === 'quantum' && <QuantumSimulator />}
            {activeTab === 'mizan' && <MizanTelemetry />}
            {activeTab === 'docs' && <TreatisesReader />}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-[#362f22] bg-[#1c1810] py-4 text-xs text-[#a89a78]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>Nefs-i Müdrike Mimari Şebekesi &middot; 43 Meleke &middot; 9 Alt Harita &middot; 245 Bağlantı</span>
          </div>
          <div className="font-mono-code text-[11px] text-[#6f6449]">
            AI Studio Node.js Runtime &middot; Port 3000
          </div>
        </div>
      </footer>
    </div>
  );
}
