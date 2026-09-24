import React, { useState, useMemo } from 'react';
import { Meleke } from '../types';
import { Search, Filter, Compass, ArrowRight, ArrowLeft, Cpu, Activity, ShieldCheck, Zap } from 'lucide-react';

interface FacultyMapProps {
  melekeler: Meleke[];
  onSelectMeleke?: (meleke: Meleke) => void;
}

export const FacultyMap: React.FC<FacultyMapProps> = ({ melekeler }) => {
  const [selectedMeleke, setSelectedMeleke] = useState<Meleke | null>(
    melekeler.find(m => m.ad === 'Muhakeme') || melekeler[0] || null
  );
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTier, setSelectedTier] = useState<number | 'all'>('all');
  const [selectedRole, setSelectedRole] = useState<string>('all');

  const tiers = [
    { no: 1, name: 'Ham Algı', color: '#e08856' },
    { no: 2, name: 'Ham Malzeme', color: '#c49a45' },
    { no: 3, name: 'Kavramsallaştırma', color: '#7ba05b' },
    { no: 4, name: 'Sınama ve Kıyas', color: '#4aa3a2' },
    { no: 5, name: 'Derin Muhakeme Çekirdeği', color: '#5b82c4' },
    { no: 6, name: 'Hüküm', color: '#b06ec9' },
    { no: 7, name: 'Yön ve Gaye', color: '#d9534f' },
    { no: 8, name: 'Beyan', color: '#38a169' },
    { no: 9, name: 'Kapanış', color: '#805ad5' },
  ];

  const filteredMelekeler = useMemo(() => {
    return melekeler.filter(m => {
      const matchSearch = m.ad.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.tanim.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.tierAd.toLowerCase().includes(searchTerm.toLowerCase());
      const matchTier = selectedTier === 'all' || m.tier === selectedTier;
      const matchRole = selectedRole === 'all' || m.rol === selectedRole;
      return matchSearch && matchTier && matchRole;
    });
  }, [melekeler, searchTerm, selectedTier, selectedRole]);

  // Check relationship to selected meleke
  const isIncoming = (ad: string) => selectedMeleke?.girisler.includes(ad);
  const isOutgoing = (ad: string) => selectedMeleke?.cikislar.includes(ad);

  return (
    <div className="flex flex-col lg:flex-row gap-6 w-full">
      {/* Left/Main Column: Controls & Grid Canvas */}
      <div className="flex-1 flex flex-col space-y-4">
        {/* Filter Bar */}
        <div className="bg-[#1c1810] border border-[#362f22] p-4 rounded-xl flex flex-wrap gap-4 items-center justify-between">
          <div className="relative flex-1 min-w-[220px]">
            <Search className="w-4 h-4 text-[#a89a78] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Meleke ara (örn. Muhakeme, Mana, Kıyas)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#16130e] border border-[#362f22] rounded-lg pl-9 pr-4 py-2 text-sm text-[#ece3cf] placeholder-[#6f6449] focus:outline-none focus:border-[#e08856]"
            />
          </div>

          {/* Tier Filter */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-[#a89a78] uppercase tracking-wider flex items-center gap-1 font-mono-code">
              <Filter className="w-3.5 h-3.5" /> Kademe:
            </span>
            <select
              value={selectedTier}
              onChange={(e) => setSelectedTier(e.target.value === 'all' ? 'all' : Number(e.target.value))}
              className="bg-[#16130e] border border-[#362f22] rounded-lg px-3 py-1.5 text-xs text-[#ece3cf] focus:outline-none focus:border-[#e08856]"
            >
              <option value="all">Bütün Kademeler (9 Alt Harita)</option>
              {tiers.map(t => (
                <option key={t.no} value={t.no}>Tier {t.no}: {t.name}</option>
              ))}
            </select>
          </div>

          {/* Role Filter */}
          <div className="flex items-center gap-1.5 bg-[#16130e] p-1 rounded-lg border border-[#362f22]">
            {['all', 'kurucu', 'koruyucu', 'çözücü'].map((role) => (
              <button
                key={role}
                onClick={() => setSelectedRole(role)}
                className={`px-2.5 py-1 text-xs rounded capitalize transition-colors ${
                  selectedRole === role
                    ? 'bg-[#3a2418] text-[#e08856] font-semibold border border-[#e08856]/40'
                    : 'text-[#a89a78] hover:text-[#ece3cf]'
                }`}
              >
                {role === 'all' ? 'Tümü' : role}
              </button>
            ))}
          </div>
        </div>

        {/* Tiers Visual Grid */}
        <div className="space-y-4">
          {tiers.map((tier) => {
            const tierMelekeler = filteredMelekeler.filter(m => m.tier === tier.no);
            if (tierMelekeler.length === 0 && selectedTier !== 'all') return null;

            return (
              <div
                key={tier.no}
                className="bg-[#1c1810]/70 border border-[#362f22] rounded-xl p-4 transition-all"
              >
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-[#362f22]">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: tier.color }} />
                    <span className="text-xs font-mono-code text-[#a89a78] uppercase tracking-wider">
                      Alt Harita {tier.no}
                    </span>
                    <span className="text-sm font-semibold text-[#ece3cf]">{tier.name}</span>
                  </div>
                  <span className="text-xs font-mono-code text-[#6f6449]">
                    {tierMelekeler.length} Meleke
                  </span>
                </div>

                {tierMelekeler.length === 0 ? (
                  <p className="text-xs text-[#6f6449] italic py-2">Filtreye uyan meleke bulunamadı.</p>
                ) : (
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-3">
                    {tierMelekeler.map((m) => {
                      const isSelected = selectedMeleke?.id === m.id;
                      const incoming = isIncoming(m.ad);
                      const outgoing = isOutgoing(m.ad);

                      return (
                        <button
                          key={m.id}
                          onClick={() => setSelectedMeleke(m)}
                          className={`relative p-3 rounded-lg border text-left transition-all group flex flex-col justify-between ${
                            isSelected
                              ? 'bg-[#3a2418] border-[#e08856] ring-1 ring-[#e08856] shadow-lg shadow-[#e08856]/10'
                              : incoming
                              ? 'bg-[#212b1e] border-[#7ba05b] text-[#ece3cf]'
                              : outgoing
                              ? 'bg-[#1b2533] border-[#5b82c4] text-[#ece3cf]'
                              : 'bg-[#16130e] border-[#362f22] hover:border-[#6f6449] hover:bg-[#1a1712]'
                          }`}
                        >
                          <div>
                            <div className="flex items-center justify-between gap-1 mb-1.5">
                              <span className="text-[10px] font-mono-code text-[#a89a78]">
                                𝒪{m.no}
                              </span>
                              <span
                                className={`text-[9px] px-1.5 py-0.5 rounded capitalize font-medium ${
                                  m.rol === 'kurucu'
                                    ? 'bg-amber-950/60 text-amber-300 border border-amber-800/40'
                                    : m.rol === 'koruyucu'
                                    ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/40'
                                    : 'bg-rose-950/60 text-rose-300 border border-rose-800/40'
                                }`}
                              >
                                {m.rol}
                              </span>
                            </div>
                            <h4 className="text-sm font-semibold text-[#ece3cf] group-hover:text-[#e08856] transition-colors leading-tight">
                              {m.ad}
                            </h4>
                          </div>

                          <div className="mt-2 pt-2 border-t border-[#362f22]/50 flex items-center justify-between text-[10px] text-[#a89a78]">
                            <span>{m.girisler.length} girdi</span>
                            <span>{m.cikislar.length} çıktı</span>
                          </div>

                          {/* Relationship indicator badges */}
                          {incoming && (
                            <span className="absolute -top-1.5 -left-1.5 bg-[#7ba05b] text-[#16130e] text-[9px] font-bold px-1 rounded shadow">
                              GİRDİ
                            </span>
                          )}
                          {outgoing && (
                            <span className="absolute -top-1.5 -right-1.5 bg-[#5b82c4] text-[#ece3cf] text-[9px] font-bold px-1 rounded shadow">
                              ÇIKTI
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Column: Meleke Inspector Panel */}
      <div className="w-full lg:w-96 flex flex-col space-y-4">
        {selectedMeleke ? (
          <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl sticky top-4 space-y-5">
            {/* Header */}
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono-code text-[#e08856] font-semibold">
                  MELEKE 𝒪{selectedMeleke.no} &middot; TIER {selectedMeleke.tier}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded capitalize font-medium ${
                    selectedMeleke.rol === 'kurucu'
                      ? 'bg-amber-950/60 text-amber-300 border border-amber-800/40'
                      : selectedMeleke.rol === 'koruyucu'
                      ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/40'
                      : 'bg-rose-950/60 text-rose-300 border border-rose-800/40'
                  }`}
                >
                  {selectedMeleke.rol}
                </span>
              </div>
              <h3 className="text-2xl font-serif-fraunces font-bold text-[#ece3cf] mt-1">
                {selectedMeleke.ad}
              </h3>
              <p className="text-xs text-[#a89a78] mt-0.5">Alt Harita: {selectedMeleke.tierAd}</p>
            </div>

            {/* Description */}
            <div className="bg-[#16130e] p-3.5 rounded-lg border border-[#362f22] space-y-2">
              <span className="text-[11px] font-mono-code text-[#a89a78] uppercase tracking-wider block">
                Zihnî Fonksiyon &amp; Rol
              </span>
              <p className="text-sm text-[#ece3cf] leading-relaxed">
                {selectedMeleke.tanim}
              </p>
            </div>

            {/* Quantum Operation Profile */}
            <div className="bg-[#16130e] p-3.5 rounded-lg border border-[#362f22] space-y-2">
              <span className="text-[11px] font-mono-code text-[#a89a78] uppercase tracking-wider flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-[#e08856]" />
                Kuantum Kapı ve Operatör Profili
              </span>
              <p className="text-xs font-mono-code text-[#e08856] bg-[#3a2418]/60 p-2 rounded border border-[#e08856]/30">
                {selectedMeleke.kapiTipi}
              </p>
              <p className="text-xs text-[#a89a78] leading-normal pt-1">
                {selectedMeleke.detay}
              </p>
            </div>

            {/* Incoming Connections */}
            <div className="space-y-2">
              <span className="text-xs font-mono-code text-[#a89a78] uppercase tracking-wider flex items-center gap-1.5">
                <ArrowLeft className="w-3.5 h-3.5 text-[#7ba05b]" />
                Besleyen Melekeler (Girdiler - {selectedMeleke.girisler.length}):
              </span>
              <div className="flex flex-wrap gap-1.5">
                {selectedMeleke.girisler.map((ad, idx) => {
                  const target = melekeler.find(m => m.ad === ad);
                  return (
                    <button
                      key={idx}
                      onClick={() => target && setSelectedMeleke(target)}
                      className="text-xs px-2.5 py-1 rounded bg-[#212b1e] border border-[#7ba05b]/40 text-[#ece3cf] hover:border-[#7ba05b] hover:bg-[#2b3927] transition-colors"
                    >
                      {ad}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Outgoing Connections */}
            <div className="space-y-2">
              <span className="text-xs font-mono-code text-[#a89a78] uppercase tracking-wider flex items-center gap-1.5">
                <ArrowRight className="w-3.5 h-3.5 text-[#5b82c4]" />
                Beslediği Melekeler (Çıktılar - {selectedMeleke.cikislar.length}):
              </span>
              <div className="flex flex-wrap gap-1.5">
                {selectedMeleke.cikislar.map((ad, idx) => {
                  const target = melekeler.find(m => m.ad === ad);
                  return (
                    <button
                      key={idx}
                      onClick={() => target && setSelectedMeleke(target)}
                      className="text-xs px-2.5 py-1 rounded bg-[#1b2533] border border-[#5b82c4]/40 text-[#ece3cf] hover:border-[#5b82c4] hover:bg-[#233145] transition-colors"
                    >
                      {ad}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Note on Muhakeme central role */}
            {selectedMeleke.ad === 'Muhakeme' && (
              <div className="bg-[#2a1d2e] border border-[#b06ec9]/50 p-3 rounded-lg text-xs text-[#ece3cf]">
                <strong className="text-[#b06ec9] block mb-1">⭐ Şebekenin Kalbi:</strong>
                Muhakeme, belgede 11 farklı melekeden doğrudan girdi alan ve Hüküm alt haritasının fiilî toplama noktası olan merkezdir.
              </div>
            )}
          </div>
        ) : (
          <div className="bg-[#1c1810] border border-[#362f22] p-8 rounded-xl text-center text-[#a89a78] flex flex-col items-center justify-center space-y-2">
            <Compass className="w-8 h-8 text-[#6f6449]" />
            <p className="text-sm">Ayrıntılarını incelemek için bir meleke seçin.</p>
          </div>
        )}
      </div>
    </div>
  );
};
