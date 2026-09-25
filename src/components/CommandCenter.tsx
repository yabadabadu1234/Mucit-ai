import React, { useState, useEffect, useRef } from 'react';
import {
  Play,
  Square,
  Terminal as TerminalIcon,
  Shield,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Copy,
  Download,
  Trash2,
  Sliders,
  Cpu,
  Zap,
  ArrowRight,
  Activity,
  Layers,
  Sparkles,
  Database,
  ExternalLink,
  PlusCircle,
  CheckSquare,
  Square as SquareBox,
  Filter,
  Search,
  BookOpen,
  Box
} from 'lucide-react';

interface LogEntry {
  id: string;
  time: string;
  level: string;
  message: string;
  raw: string;
}

interface VerisetiItem {
  ad: string;
  sahip_isim: string;
  kategori: string;
  surum: string;
  varlik: string;
  pay: number;
  alindi: boolean;
  boyut_bayt: number;
  ornek_sayisi: number;
  ozel_mi: boolean;
  release_url: string;
}

export function CommandCenter() {
  const [selectedMode, setSelectedMode] = useState<'dar' | 'dengeli' | 'kulliyet' | 'ozel'>('dengeli');
  const [customDongu, setCustomDongu] = useState(15);
  const [customGorev, setCustomGorev] = useState(10);
  const [customKapi, setCustomKapi] = useState(51);
  const [customT0, setCustomT0] = useState(8.0);
  const [customTau, setCustomTau] = useState(2.0);

  const [includeReleases, setIncludeReleases] = useState(true);
  const [cikarimMetni, setCikarimMetni] = useState('Penguen bir kuştur fakat suda yüzer');
  const [activeProcess, setActiveProcess] = useState<'idle' | 'egit' | 'test' | 'cikarim'>('idle');
  const [progressLabel, setProgressLabel] = useState('');
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const [copySuccess, setCopySuccess] = useState(false);
  const [lastResult, setLastResult] = useState<any>(null);

  // Veriseti ve Release State
  const [verisetleri, setVerisetleri] = useState<VerisetiItem[]>([]);
  const [selectedDatasets, setSelectedDatasets] = useState<string[]>([]);
  const [datasetFilter, setDatasetFilter] = useState<'all' | 'lugat' | 'kadim_turkce' | 'yek_kitap' | 'release_koprusu' | 'arc' | 'riyaziye' | 'kelam' | 'ozel_release'>('all');
  const [datasetSearch, setDatasetSearch] = useState('');
  const [loadingDatasets, setLoadingDatasets] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);

  // Yeni Release Ekleme Formu
  const [yeniAd, setYeniAd] = useState('');
  const [yeniSahip, setYeniSahip] = useState('');
  const [yeniSurum, setYeniSurum] = useState('v1.0.0');
  const [yeniVarlik, setYeniVarlik] = useState('');
  const [yeniPay, setYeniPay] = useState(3.0);
  const [yeniDogrudanUrl, setYeniDogrudanUrl] = useState('');
  const [eklemeHatasi, setEklemeHatasi] = useState('');

  const terminalEndRef = useRef<HTMLDivElement>(null);
  const terminalContainerRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Verisetlerini sunucudan yükle
  const verisetleriniYukle = async () => {
    setLoadingDatasets(true);
    try {
      const res = await fetch('/api/kulliyat/verisetleri');
      const data = await res.json();
      if (data.success && data.verisetleri) {
        setVerisetleri(data.verisetleri);
      }
    } catch (err) {
      console.error('Verisetleri yüklenemedi:', err);
    } finally {
      setLoadingDatasets(false);
    }
  };

  // Sayfa açıldığında sunucudaki kalıcı logları ve aktif eğitimi geri yükle
  const sunucuDurumunuVeLoglariYukle = async () => {
    try {
      const res = await fetch('/api/kulliyat/status');
      const data = await res.json();
      if (data.loglar && Array.isArray(data.loglar) && data.loglar.length > 0) {
        const parsed = data.loglar.map((l: string) => parseLogLine(l));
        setLogs(parsed);
      }
      if (data.gorev) {
        if (data.gorev.durum === 'calisiyor') {
          setActiveProcess(data.gorev.activeProcess || 'egit');
          setProgressLabel(data.gorev.progressLabel || 'Arka Planda Eğitim Devam Ediyor...');
          baglanSSE();
        } else {
          setActiveProcess('idle');
          if (data.gorev.sonuc) {
            setLastResult(data.gorev.sonuc);
          }
        }
      }
    } catch (err) {
      console.error('Kalıcı durum yüklenemedi:', err);
    }
  };

  const baglanSSE = (paramUrl?: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    const url = paramUrl || '/api/kulliyat/stream-exec';
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'log') {
          appendLog(payload.line);
        } else if (payload.type === 'start') {
          setActiveProcess(payload.action);
          setProgressLabel(payload.progressLabel);
        } else if (payload.type === 'result') {
          setLastResult(payload.data);
        } else if (payload.type === 'done') {
          setActiveProcess('idle');
          appendLog(`[${new Date().toLocaleTimeString('tr-TR')}] [TAMAM] İşlem ${payload.durum || 'tamamlandı'}.`);
          es.close();
        } else if (payload.type === 'error') {
          setActiveProcess('idle');
          appendLog(`[${new Date().toLocaleTimeString('tr-TR')}] [HATA] ${payload.message}`);
          es.close();
        }
      } catch {
        appendLog(`[${new Date().toLocaleTimeString('tr-TR')}] [BILGI] ${event.data}`);
      }
    };

    es.onerror = () => {
      // Bağlantı koptuğunda arka plan prosesi çalışmaya devam eder
      setTimeout(() => {
        fetch('/api/kulliyat/status')
          .then(r => r.json())
          .then(d => {
            if (d.gorev?.durum === 'calisiyor') {
              baglanSSE();
            } else {
              setActiveProcess('idle');
              if (d.gorev?.sonuc) setLastResult(d.gorev.sonuc);
            }
          })
          .catch(() => {});
      }, 3000);
    };
  };

  useEffect(() => {
    verisetleriniYukle();
    sunucuDurumunuVeLoglariYukle();
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    let timer: any;
    if (activeProcess !== 'idle') {
      timer = setInterval(() => {
        setElapsedSeconds(prev => prev + 1);
      }, 1000);
    } else {
      setElapsedSeconds(0);
    }
    return () => clearInterval(timer);
  }, [activeProcess]);

  useEffect(() => {
    if (autoScroll && terminalContainerRef.current) {
      // scrollIntoView tüm sayfayı (window) aşağı çekiyordu.
      // Sadece konsol kutusunun kendi içini aşağı kaydırıyoruz:
      terminalContainerRef.current.scrollTop = terminalContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const parseLogLine = (rawLine: string): LogEntry => {
    const timeMatch = rawLine.match(/\[(\d{2}:\d{2}:\d{2})\]/);
    const levelMatch = rawLine.match(/\[([A-Z0-9_]+)\]/g);
    
    let time = timeMatch ? timeMatch[1] : new Date().toLocaleTimeString('tr-TR');
    let level = 'BILGI';
    
    if (levelMatch && levelMatch.length > 1) {
      level = levelMatch[1].replace(/[\[\]]/g, '');
    } else if (levelMatch && levelMatch.length === 1 && !timeMatch) {
      level = levelMatch[0].replace(/[\[\]]/g, '');
    }

    let message = rawLine.replace(/\[\d{2}:\d{2}:\d{2}\]/, '').replace(/\[[A-Z0-9_]+\]/, '').trim();
    if (!message) message = rawLine;

    return {
      id: Math.random().toString(36).substring(2, 9),
      time,
      level,
      message,
      raw: rawLine
    };
  };

  const appendLog = (line: string) => {
    const entry = parseLogLine(line);
    setLogs(prev => [...prev, entry]);
  };

  const durdur = async () => {
    try {
      await fetch('/api/kulliyat/durdur', { method: 'POST' });
    } catch {}
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setActiveProcess('idle');
    appendLog(`[${new Date().toLocaleTimeString('tr-TR')}] [UYARI] Kullanıcı tarafından durdurma emri gönderildi.`);
  };

  const calistir = (action: 'egit' | 'test' | 'cikarim', ozelSecili?: string[]) => {
    if (activeProcess !== 'idle') return;

    let targetLabel = '';
    let url = `/api/kulliyat/stream-exec?action=${action}`;
    if (action === 'egit') {
      const seciliList = ozelSecili || selectedDatasets;
      const seciliStr = seciliList.join(',');
      targetLabel = `Küllî Eğitim (${selectedMode.toUpperCase()}) İcra Ediliyor...`;
      url += `&mod=${selectedMode}&include_releases=${includeReleases}`;
      if (seciliStr) {
        url += `&secili_verisetleri=${encodeURIComponent(seciliStr)}`;
      }
      if (selectedMode === 'ozel') {
        url += `&dongu=${customDongu}&azami_gorev=${customGorev}&kapi_sayisi=${customKapi}&t0=${customT0}&tau=${customTau}`;
      }
    } else if (action === 'test') {
      targetLabel = '10 Küllî İdrak ve Release Teoremi Test Suiti İcra Ediliyor...';
    } else if (action === 'cikarim') {
      targetLabel = `Çıkarım Yapılıyor: "${cikarimMetni.slice(0, 30)}..."`;
      url += `&metin=${encodeURIComponent(cikarimMetni)}`;
    }

    setActiveProcess(action);
    setProgressLabel(targetLabel);
    setLastResult(null);

    appendLog(`[${new Date().toLocaleTimeString('tr-TR')}] [BASLAT] >>> ${targetLabel || action.toUpperCase()} tetiklendi.`);
    baglanSSE(url);
  };

  const yeniReleaseEkle = async (e: React.FormEvent) => {
    e.preventDefault();
    setEklemeHatasi('');
    if (!yeniAd.trim() || !yeniSahip.trim()) {
      setEklemeHatasi('Veriseti Adı ve GitHub Depo kimliği zorunludur.');
      return;
    }
    try {
      const res = await fetch('/api/kulliyat/veriseti-ekle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ad: yeniAd.trim(),
          sahip_isim: yeniSahip.trim(),
          surum: yeniSurum.trim(),
          varlik: yeniVarlik.trim(),
          pay: yeniPay,
          dogrudan_url: yeniDogrudanUrl.trim()
        })
      });
      const data = await res.json();
      if (data.success) {
        setShowAddModal(false);
        setYeniAd('');
        setYeniSahip('');
        setYeniVarlik('');
        setYeniDogrudanUrl('');
        await verisetleriniYukle();
        setSelectedDatasets(prev => [...prev, data.kaynak.ad]);
        appendLog(`[${new Date().toLocaleTimeString('tr-TR')}] [RELEASE] Yeni GitHub Release veriseti kaydedildi: '${data.kaynak.ad}'`);
      } else {
        setEklemeHatasi(data.error || 'Kayıt başarısız oldu.');
      }
    } catch (err: any) {
      setEklemeHatasi(err.message || 'Sunucu hatası.');
    }
  };

  const copyLogs = () => {
    const fullText = logs.map(l => l.raw).join('\n');
    navigator.clipboard.writeText(fullText);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const downloadLogs = () => {
    const fullText = logs.map(l => l.raw).join('\n');
    const blob = new Blob([fullText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `kulliyat-log-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const clearLogs = async () => {
    setLogs([]);
    try {
      await fetch('/api/kulliyat/log-temizle', { method: 'POST' });
    } catch {}
  };

  const filteredLogs = logs.filter(l => {
    if (activeFilter === 'all') return true;
    return l.level.toLowerCase().includes(activeFilter.toLowerCase());
  });

  const getLevelColor = (lvl: string) => {
    const u = lvl.toUpperCase();
    if (u.includes('RELEASE')) return 'text-cyan-300 bg-cyan-950/60 border-cyan-700/60 font-bold';
    if (u.includes('BORUHATTI')) return 'text-purple-300 bg-purple-950/60 border-purple-700/60';
    if (u.includes('KULLIYAT')) return 'text-amber-300 bg-amber-950/60 border-amber-700/60';
    if (u.includes('KUANTUM') || u.includes('ZIRH')) return 'text-indigo-400 bg-indigo-950/40 border-indigo-800/40';
    if (u.includes('TAHFIZ')) return 'text-amber-400 bg-amber-950/40 border-amber-800/40';
    if (u.includes('TAHKIK')) return 'text-sky-400 bg-sky-950/40 border-sky-800/40';
    if (u.includes('TEST')) return 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40';
    if (u.includes('HUKUM') || u.includes('SONUC')) return 'text-yellow-300 bg-yellow-950/40 border-yellow-700/50';
    if (u.includes('HATA')) return 'text-rose-400 bg-rose-950/50 border-rose-800/60';
    if (u.includes('UYARI')) return 'text-orange-400 bg-orange-950/40 border-orange-800/40';
    if (u.includes('CIKARIM')) return 'text-teal-300 bg-teal-950/40 border-teal-800/40';
    return 'text-[#a89a78] bg-[#221c14] border-[#362f22]';
  };

  const toggleSelectDataset = (ad: string) => {
    setSelectedDatasets(prev =>
      prev.includes(ad) ? prev.filter(x => x !== ad) : [...prev, ad]
    );
  };

  const selectAllReleases = () => {
    const releases = verisetleri
      .filter(v => v.kategori === 'release_koprusu' || v.kategori === 'ozel_release')
      .map(v => v.ad);
    setSelectedDatasets(releases);
  };

  const selectAllDatasets = () => {
    setSelectedDatasets(verisetleri.map(v => v.ad));
  };

  const clearSelectedDatasets = () => {
    setSelectedDatasets([]);
  };

  // Veriseti filtreleme
  const filteredDatasets = verisetleri.filter(v => {
    if (datasetFilter !== 'all' && v.kategori !== datasetFilter) return false;
    if (datasetSearch.trim()) {
      const q = datasetSearch.toLowerCase();
      return (
        v.ad.toLowerCase().includes(q) ||
        v.sahip_isim.toLowerCase().includes(q) ||
        v.varlik.toLowerCase().includes(q) ||
        v.surum.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const totalByteSize = verisetleri.reduce((acc, curr) => acc + (curr.boyut_bayt || 0), 0);
  const totalExamples = verisetleri.reduce((acc, curr) => acc + (curr.ornek_sayisi || 0), 0);
  const releaseCount = verisetleri.filter(v => v.kategori === 'release_koprusu' || v.kategori === 'ozel_release').length;

  return (
    <div className="space-y-6">
      {/* Top Banner / Telemetry Status */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-[#1c1810] via-[#241d13] to-[#1c1810] border border-[#362f22] flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-[#3a2418] border border-[#e08856]/40 flex items-center justify-center text-[#e08856] shadow-inner">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-serif-fraunces font-bold text-[#ece3cf]">
                Eğitim, Test &amp; Külliyat Kumanda Masası
              </h2>
              <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-[#3a2418] text-[#e08856] border border-[#e08856]/30">
                1,048,576 Qudit Zırhı
              </span>
              <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-700/50">
                GitHub Release Boru Hattı
              </span>
            </div>
            <p className="text-xs text-[#a89a78]">
              {verisetleri.length} Külliyat veriseti &middot; {releaseCount} GitHub Release köprüsü &middot; Ferman 1-O akış mimarisi
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {activeProcess !== 'idle' ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-950/40 border border-amber-600/50 text-amber-300 text-xs font-mono-code">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
              <span>{activeProcess.toUpperCase()} AKTİF ({elapsedSeconds}s)</span>
              <button
                onClick={durdur}
                className="ml-2 px-2 py-0.5 rounded bg-rose-950 hover:bg-rose-900 border border-rose-700/60 text-rose-300 text-[10px] font-sans flex items-center gap-1 transition-all"
              >
                <Square className="w-3 h-3 fill-current" />
                Durdur
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-950/30 border border-emerald-700/40 text-emerald-400 text-xs font-mono-code">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span>SİSTEM HAZIR (İdrak &amp; Release Boru Hattı Mühürlü)</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Grid: Control Deck (Left) & Terminal (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Triggers & Mode Config (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Card 1: Küllî Eğitim Modları */}
          <div className="p-4 rounded-xl bg-[#1c1810] border border-[#362f22] space-y-4">
            <div className="flex items-center justify-between border-b border-[#362f22] pb-2">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-[#e08856]" />
                <h3 className="text-sm font-semibold text-[#ece3cf]">Küllî Eğitim Modları</h3>
              </div>
              <span className="text-[10px] font-mono-code text-[#a89a78]">Fıtrat &amp; Rüşt</span>
            </div>

            {/* Mode Selector Cards */}
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setSelectedMode('dar')}
                className={`p-2.5 rounded-lg border text-left transition-all ${
                  selectedMode === 'dar'
                    ? 'bg-[#3a2418] border-[#e08856] text-[#ece3cf] shadow-md'
                    : 'bg-[#16130e] border-[#362f22] text-[#a89a78] hover:border-[#4d4230]'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs font-bold text-[#ece3cf]">Dar Bütçeli</span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-amber-950/60 text-amber-300 font-mono-code">Hızlı</span>
                </div>
                <div className="text-[10px] space-y-0.5 opacity-80 font-mono-code">
                  <div>5 Tahfîz &middot; 4 ARC</div>
                  <div>3 Külliyat/Release</div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setSelectedMode('dengeli')}
                className={`p-2.5 rounded-lg border text-left transition-all ${
                  selectedMode === 'dengeli'
                    ? 'bg-[#3a2418] border-[#e08856] text-[#ece3cf] shadow-md'
                    : 'bg-[#16130e] border-[#362f22] text-[#a89a78] hover:border-[#4d4230]'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs font-bold text-[#ece3cf]">Dengeli</span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-950/60 text-emerald-300 font-mono-code">Standart</span>
                </div>
                <div className="text-[10px] space-y-0.5 opacity-80 font-mono-code">
                  <div>12 Tahfîz &middot; 10 ARC</div>
                  <div>6 Külliyat/Release</div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setSelectedMode('kulliyet')}
                className={`p-2.5 rounded-lg border text-left transition-all ${
                  selectedMode === 'kulliyet'
                    ? 'bg-[#3a2418] border-[#e08856] text-[#ece3cf] shadow-md'
                    : 'bg-[#16130e] border-[#362f22] text-[#a89a78] hover:border-[#4d4230]'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs font-bold text-[#ece3cf]">Küllî (Derin)</span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-purple-950/60 text-purple-300 font-mono-code">Tam Zırh</span>
                </div>
                <div className="text-[10px] space-y-0.5 opacity-80 font-mono-code">
                  <div>20 Tahfîz &middot; 20 ARC</div>
                  <div>12 Külliyat/Release</div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setSelectedMode('ozel')}
                className={`p-2.5 rounded-lg border text-left transition-all ${
                  selectedMode === 'ozel'
                    ? 'bg-[#3a2418] border-[#e08856] text-[#ece3cf] shadow-md'
                    : 'bg-[#16130e] border-[#362f22] text-[#a89a78] hover:border-[#4d4230]'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs font-bold text-[#ece3cf]">Özel Mod</span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-sky-950/60 text-sky-300 font-mono-code">Parametrik</span>
                </div>
                <div className="text-[10px] space-y-0.5 opacity-80 font-mono-code">
                  <div>Serbest Ayar</div>
                  <div>Özelleştirilebilir</div>
                </div>
              </button>
            </div>

            {/* Custom Mode Sliders */}
            {selectedMode === 'ozel' && (
              <div className="p-3 rounded-lg bg-[#16130e] border border-[#362f22] space-y-3 text-xs font-mono-code">
                <div className="flex items-center justify-between">
                  <span className="text-[#a89a78]">Tahfîz Döngü Adedi:</span>
                  <span className="text-[#e08856] font-bold">{customDongu}</span>
                </div>
                <input
                  type="range"
                  min="2"
                  max="35"
                  value={customDongu}
                  onChange={(e) => setCustomDongu(Number(e.target.value))}
                  className="w-full accent-[#e08856]"
                />

                <div className="flex items-center justify-between">
                  <span className="text-[#a89a78]">ARC Görev Adedi:</span>
                  <span className="text-[#e08856] font-bold">{customGorev}</span>
                </div>
                <input
                  type="range"
                  min="2"
                  max="30"
                  value={customGorev}
                  onChange={(e) => setCustomGorev(Number(e.target.value))}
                  className="w-full accent-[#e08856]"
                />

                <div className="flex items-center justify-between">
                  <span className="text-[#a89a78]">Zırh Kapı Adedi:</span>
                  <span className="text-[#e08856] font-bold">{customKapi} Kapı</span>
                </div>
                <input
                  type="range"
                  min="20"
                  max="102"
                  value={customKapi}
                  onChange={(e) => setCustomKapi(Number(e.target.value))}
                  className="w-full accent-[#e08856]"
                />

                <div className="grid grid-cols-2 gap-2 pt-1">
                  <div>
                    <label className="text-[10px] text-[#a89a78] block">Rüşt Başlangıcı (t0):</label>
                    <input
                      type="number"
                      step="0.5"
                      value={customT0}
                      onChange={(e) => setCustomT0(Number(e.target.value))}
                      className="w-full px-2 py-1 rounded bg-[#221c14] border border-[#362f22] text-[#ece3cf] text-xs"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-[#a89a78] block">Gevşeme Hızı (tau):</label>
                    <input
                      type="number"
                      step="0.1"
                      value={customTau}
                      onChange={(e) => setCustomTau(Number(e.target.value))}
                      className="w-full px-2 py-1 rounded bg-[#221c14] border border-[#362f22] text-[#ece3cf] text-xs"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Release Inclusion Toggle */}
            <div className="p-3 rounded-lg bg-[#16130e] border border-[#362f22] flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" />
                <div>
                  <span className="text-xs font-semibold text-[#ece3cf] block">
                    GitHub Release &amp; Külliyatı Eğit
                  </span>
                  <span className="text-[10px] text-[#a89a78] block">
                    Ferman 1-O boru hattıyla akıt (UltraData-Math, FineMath, BARC vb.)
                  </span>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeReleases}
                  onChange={(e) => setIncludeReleases(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-9 h-5 bg-[#2a2217] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-[#ece3cf] after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-cyan-600"></div>
              </label>
            </div>

            {selectedDatasets.length > 0 && (
              <div className="px-3 py-2 rounded-lg bg-cyan-950/40 border border-cyan-800/40 text-[11px] font-mono-code text-cyan-300 flex items-center justify-between">
                <span>{selectedDatasets.length} veriseti özel olarak seçildi</span>
                <button
                  type="button"
                  onClick={clearSelectedDatasets}
                  className="text-[10px] text-[#a89a78] hover:text-[#ece3cf] underline"
                >
                  Seçimi Sıfırla
                </button>
              </div>
            )}

            {/* Launch Training Button */}
            <button
              onClick={() => calistir('egit')}
              disabled={activeProcess !== 'idle'}
              className="w-full py-2.5 rounded-lg bg-[#e08856] hover:bg-[#c97444] disabled:bg-[#362f22] disabled:text-[#6f6449] text-[#16130e] font-semibold text-xs transition-all flex items-center justify-center gap-2 shadow-md cursor-pointer disabled:cursor-not-allowed"
            >
              {activeProcess === 'egit' ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Küllî Eğitim &amp; Release Akışı İşleniyor...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Küllî Eğitimi Başlat ({selectedMode.toUpperCase()})</span>
                </>
              )}
            </button>
          </div>

          {/* Card 2: 10 Küllî İdrak & Release Teoremi Test Suiti */}
          <div className="p-4 rounded-xl bg-[#1c1810] border border-[#362f22] space-y-3">
            <div className="flex items-center justify-between border-b border-[#362f22] pb-2">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-semibold text-[#ece3cf]">Küllî Teorem Test Suiti</h3>
              </div>
              <span className="text-[10px] font-mono-code text-emerald-400">10/10 Teorem</span>
            </div>

            <p className="text-xs text-[#a89a78]">
              Bargmann İntaç, Wilson Holonomi, Hodge Ayrışımı, Epistemik Sheaf, Tabula Rasa, 1M Qudit Zırhı ve Ferman 1-O GitHub Release Boru Hattını doğrular.
            </p>

            <button
              onClick={() => calistir('test')}
              disabled={activeProcess !== 'idle'}
              className="w-full py-2.5 rounded-lg bg-emerald-700/80 hover:bg-emerald-600 disabled:bg-[#362f22] disabled:text-[#6f6449] text-[#ece3cf] font-semibold text-xs transition-all flex items-center justify-center gap-2 shadow-md cursor-pointer disabled:cursor-not-allowed"
            >
              {activeProcess === 'test' ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>10 Teorem Test Ediliyor...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>10 Küllî Teoremi Test Et</span>
                </>
              )}
            </button>
          </div>

          {/* Card 3: Canlı Çıkarım & Kaziye Denetimi */}
          <div className="p-4 rounded-xl bg-[#1c1810] border border-[#362f22] space-y-3">
            <div className="flex items-center justify-between border-b border-[#362f22] pb-2">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-sky-400" />
                <h3 className="text-sm font-semibold text-[#ece3cf]">Küllî Çıkarım &amp; Kaziye Tetikleyici</h3>
              </div>
              <span className="text-[10px] font-mono-code text-sky-400">Canlı Kanıt</span>
            </div>

            <div className="space-y-1.5">
              <label className="text-[11px] text-[#a89a78]">İncelenecek Kaziye / İddia Metni:</label>
              <input
                type="text"
                value={cikarimMetni}
                onChange={(e) => setCikarimMetni(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#16130e] border border-[#362f22] text-[#ece3cf] text-xs focus:border-[#e08856] focus:outline-none"
              />
              <div className="flex flex-wrap gap-1.5 pt-1">
                {[
                  'Yalan söylemek iyi bir şeydir',
                  'Penguen bir kuştur fakat suda yüzer',
                  'Ahmet şirkette amir olarak Mehmet\'e yetki verdi',
                  'Bütün insanlar fânidir, Sokrates insandır'
                ].map((orn, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setCikarimMetni(orn)}
                    className={`text-[10px] font-mono-code px-2 py-0.5 rounded border transition-all ${
                      orn.includes('Yalan')
                        ? 'bg-rose-950/40 hover:bg-rose-900/60 border-rose-800/50 text-rose-300'
                        : 'bg-[#241d13] hover:bg-[#33291b] border-[#362f22] text-[#a89a78] hover:text-[#ece3cf]'
                    }`}
                  >
                    {orn.slice(0, 24)}...
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={() => calistir('cikarim')}
              disabled={activeProcess !== 'idle'}
              className="w-full py-2.5 rounded-lg bg-sky-700/80 hover:bg-sky-600 disabled:bg-[#362f22] disabled:text-[#6f6449] text-[#ece3cf] font-semibold text-xs transition-all flex items-center justify-center gap-2 shadow-md cursor-pointer disabled:cursor-not-allowed"
            >
              {activeProcess === 'cikarim' ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Çıkarım Yapılıyor...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  <span>Kaziye Çıkarımını İcra Et</span>
                </>
              )}
            </button>
          </div>

        </div>

        {/* Right Column: Live Terminal & Output Drawer (7 cols) */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          
          {/* Terminal Window */}
          <div className="rounded-2xl bg-[#0e0c08] border border-[#362f22] shadow-2xl flex flex-col h-[620px] overflow-hidden">
            
            {/* Terminal Header */}
            <div className="px-4 py-3 bg-[#17130d] border-b border-[#362f22] flex flex-wrap items-center justify-between gap-3 select-none">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-rose-500/80 inline-block" />
                  <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
                  <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
                </div>
                <div className="flex items-center gap-2 ml-2">
                  <TerminalIcon className="w-4 h-4 text-[#e08856]" />
                  <span className="text-xs font-mono-code font-bold text-[#ece3cf]">
                    Nefs-i Müdrike // Küllî Canlı Konsol
                  </span>
                  <span className="text-[10px] font-mono-code px-1.5 py-0.2 rounded bg-[#241d13] text-[#a89a78] border border-[#362f22]">
                    {logs.length} satır
                  </span>
                </div>
              </div>

              {/* Terminal Quick Actions */}
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setAutoScroll(!autoScroll)}
                  className={`px-2 py-1 rounded text-[10px] font-mono-code border transition-all ${
                    autoScroll
                      ? 'bg-emerald-950/60 border-emerald-700/60 text-emerald-300'
                      : 'bg-[#221c14] border-[#362f22] text-[#a89a78]'
                  }`}
                  title="Konsolu otomatik aşağı kaydır"
                >
                  Oto-Kaydır: {autoScroll ? 'AÇIK' : 'KAPALI'}
                </button>

                <button
                  onClick={copyLogs}
                  className="p-1 rounded bg-[#221c14] hover:bg-[#33291b] border border-[#362f22] text-[#a89a78] hover:text-[#ece3cf] transition-all"
                  title="Logları kopyala"
                >
                  <Copy className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={downloadLogs}
                  className="p-1 rounded bg-[#221c14] hover:bg-[#33291b] border border-[#362f22] text-[#a89a78] hover:text-[#ece3cf] transition-all"
                  title="Logları indir (.txt)"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={clearLogs}
                  className="p-1 rounded bg-[#221c14] hover:bg-rose-950/50 border border-[#362f22] text-[#a89a78] hover:text-rose-300 transition-all"
                  title="Konsolu temizle"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Filter Bar */}
            <div className="px-4 py-1.5 bg-[#120f0a] border-b border-[#241f17] flex items-center gap-1.5 overflow-x-auto text-[10px] font-mono-code">
              <span className="text-[#6f6449] mr-1">Filtrele:</span>
              {['all', 'RELEASE', 'BORUHATTI', 'KULLIYAT', 'KUANTUM', 'TAHFIZ', 'TAHKIK', 'TEST', 'ZIRH', 'SONUC'].map((flt) => (
                <button
                  key={flt}
                  onClick={() => setActiveFilter(flt)}
                  className={`px-2 py-0.5 rounded transition-all whitespace-nowrap ${
                    activeFilter === flt
                      ? 'bg-[#e08856] text-[#16130e] font-bold'
                      : 'bg-[#1c1810] text-[#a89a78] hover:text-[#ece3cf] border border-[#362f22]'
                  }`}
                >
                  {flt.toUpperCase()}
                </button>
              ))}
              {copySuccess && (
                <span className="ml-auto text-emerald-400 font-bold animate-pulse">Kopyalandı!</span>
              )}
            </div>

            {/* Terminal Log Screen */}
            <div
              ref={terminalContainerRef}
              onScroll={(e) => {
                const target = e.currentTarget;
                const isNearBottom = target.scrollHeight - target.scrollTop - target.clientHeight < 60;
                // Kullanıcı elle yukarı kaydırdıysa oto-kaydırmayı devre dışı bırak, en alta indiyse tekrar aç
                if (!isNearBottom && autoScroll) {
                  setAutoScroll(false);
                } else if (isNearBottom && !autoScroll) {
                  setAutoScroll(true);
                }
              }}
              className="flex-1 p-4 overflow-y-auto font-mono-code text-[11px] leading-relaxed space-y-1.5 text-[#d4c8b0] bg-[#0c0a07]"
            >
              {logs.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-16 text-[#6f6449] space-y-2 select-none">
                  <TerminalIcon className="w-8 h-8 opacity-40" />
                  <p>Canlı telemetri akışı bekleniyor...</p>
                  <p className="text-[10px]">
                    Sol panelden veya aşağıdaki Veriseti Masasından eğitim, test veya çıkarım başlatınız.
                  </p>
                </div>
              ) : (
                filteredLogs.map((log) => (
                  <div key={log.id} className="flex items-start gap-2 hover:bg-[#1a150e]/60 py-0.5 px-1 rounded transition-colors">
                    <span className="text-[#6f6449] shrink-0 select-none text-[10px]">{log.time}</span>
                    <span className={`px-1.5 py-0.2 rounded text-[9px] border font-bold shrink-0 select-none ${getLevelColor(log.level)}`}>
                      {log.level}
                    </span>
                    <span className="break-all whitespace-pre-wrap">{log.message}</span>
                  </div>
                ))
              )}
              <div ref={terminalEndRef} />
            </div>

            {/* Terminal Status Footer */}
            <div className="px-4 py-2 bg-[#17130d] border-t border-[#362f22] flex items-center justify-between text-[10px] font-mono-code text-[#a89a78]">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>Boru Hattı Stream: Aktif</span>
              </div>
              <div className="flex items-center gap-3">
                <span>Zırh: 1,048,576 Qudit (2N=2,097,152)</span>
                <span>Faktörize Vakum: 100%</span>
              </div>
            </div>

          </div>

          {/* Structured Result Summary Card (Appears if lastResult exists) */}
          {lastResult && (
            <div className="p-4 rounded-xl bg-[#1c1810] border border-[#e08856]/40 space-y-3 animate-fade-in shadow-xl">
              <div className="flex items-center justify-between border-b border-[#362f22] pb-2">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-[#e08856]" />
                  <span className="text-xs font-bold font-serif-fraunces text-[#ece3cf]">
                    İşlem Neticesi Özeti
                  </span>
                </div>
                {lastResult.nihai_rust_makami && (
                  <span className="text-xs font-mono-code px-2 py-0.5 rounded bg-emerald-950 border border-emerald-700/50 text-emerald-300">
                    Makam: {lastResult.nihai_rust_makami} (α={lastResult.nihai_alpha})
                  </span>
                )}
                {lastResult.tum_testler_gecti && (
                  <span className="text-xs font-mono-code px-2 py-0.5 rounded bg-emerald-950 border border-emerald-700/50 text-emerald-300">
                    10/10 Teorem Geçti
                  </span>
                )}
                {lastResult.nihai_hukum && (
                  <span className={`text-xs font-mono-code px-2.5 py-0.5 rounded border font-bold ${
                    lastResult.nihai_hukum.includes('CERH') || lastResult.nihai_hukum.includes('İHLAL')
                      ? 'bg-rose-950/80 border-rose-700/60 text-rose-300'
                      : 'bg-emerald-950/80 border-emerald-700/60 text-emerald-300'
                  }`}>
                    {lastResult.nihai_hukum.includes('CERH') ? 'Möbius Cerhi (Red)' : 'Burhan Tasdiki'}
                  </span>
                )}
              </div>

              {/* Inference Verdict Details */}
              {lastResult.nihai_hukum && (
                <div className={`p-3 rounded-lg border text-xs font-mono-code space-y-1.5 ${
                  lastResult.nihai_hukum.includes('CERH')
                    ? 'bg-rose-950/30 border-rose-800/40 text-rose-200'
                    : 'bg-emerald-950/30 border-emerald-800/40 text-emerald-200'
                }`}>
                  <div className="font-bold flex items-center justify-between">
                    <span>Nihai Hüküm ve İdrak Neticesi:</span>
                    <span className="text-[10px] text-[#a89a78]">Ferman 1-G &middot; Ya İspat Ya Sükût</span>
                  </div>
                  <p className="text-[11px] leading-relaxed break-words">{lastResult.nihai_hukum}</p>
                  {lastResult.tenakuz_raporu?.cerh_sebebi && (
                    <div className="text-[10px] text-rose-400 bg-rose-950/60 p-2 rounded border border-rose-800/50 mt-1">
                      <strong>Tenakuz Tahlili:</strong> {lastResult.tenakuz_raporu.cerh_sebebi}
                    </div>
                  )}
                  {lastResult.vecih && (
                    <div className="flex flex-wrap gap-2 text-[10px] pt-1 text-[#a89a78]">
                      <span>Vecih: <strong className="text-[#ece3cf]">{lastResult.vecih.tip} ({lastResult.vecih.mertebe})</strong></span>
                      <span>İntaç: <strong className="text-[#ece3cf]">{lastResult.intac_manifoldu?.topoloji}</strong></span>
                      <span>Holonomi: <strong className="text-[#ece3cf]">{lastResult.holonomi_devridaim?.cins}</strong></span>
                    </div>
                  )}
                </div>
              )}

              {/* Küme Tasnif ve Tâdil Teftişi (Python Doğrudan İcra) */}
              {(lastResult.kume_tasnifi || lastResult.kume_tasnif_ve_tadil) && (
                <div className="p-3 rounded-lg bg-[#14181f] border border-amber-800/40 text-xs font-mono-code space-y-2">
                  <div className="flex items-center justify-between text-amber-300 font-bold">
                    <span>Küme Tasnif &amp; Serbestlik Derecesi Teftişi:</span>
                    <span className="text-[10px] text-[#a89a78]">3 Kat'î Şart &middot; 3 Kademeli Tâdil</span>
                  </div>
                  {lastResult.kume_tasnifi && (
                    <div className="space-y-1 text-[11px] text-amber-100/90">
                      <div className="flex items-center justify-between text-[10px]">
                        <span>Küme: <strong>{lastResult.kume_tasnifi.kume_adi}</strong> ({lastResult.kume_tasnifi.ontoloji_turu})</span>
                        <span className={lastResult.kume_tasnifi.uc_kati_sart?.tam_ve_ortucu_mu ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>
                          {lastResult.kume_tasnifi.uc_kati_sart?.tam_ve_ortucu_mu ? 'Tam Tasnifat (Örtücü)' : 'Muvakkat İkmal / Tâdil Gerekli'}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {lastResult.kume_tasnifi.serbestlik_dereceleri?.map((sd: any, idx: number) => (
                          <span key={idx} className="px-2 py-0.5 rounded bg-[#1e2530] border border-amber-900/50 text-amber-200 text-[10px]">
                            {sd.ad} ({sd.tur}) &middot; [{sd.degerler?.slice(0, 3).join(', ')}]
                          </span>
                        ))}
                      </div>
                      {lastResult.kume_tasnifi.tadil && (
                        <div className="p-2 rounded bg-amber-950/40 border border-amber-800/60 text-[10px] text-amber-200 mt-1">
                          <strong>Tâdil İcrası ({lastResult.kume_tasnifi.tadil.kademe}):</strong> {lastResult.kume_tasnifi.tadil.amel}
                          <span className="block text-emerald-400">Muhafaza Kaidesi (İctisâb-ı Sabık): {lastResult.kume_tasnifi.tadil.muhafaza_kaidesi_saglandi_mi ? 'Muhafaza Edildi' : 'İhlal'}</span>
                        </div>
                      )}
                    </div>
                  )}
                  {lastResult.kume_tasnif_ve_tadil && (
                    <div className="text-[11px] text-amber-200/90 space-y-1 pt-1">
                      <div className="text-[10px] text-[#a89a78]">Tâlim Safhası Tâdil Durumu:</div>
                      <p className="text-[10px]">{lastResult.kume_tasnif_ve_tadil.tadil_icrasi?.amel}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Training Summary */}
              {lastResult.bir_milyon_qudit_zirhi && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono-code text-[#a89a78]">
                  <div className="p-2 rounded bg-[#16130e] border border-[#362f22]">
                    <span className="text-[10px] block text-[#6f6449]">Aktif Qudit</span>
                    <span className="text-[#ece3cf] font-bold">{lastResult.bir_milyon_qudit_zirhi.aktif_qudit}</span>
                  </div>
                  <div className="p-2 rounded bg-[#16130e] border border-[#362f22]">
                    <span className="text-[10px] block text-[#6f6449]">Seyirci Dekuplaj</span>
                    <span className="text-emerald-400 font-bold">{lastResult.bir_milyon_qudit_zirhi.seyirci_qudit?.toLocaleString()}</span>
                  </div>
                  <div className="p-2 rounded bg-[#16130e] border border-[#362f22]">
                    <span className="text-[10px] block text-[#6f6449]">Fubini-Study (d_FS)</span>
                    <span className="text-[#e08856] font-bold">{lastResult.bir_milyon_qudit_zirhi.fubini_study_mesafe} rad</span>
                  </div>
                  <div className="p-2 rounded bg-[#16130e] border border-[#362f22]">
                    <span className="text-[10px] block text-[#6f6449]">Devre Sadakati</span>
                    <span className="text-emerald-400 font-bold">{lastResult.bir_milyon_qudit_zirhi.kapi_51_tetabuk?.sadakat}</span>
                  </div>
                </div>
              )}

              {/* Release Training Results */}
              {lastResult.kulliyat_ve_release_egitimi && lastResult.kulliyat_ve_release_egitimi.length > 0 && (
                <div className="p-3 rounded-lg bg-[#16130e] border border-cyan-800/40 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-cyan-300">
                    <span className="flex items-center gap-1.5">
                      <Database className="w-3.5 h-3.5" />
                      Külliyat &amp; GitHub Release Tâlim Neticeleri ({lastResult.kulliyat_ve_release_egitimi.length} Veriseti)
                    </span>
                    <span className="text-[10px] text-[#a89a78]">Ferman 1-O Boru Hattı</span>
                  </div>
                  <div className="space-y-1.5 max-h-44 overflow-y-auto text-[11px] font-mono-code">
                    {lastResult.kulliyat_ve_release_egitimi.map((kr: any, i: number) => (
                      <div key={i} className="p-1.5 rounded bg-[#221c14] border border-[#362f22] flex items-center justify-between gap-2">
                        <div>
                          <span className="text-[#ece3cf] font-bold block">{kr.veriseti_ad}</span>
                          <span className="text-[10px] text-[#a89a78]">{kr.sahip_isim} &middot; {kr.ornek_sayisi?.toLocaleString()} kayıt</span>
                        </div>
                        <div className="text-right text-[10px]">
                          <span className="text-cyan-400 font-bold block">r_K={kr.r_K} &middot; Toda={kr.toda_en_iyi}</span>
                          <span className="text-emerald-400">Sadakat: {kr.mantiga_sadakat ? 'Tam' : 'Cerh'}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Test Reports List */}
              {lastResult.raporlar && (
                <div className="space-y-1 max-h-36 overflow-y-auto text-xs font-mono-code">
                  {lastResult.raporlar.map((r: any, idx: number) => (
                    <div key={idx} className="flex justify-between py-1 border-b border-[#362f22]/50 text-[11px]">
                      <span className="text-[#ece3cf]">{r.test}</span>
                      <span className="text-emerald-400 font-bold">{r.durum} &middot; {r.detay}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </div>

      </div>

      {/* FULL-WIDTH CARD: Külliyat ve GitHub Release Veriseti Envanteri */}
      <div className="p-5 rounded-2xl bg-[#1c1810] border border-[#362f22] shadow-xl space-y-4">
        
        {/* Envanter Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#362f22] pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-950/60 border border-cyan-700/50 flex items-center justify-center text-cyan-300">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold font-serif-fraunces text-[#ece3cf]">
                  Külliyat &amp; GitHub Release Veriseti Envanteri
                </h3>
                <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/40">
                  {verisetleri.length} Toplam Veriseti
                </span>
                <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800/40">
                  {releaseCount} GitHub Release
                </span>
              </div>
              <p className="text-xs text-[#a89a78]">
                Bütün verisetleri Ferman 1-O boru hattıyla (akışla) taranır; disk taşması engellenerek Qudit Zırhına aktarılır.
              </p>
            </div>
          </div>

          {/* Header Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowAddModal(true)}
              className="px-3 py-1.5 rounded-lg bg-cyan-700 hover:bg-cyan-600 text-[#16130e] font-semibold text-xs transition-all flex items-center gap-1.5 shadow"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Yeni GitHub Release Ekle</span>
            </button>
            <button
              type="button"
              onClick={selectAllReleases}
              className="px-3 py-1.5 rounded-lg bg-[#241d13] hover:bg-[#33291b] border border-[#362f22] text-cyan-300 text-xs transition-all font-mono-code"
            >
              Tüm Release'leri Seç ({releaseCount})
            </button>
            <button
              type="button"
              onClick={selectAllDatasets}
              className="px-3 py-1.5 rounded-lg bg-[#241d13] hover:bg-[#33291b] border border-[#362f22] text-[#ece3cf] text-xs transition-all font-mono-code"
            >
              Hepsini Seç
            </button>
            {selectedDatasets.length > 0 && (
              <button
                type="button"
                onClick={clearSelectedDatasets}
                className="px-2.5 py-1.5 rounded-lg bg-rose-950/60 hover:bg-rose-900 border border-rose-800/50 text-rose-300 text-xs transition-all font-mono-code"
              >
                Temizle ({selectedDatasets.length})
              </button>
            )}
          </div>
        </div>

        {/* Filter and Search Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <div className="flex items-center gap-1.5 overflow-x-auto text-xs font-mono-code pb-1 max-w-full">
            {[
              { id: 'all', label: `Tümü (${verisetleri.length})` },
              { id: 'lugat', label: `Şümullü Lügatler & Sözlükler (${verisetleri.filter(v => v.kategori === 'lugat').length})` },
              { id: 'kadim_turkce', label: `1900 Öncesi Kadîm Türkçe (${verisetleri.filter(v => v.kategori === 'kadim_turkce').length})` },
              { id: 'yek_kitap', label: `Yek Kitap İlmî Eserler (${verisetleri.filter(v => v.kategori === 'yek_kitap').length})` },
              { id: 'release_koprusu', label: `GitHub Release Köprüleri (${releaseCount})` },
              { id: 'arc', label: `ARC Ailesi (${verisetleri.filter(v => v.kategori === 'arc').length})` },
              { id: 'riyaziye', label: `Riyaziye & Muhakeme (${verisetleri.filter(v => v.kategori === 'riyaziye').length})` },
              { id: 'kelam', label: `İslâmî & Kelâmî (${verisetleri.filter(v => v.kategori === 'kelam').length})` },
              { id: 'ozel_release', label: 'Özel Eklenenler' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setDatasetFilter(tab.id as any)}
                className={`px-3 py-1 rounded-lg transition-all whitespace-nowrap cursor-pointer ${
                  datasetFilter === tab.id
                    ? 'bg-[#e08856] text-[#16130e] font-bold shadow'
                    : 'bg-[#16130e] text-[#a89a78] hover:text-[#ece3cf] border border-[#362f22]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="relative min-w-[240px]">
            <Search className="w-3.5 h-3.5 text-[#6f6449] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Veriseti adı, depo, varlık veya sürüm ara..."
              value={datasetSearch}
              onChange={(e) => setDatasetSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-[#16130e] border border-[#362f22] text-[#ece3cf] text-xs focus:border-[#e08856] focus:outline-none placeholder-[#6f6449]"
            />
          </div>
        </div>

        {/* Datasets Table */}
        <div className="border border-[#362f22] rounded-xl overflow-hidden bg-[#14110c]">
          <div className="max-h-[380px] overflow-y-auto">
            <table className="w-full text-left text-xs font-mono-code border-collapse">
              <thead className="bg-[#1b1710] text-[#a89a78] sticky top-0 border-b border-[#362f22] select-none text-[11px]">
                <tr>
                  <th className="py-2.5 px-3 w-10 text-center">Seç</th>
                  <th className="py-2.5 px-3">Veriseti Adı &amp; Depo</th>
                  <th className="py-2.5 px-3">Tür / Kategori</th>
                  <th className="py-2.5 px-3">Sürüm &amp; Varlık</th>
                  <th className="py-2.5 px-3 text-right">Boyut</th>
                  <th className="py-2.5 px-3 text-right">Örnek Sayısı</th>
                  <th className="py-2.5 px-3 text-center">Söz Hakkı (Pay)</th>
                  <th className="py-2.5 px-3 text-right">İşlem</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#221c14] text-[#d4c8b0]">
                {loadingDatasets ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-[#a89a78]">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-[#e08856]" />
                      Veriseti kataloğu taranıyor...
                    </td>
                  </tr>
                ) : filteredDatasets.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-[#6f6449]">
                      Arama kriterine uygun veriseti bulunamadı.
                    </td>
                  </tr>
                ) : (
                  filteredDatasets.map((ds, idx) => {
                    const isSelected = selectedDatasets.includes(ds.ad);
                    const isRelease = ds.kategori === 'release_koprusu' || ds.kategori === 'ozel_release';
                    return (
                      <tr
                        key={idx}
                        className={`hover:bg-[#1a150e] transition-colors ${
                          isSelected ? 'bg-cyan-950/20' : ''
                        }`}
                      >
                        <td className="py-2 px-3 text-center">
                          <button
                            type="button"
                            onClick={() => toggleSelectDataset(ds.ad)}
                            className="text-[#a89a78] hover:text-[#ece3cf]"
                          >
                            {isSelected ? (
                              <CheckSquare className="w-4 h-4 text-cyan-400" />
                            ) : (
                              <SquareBox className="w-4 h-4 text-[#6f6449]" />
                            )}
                          </button>
                        </td>

                        <td className="py-2 px-3">
                          <div className="font-sans font-semibold text-[#ece3cf] flex items-center gap-1.5">
                            <span>{ds.ad}</span>
                            {ds.ozel_mi && (
                              <span className="text-[9px] px-1 py-0.2 rounded bg-amber-950 text-amber-300 border border-amber-700/40">
                                Özel
                              </span>
                            )}
                          </div>
                          <span className="text-[10px] text-[#8c7e63] block font-mono-code">
                            {ds.sahip_isim}
                          </span>
                        </td>

                        <td className="py-2 px-3">
                          {ds.kategori === 'lugat' ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-violet-950/80 text-violet-300 border border-violet-800/50">
                              Lügat / Sözlük
                            </span>
                          ) : ds.kategori === 'kadim_turkce' ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-950/80 text-teal-300 border border-teal-800/50">
                              Kadîm Türkçe (&lt;1900)
                            </span>
                          ) : ds.kategori === 'yek_kitap' ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950/80 text-amber-300 border border-amber-800/50">
                              Yek Kitap İlmî Eser
                            </span>
                          ) : isRelease ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/50">
                              GitHub Release
                            </span>
                          ) : ds.kategori === 'arc' ? (
                            <span className="px-2 py-0.5 rounded text-[10px] bg-amber-950/60 text-amber-300 border border-amber-800/40">
                              ARC Ailesi
                            </span>
                          ) : ds.kategori === 'riyaziye' ? (
                            <span className="px-2 py-0.5 rounded text-[10px] bg-sky-950/60 text-sky-300 border border-sky-800/40">
                              Riyaziye / Muhakeme
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950/60 text-emerald-300 border border-emerald-800/40">
                              İslâmî / Kelâmî
                            </span>
                          )}
                        </td>

                        <td className="py-2 px-3">
                          {ds.varlik ? (
                            <div>
                              <span className="text-[11px] text-[#ece3cf] font-bold block">{ds.varlik}</span>
                              <span className="text-[9px] text-[#8c7e63]">{ds.surum || 'release'}</span>
                            </div>
                          ) : (
                            <span className="text-[#6f6449] text-[10px]">- Külliyat Gövdesi -</span>
                          )}
                        </td>

                        <td className="py-2 px-3 text-right">
                          <span className="text-[#ece3cf]">
                            {ds.boyut_bayt ? (ds.boyut_bayt > 1e9 ? `${(ds.boyut_bayt / 1e9).toFixed(2)} GB` : `${(ds.boyut_bayt / 1e6).toFixed(1)} MB`) : '-'}
                          </span>
                        </td>

                        <td className="py-2 px-3 text-right">
                          <span className="text-[#a89a78]">
                            {ds.ornek_sayisi ? ds.ornek_sayisi.toLocaleString() : '-'}
                          </span>
                        </td>

                        <td className="py-2 px-3 text-center">
                          <span className="px-1.5 py-0.5 rounded bg-[#241d13] text-[#e08856] font-bold border border-[#362f22]">
                            {ds.pay.toFixed(1)}
                          </span>
                        </td>

                        <td className="py-2 px-3 text-right">
                          <button
                            type="button"
                            onClick={() => calistir('egit', [ds.ad])}
                            disabled={activeProcess !== 'idle'}
                            className="px-2.5 py-1 rounded bg-[#272117] hover:bg-[#3d3221] border border-[#362f22] text-[#e08856] text-[10px] font-semibold transition-all disabled:opacity-50"
                            title="Yalnız bu verisetiyle tekil eğitim akışı başlat"
                          >
                            Tekil Eğit
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer Statistics */}
        <div className="flex flex-wrap items-center justify-between text-xs font-mono-code text-[#a89a78] pt-1">
          <div className="flex items-center gap-4">
            <span>Toplam Hacim: <strong className="text-[#ece3cf]">{(totalByteSize / 1e9).toFixed(2)} GB</strong></span>
            <span>Kayıt Havuzu: <strong className="text-[#ece3cf]">{totalExamples.toLocaleString()} Örnek</strong></span>
            <span>Boru Hattı Prensibi: <strong className="text-cyan-400">Ferman 1-O (Pencere Akışı)</strong></span>
          </div>
          {selectedDatasets.length > 0 && (
            <button
              onClick={() => calistir('egit', selectedDatasets)}
              disabled={activeProcess !== 'idle'}
              className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-[#16130e] font-bold text-xs shadow flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Seçili {selectedDatasets.length} Verisetini Eğit</span>
            </button>
          )}
        </div>

      </div>

      {/* MODAL: Yeni GitHub Release Veriseti Ekleme */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-[#1c1810] border border-[#e08856]/50 rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-[#362f22] pb-3">
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm font-bold font-serif-fraunces text-[#ece3cf]">
                  Yeni GitHub Release Veriseti Ekle
                </h3>
              </div>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-[#a89a78] hover:text-[#ece3cf] text-sm"
              >
                ✕
              </button>
            </div>

            {eklemeHatasi && (
              <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800/60 text-xs text-rose-300">
                {eklemeHatasi}
              </div>
            )}

            <form onSubmit={yeniReleaseEkle} className="space-y-3 text-xs font-mono-code">
              <div>
                <label className="text-[11px] text-[#a89a78] block mb-1">Veriseti Adı (Açıklayıcı Başlık):</label>
                <input
                  type="text"
                  placeholder="Örn: Risale Kelâmı Release v1 veya UltraData-Math"
                  value={yeniAd}
                  onChange={(e) => setYeniAd(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-[#14110c] border border-[#362f22] text-[#ece3cf] focus:border-cyan-500 focus:outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[11px] text-[#a89a78] block mb-1">GitHub Depo (Kullanıcı/Depo):</label>
                  <input
                    type="text"
                    placeholder="Örn: yabadabadu1234/Mucit-ai"
                    value={yeniSahip}
                    onChange={(e) => setYeniSahip(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#14110c] border border-[#362f22] text-[#ece3cf] focus:border-cyan-500 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="text-[11px] text-[#a89a78] block mb-1">Release Tag / Sürüm:</label>
                  <input
                    type="text"
                    placeholder="Örn: kulliyat-1 veya v1.0.0"
                    value={yeniSurum}
                    onChange={(e) => setYeniSurum(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#14110c] border border-[#362f22] text-[#ece3cf] focus:border-cyan-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[11px] text-[#a89a78] block mb-1">Varlık / Dosya Adı:</label>
                  <input
                    type="text"
                    placeholder="Örn: kulliyat.mucit veya data.json"
                    value={yeniVarlik}
                    onChange={(e) => setYeniVarlik(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#14110c] border border-[#362f22] text-[#ece3cf] focus:border-cyan-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="text-[11px] text-[#a89a78] block mb-1">Söz Hakkı (Pay Ağırlığı):</label>
                  <input
                    type="number"
                    step="0.5"
                    min="0.5"
                    max="10"
                    value={yeniPay}
                    onChange={(e) => setYeniPay(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-[#14110c] border border-[#362f22] text-[#ece3cf] focus:border-cyan-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="text-[11px] text-[#a89a78] block mb-1">Doğrudan İndirme Linki (Opsiyonel):</label>
                <input
                  type="text"
                  placeholder="https://github.com/.../releases/download/... veya özel URL"
                  value={yeniDogrudanUrl}
                  onChange={(e) => setYeniDogrudanUrl(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-[#14110c] border border-[#362f22] text-[#ece3cf] focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#362f22]">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg bg-[#221c14] hover:bg-[#33291b] border border-[#362f22] text-[#a89a78] text-xs transition-all"
                >
                  Vazgeç
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-[#16130e] font-bold text-xs transition-all shadow"
                >
                  Release Verisetini Kaydet &amp; Kataloğa Ekle
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
