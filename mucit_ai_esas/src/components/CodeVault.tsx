import React, { useState } from 'react';
import { FULL_CODE_VAULT_FILES, CodeFile } from '../data/fullCodeVaultFiles';
import { StagedProposal, INITIAL_PROPOSALS } from '../utils/codeStaging';
import { codeBackupRepo, injectPrePostGuards } from '../utils/codeGuardBackup';
import { CodeDiffViewer } from './CodeDiffViewer';
import { ExecutionSandbox } from './ExecutionSandbox';
import { 
  Copy, 
  Check, 
  Download, 
  Terminal, 
  Code2, 
  FileCode, 
  Folder, 
  Layers, 
  Search, 
  ShieldCheck,
  Zap,
  ArrowRight,
  Cpu,
  GitCompare,
  History,
  Edit3,
  PlusCircle,
  CheckCircle2,
  Lock,
  Save,
  Sparkles,
  Play
} from 'lucide-react';

export const CodeVault: React.FC = () => {
  // Navigation & Subview Tabs
  const [activeSubTab, setActiveSubTab] = useState<'files' | 'sandbox' | 'diff' | 'backup'>('files');
  
  // File State
  const [codeFiles, setCodeFiles] = useState<CodeFile[]>(FULL_CODE_VAULT_FILES);
  const [selectedFileId, setSelectedFileId] = useState<string>('MOD1_PY');
  const [copied, setCopied] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showGuards, setShowGuards] = useState<boolean>(true);
  const [isDirectEditing, setIsDirectEditing] = useState<boolean>(false);
  const [directCodeText, setDirectCodeText] = useState<string>('');

  // Staging & Proposals State
  const [proposals, setProposals] = useState<StagedProposal[]>(INITIAL_PROPOSALS);
  const [selectedProposalId, setSelectedProposalId] = useState<string>('PROP_001');

  // Notification Toast
  const [notification, setNotification] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 3500);
  };

  const currentFile: CodeFile = codeFiles.find(f => f.id === selectedFileId) || codeFiles[0];
  const currentProposal: StagedProposal | undefined = proposals.find(p => p.id === selectedProposalId);

  const filteredFiles = codeFiles.filter(f => 
    f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    f.path.toLowerCase().includes(searchQuery.toLowerCase()) ||
    f.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Compute displayed code with/without pre/post guard injection
  const displayedCode = showGuards
    ? injectPrePostGuards(currentFile.code, currentFile.language).guardedCode
    : currentFile.code;

  const handleCopyCode = () => {
    navigator.clipboard.writeText(displayedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadCode = () => {
    const blob = new Blob([displayedCode], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = currentFile.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Direct manual edit handler (Fourth Duty: Müfettiş Hakkı)
  const handleStartDirectEdit = () => {
    setDirectCodeText(currentFile.code);
    setIsDirectEditing(true);
  };

  const handleSaveDirectEdit = () => {
    // Save to backup first
    codeBackupRepo.createBackup(
      currentFile.id,
      currentFile.path,
      directCodeText,
      currentFile.language,
      'Müfettiş Doğrudan Manuel Düzenlemesi'
    );

    // Update active code
    setCodeFiles(prev => prev.map(f => f.id === currentFile.id ? { ...f, code: directCodeText } : f));
    setIsDirectEditing(false);
    showToast(`Müfettiş Müdahalesi Kaydedildi! (${currentFile.name} güncellendi)`);
  };

  // Create new staged proposal from current file
  const handleCreateNewProposal = () => {
    const newPropId = `PROP_${Date.now().toString().slice(-4)}`;
    const newProp: StagedProposal = {
      id: newPropId,
      fileId: currentFile.id,
      filePath: currentFile.path,
      fileLanguage: currentFile.language,
      title: `${currentFile.name} Üzerinde Yeni Kod Optimizasyon Teklifi`,
      description: `Otomatik performans ve nizamname kontrolü kapsamında teklif edilen kod güncellemesi.`,
      proposedBy: 'Küllî Mimarî Ajanı',
      createdAt: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
      status: 'pending',
      originalCode: currentFile.code,
      proposedCode: currentFile.code + (currentFile.language === 'python' ? '\n\n# [NİZAMNAME İYİLEŞTİRMESİ] Yeni performans kancası eklendi' : '\n\n// [NİZAMNAME İYİLEŞTİRMESİ] High-throughput DMA buffer optimization'),
      userEditedCode: currentFile.code + (currentFile.language === 'python' ? '\n\n# [NİZAMNAME İYİLEŞTİRMESİ] Yeni performans kancası eklendi' : '\n\n// [NİZAMNAME İYİLEŞTİRMESİ] High-throughput DMA buffer optimization')
    };

    setProposals(prev => [newProp, ...prev]);
    setSelectedProposalId(newPropId);
    setActiveSubTab('diff');
    showToast(`Yeni Kod İyileştirme Teklifi (${newPropId}) Mukayese Meydanına Gönderildi!`);
  };

  // Approve proposal (Third Duty: İrade-i Seniyye - DERHAL HUZURDAN ÇEKİLME TALİMATI)
  const handleApproveProposal = (proposalId: string, finalCode: string) => {
    const prop = proposals.find(p => p.id === proposalId);
    if (!prop) return;

    // 1. Update active code file in state
    setCodeFiles(prev => prev.map(f => f.id === prop.fileId ? { ...f, code: finalCode } : f));

    // 2. Mark proposal as approved
    const updatedProposals = proposals.map(p => p.id === proposalId ? { ...p, status: 'approved' as const } : p);
    setProposals(updatedProposals);

    // 3. Immediately dismiss approved proposal from view / advance to next pending proposal if available
    const nextPending = updatedProposals.find(p => p.status === 'pending' && p.id !== proposalId);
    if (nextPending) {
      setSelectedProposalId(nextPending.id);
    }

    showToast(`İrade-i Seniyye Mühürü Vuruldu! Teklif Kabul Edildi ve Huzurdan Çekildi (${prop.filePath}).`);
  };

  // Reject proposal
  const handleRejectProposal = (proposalId: string) => {
    const updatedProposals = proposals.map(p => p.id === proposalId ? { ...p, status: 'rejected' as const } : p);
    setProposals(updatedProposals);

    const nextPending = updatedProposals.find(p => p.status === 'pending' && p.id !== proposalId);
    if (nextPending) {
      setSelectedProposalId(nextPending.id);
    }

    showToast(`Teklif Hükümsüz Kılındı ve Huzurdan Çekildi.`);
  };

  // Update proposed user code dynamically
  const handleUserUpdateCode = (proposalId: string, newCode: string) => {
    setProposals(prev => prev.map(p => p.id === proposalId ? { ...p, userEditedCode: newCode } : p));
  };

  const pendingProposalsCount = proposals.filter(p => p.status === 'pending').length;

  return (
    <div className="flex-1 flex flex-col bg-[#0A0A0B] text-slate-200 overflow-hidden font-mono">
      {/* Top Banner */}
      <div className="p-4 bg-[#121316] border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 rounded flex items-center gap-1">
              <Terminal className="w-3 h-3 text-emerald-400" /> Tam Teşekküllü Nizamname Sürücü Deposu
            </span>
            <span className="text-xs text-slate-400">Müstakil .py/.cpp Dosyaları + Meydan-ı Tecrübe + Diff Inspector</span>
          </div>
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <Code2 className="w-5 h-5 text-emerald-400" />
            Küllî Sanal GPU Sürücü Kodları & Meydan-ı Tecrübe
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Pre/Post Kuşatma, Mukayese Meydanı (Diff View), Meydan-ı Tecrübe (Sandbox) ve İrade-i Seniyye Mühürü.
          </p>
        </div>

        {/* Global Tab Switchers */}
        <div className="flex items-center gap-2">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-1 flex items-center gap-1 text-xs">
            <button
              onClick={() => setActiveSubTab('files')}
              className={`px-3 py-1.5 rounded-lg font-mono font-semibold transition flex items-center gap-1.5 ${
                activeSubTab === 'files'
                  ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileCode className="w-4 h-4 text-emerald-400" />
              Sürücü Kodları
            </button>

            <button
              onClick={() => setActiveSubTab('sandbox')}
              className={`px-3 py-1.5 rounded-lg font-mono font-semibold transition flex items-center gap-1.5 ${
                activeSubTab === 'sandbox'
                  ? 'bg-amber-950/80 text-amber-300 border border-amber-500/40 shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Play className="w-4 h-4 text-amber-400 fill-amber-400/20" />
              Meydan-ı Tecrübe (Sandbox)
            </button>

            <button
              onClick={() => setActiveSubTab('diff')}
              className={`px-3 py-1.5 rounded-lg font-mono font-semibold transition flex items-center gap-1.5 relative ${
                activeSubTab === 'diff'
                  ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-500/40 shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <GitCompare className="w-4 h-4 text-cyan-400" />
              Mukayese Meydanı (Diff)
              {pendingProposalsCount > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-amber-500 text-black font-bold text-[10px]">
                  {pendingProposalsCount}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveSubTab('backup')}
              className={`px-3 py-1.5 rounded-lg font-mono font-semibold transition flex items-center gap-1.5 ${
                activeSubTab === 'backup'
                  ? 'bg-purple-950/80 text-purple-300 border border-purple-500/40 shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <History className="w-4 h-4 text-purple-400" />
              Yedek Arşivi
            </button>
          </div>
        </div>
      </div>

      {/* Notification Toast Banner */}
      {notification && (
        <div className="p-2.5 bg-emerald-950/90 border-b border-emerald-500/40 text-emerald-200 text-xs font-mono flex items-center justify-between px-6 animate-fadeIn">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>{notification}</span>
          </div>
          <span className="text-[10px] text-emerald-400 font-bold">NİZAMNAME İŞLEMİ TAMAMLANDI</span>
        </div>
      )}

      {/* SUB-VIEW 1: Active Code Files Explorer */}
      {activeSubTab === 'files' && (
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
          {/* File Browser Sidebar */}
          <div className="lg:col-span-4 bg-[#121316] border-r border-slate-800 p-4 flex flex-col overflow-y-auto">
            <div className="mb-3">
              <label className="text-[11px] font-mono text-slate-400 uppercase mb-1 block">
                Sürücü Dosyaları & Arama
              </label>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Dosya adı veya modül ara..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-emerald-500/50"
                />
              </div>
            </div>

            <div className="space-y-2 flex-1 overflow-y-auto pr-1">
              <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider px-1">
                kulli_gpu Subsystem Source Code
              </div>

              {filteredFiles.map((file) => {
                const isSelected = selectedFileId === file.id;
                const isCpp = file.language === 'cpp';

                return (
                  <button
                    key={file.id}
                    onClick={() => {
                      setSelectedFileId(file.id);
                      setIsDirectEditing(false);
                    }}
                    className={`w-full text-left p-3 rounded-xl border transition flex flex-col gap-1 text-xs ${
                      isSelected
                        ? 'bg-slate-900 border-emerald-500/80 text-emerald-300 ring-1 ring-emerald-500/30'
                        : 'bg-[#15161a] border-slate-800/80 text-slate-300 hover:border-slate-700 hover:bg-[#1b1c22]'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold font-mono flex items-center gap-2 truncate">
                        <FileCode className={`w-4 h-4 shrink-0 ${isCpp ? 'text-cyan-400' : 'text-emerald-400'}`} />
                        {file.name}
                      </span>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded uppercase font-bold border ${
                        isCpp 
                          ? 'bg-cyan-950/60 text-cyan-400 border-cyan-500/40' 
                          : 'bg-emerald-950/60 text-emerald-400 border-emerald-500/40'
                      }`}>
                        {file.language}
                      </span>
                    </div>

                    <div className="text-[10px] text-slate-400 font-mono truncate">
                      {file.path}
                    </div>

                    <div className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">
                      {file.description}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Code View / Direct Editor */}
          <div className="lg:col-span-8 bg-[#0A0A0B] flex flex-col overflow-hidden">
            {/* File Header Bar */}
            <div className="p-3 bg-[#121316]/90 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-4">
              <div className="flex items-center gap-3">
                <FileCode className={`w-4 h-4 ${currentFile.language === 'cpp' ? 'text-cyan-400' : 'text-emerald-400'}`} />
                <div>
                  <div className="text-xs font-bold text-white font-mono flex items-center gap-2">
                    {currentFile.path}
                    <span className="text-[10px] font-mono text-slate-400 font-normal">
                      ({currentFile.code.split('\n').length} Satır)
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {currentFile.description}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowGuards(!showGuards)}
                  className={`px-2.5 py-1 text-xs rounded border transition flex items-center gap-1 font-mono ${
                    showGuards 
                      ? 'bg-purple-950/80 text-purple-300 border-purple-500/40' 
                      : 'bg-slate-900 border-slate-700 text-slate-400'
                  }`}
                  title="En üst/en alt Pre/Post pasif yorum bloklarını göster/gizle"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
                  {showGuards ? 'Pre/Post Kuşatma Açık' : 'Ham Kod'}
                </button>

                <button
                  onClick={handleCreateNewProposal}
                  className="px-2.5 py-1 text-xs rounded border border-cyan-500/40 bg-cyan-950/60 text-cyan-300 hover:bg-cyan-900/60 transition flex items-center gap-1 font-mono"
                  title="Bu dosya için Staging Diff teklifi oluştur"
                >
                  <PlusCircle className="w-3.5 h-3.5 text-cyan-400" />
                  Teklif Oluştur (Diff)
                </button>

                {!isDirectEditing ? (
                  <button
                    onClick={handleStartDirectEdit}
                    className="px-2.5 py-1 text-xs rounded border border-amber-500/40 bg-amber-950/60 text-amber-300 hover:bg-amber-900/60 transition flex items-center gap-1 font-mono"
                    title="Müfettiş Hakkı: Doğrudan manuel kod düzenleme"
                  >
                    <Edit3 className="w-3.5 h-3.5 text-amber-400" />
                    Manuel Düzenle
                  </button>
                ) : (
                  <button
                    onClick={handleSaveDirectEdit}
                    className="px-3 py-1 text-xs rounded bg-amber-600 hover:bg-amber-500 text-black font-bold transition flex items-center gap-1 font-mono"
                  >
                    <Save className="w-3.5 h-3.5" />
                    Kaydet
                  </button>
                )}

                <button
                  onClick={handleCopyCode}
                  className="px-2.5 py-1 bg-slate-900 border border-slate-700 text-slate-200 hover:bg-slate-800 text-xs rounded font-mono flex items-center gap-1"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            {/* Display Area or Manual Editor */}
            <div className="flex-1 p-4 overflow-auto bg-[#050507]">
              {isDirectEditing ? (
                <div className="h-full flex flex-col space-y-2">
                  <div className="p-2 bg-amber-950/40 border border-amber-500/30 rounded text-amber-200 text-xs font-mono flex items-center gap-2">
                    <Edit3 className="w-4 h-4 text-amber-400 shrink-0" />
                    <span><strong>Müfettiş Hakkı Aktif:</strong> Kodu doğrudan değiştiriyorsunuz. Kaydet dediğinizde değişiklik anında geçerli sayılacaktır.</span>
                  </div>
                  <textarea
                    value={directCodeText}
                    onChange={(e) => setDirectCodeText(e.target.value)}
                    className="flex-1 w-full p-3 bg-black border border-slate-800 rounded text-emerald-400 font-mono text-xs focus:outline-none focus:border-amber-500/50 resize-none leading-relaxed"
                  />
                </div>
              ) : (
                <pre className="font-mono text-xs leading-relaxed text-emerald-400/90 selection:bg-emerald-900 selection:text-white">
                  <code>{displayedCode}</code>
                </pre>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SUB-VIEW 2: Meydan-ı Tecrübe (Execution Sandbox) */}
      {activeSubTab === 'sandbox' && (
        <ExecutionSandbox files={codeFiles} />
      )}

      {/* SUB-VIEW 3: Mukayese Meydanı (Diff Viewer & Approval Mechanism) */}
      {activeSubTab === 'diff' && (
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
          {/* Proposals Selector Sidebar */}
          <div className="lg:col-span-3 bg-[#121316] border-r border-slate-800 p-4 flex flex-col overflow-y-auto">
            <div className="text-xs font-mono text-slate-400 uppercase font-bold mb-3 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <GitCompare className="w-4 h-4 text-cyan-400" /> Staging Havuzu
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-400">
                {proposals.length} Teklif
              </span>
            </div>

            <div className="space-y-2 flex-1 overflow-y-auto pr-1">
              {proposals.map((p) => {
                const isSelected = selectedProposalId === p.id;
                const isPending = p.status === 'pending';
                const isApproved = p.status === 'approved';

                return (
                  <button
                    key={p.id}
                    onClick={() => setSelectedProposalId(p.id)}
                    className={`w-full text-left p-3 rounded-xl border transition flex flex-col gap-1.5 text-xs ${
                      isSelected
                        ? 'bg-slate-900 border-cyan-500/80 text-cyan-300 ring-1 ring-cyan-500/30'
                        : 'bg-[#15161a] border-slate-800/80 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold font-mono text-[11px] text-white truncate">
                        {p.id}
                      </span>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase border ${
                        isPending 
                          ? 'bg-amber-950 text-amber-400 border-amber-500/40' 
                          : isApproved 
                          ? 'bg-emerald-950 text-emerald-400 border-emerald-500/40' 
                          : 'bg-rose-950 text-rose-400 border-rose-500/40'
                      }`}>
                        {p.status}
                      </span>
                    </div>

                    <div className="font-semibold text-slate-200 line-clamp-1">
                      {p.title}
                    </div>

                    <div className="text-[10px] text-slate-400 font-mono truncate">
                      {p.filePath}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Diff Viewer Area */}
          <div className="lg:col-span-9 bg-[#0A0A0B] flex flex-col overflow-hidden p-4">
            {currentProposal ? (
              currentProposal.status === 'pending' ? (
                <CodeDiffViewer
                  proposal={currentProposal}
                  onApprove={handleApproveProposal}
                  onReject={handleRejectProposal}
                  onUserUpdateCode={handleUserUpdateCode}
                />
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-[#0B0C0E] border border-slate-800 rounded-xl space-y-3 font-mono">
                  <CheckCircle2 className="w-12 h-12 text-emerald-400" />
                  <h3 className="text-base font-bold text-white">İrade-i Seniyye Vuruldu ve Huzurdan Çekildi</h3>
                  <p className="text-xs text-slate-400 max-w-md">
                    Bu teklif (<code>{currentProposal.id}</code>) onaylanmış / işlenmiş olup ana kod tabanına entegre edilmiştir. Huzurda beklemeden derhal temizlenmiştir.
                  </p>
                  <button
                    onClick={() => setActiveSubTab('files')}
                    className="px-4 py-2 bg-slate-900 border border-slate-700 text-emerald-300 text-xs rounded-lg font-bold hover:bg-slate-800"
                  >
                    Sürücü Kodlarına Dön
                  </button>
                </div>
              )
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-500 font-mono text-xs">
                Bekleyen bir staging teklifi bulunmuyor. All proposals settled.
              </div>
            )}
          </div>
        </div>
      )}

      {/* SUB-VIEW 4: Backup Vault Repository */}
      {activeSubTab === 'backup' && (
        <div className="flex-1 p-6 overflow-y-auto bg-[#0A0A0B] space-y-4">
          <div className="p-4 bg-[#121316] border border-slate-800 rounded-xl flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
                <History className="w-4 h-4 text-purple-400" /> Kadim Muhafaza ve Yedek Deposudur
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Onaylanan veya müfettiş tarafından düzenlenen tüm kodlar pre/post injection mühürleri ile zayiat vermeden burada muhafaza edilir. Tekrarlı tıklamalarda mükerrer kayıt engellenir.
              </p>
            </div>
            <span className="text-xs font-mono text-purple-300 bg-purple-950/60 px-3 py-1 rounded border border-purple-500/30">
              Toplam Yedek: {codeBackupRepo.getAllBackups().length} Kayıt
            </span>
          </div>

          {codeBackupRepo.getAllBackups().length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {codeBackupRepo.getAllBackups().map((snap) => (
                <div key={snap.id} className="p-4 bg-[#121316] border border-slate-800 rounded-xl space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-purple-300">{snap.filePath}</span>
                    <span className="text-slate-400">{snap.timestamp}</span>
                  </div>

                  <div className="text-xs text-slate-300 font-mono bg-slate-900 p-2 rounded border border-slate-800/80">
                    Not: {snap.note}
                  </div>

                  <pre className="p-3 bg-[#050608] border border-slate-800 rounded text-[11px] text-emerald-400/90 font-mono overflow-x-auto max-h-48">
                    <code>{snap.guardedCode}</code>
                  </pre>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center text-xs text-slate-500 font-mono bg-[#121316] rounded-xl border border-slate-800">
              Henüz yedeklenme yapılmış kayıt bulunmuyor. Bir kodu kabul ettiğinizde veya kaydettiğinizde yedek otomatik olarak buraya işlenir.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
