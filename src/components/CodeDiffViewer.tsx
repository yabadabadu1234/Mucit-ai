import React, { useState } from 'react';
import { StagedProposal, computeLineDiff } from '../utils/codeStaging';
import { codeBackupRepo, injectPrePostGuards, stripPrePostGuards } from '../utils/codeGuardBackup';
import { 
  CheckCircle2, 
  XCircle, 
  Edit3, 
  ShieldCheck, 
  Save, 
  GitCompare, 
  FileCode, 
  ArrowRight, 
  Sparkles, 
  History,
  Lock,
  Layers,
  Terminal,
  AlertTriangle,
  RotateCcw
} from 'lucide-react';

interface CodeDiffViewerProps {
  proposal: StagedProposal;
  onApprove: (proposalId: string, finalCode: string) => void;
  onReject: (proposalId: string) => void;
  onUserUpdateCode: (proposalId: string, newCode: string) => void;
}

export const CodeDiffViewer: React.FC<CodeDiffViewerProps> = ({
  proposal,
  onApprove,
  onReject,
  onUserUpdateCode,
}) => {
  const [isEditingMode, setIsEditingMode] = useState<boolean>(false);
  const [userText, setUserText] = useState<string>(proposal.userEditedCode);
  const [viewMode, setViewMode] = useState<'diff' | 'guarded' | 'backup'>('diff');
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  // Compute diff between original and currently edited proposed code
  const { lines: diffLines, additionsCount, deletionsCount } = computeLineDiff(
    proposal.originalCode,
    userText
  );

  // Pre/Post Guard Injected version
  const { guardedCode, header, footer } = injectPrePostGuards(
    userText,
    proposal.fileLanguage
  );

  // Fetch backups for this file
  const backups = codeBackupRepo.getBackupsForFile(proposal.fileId);

  const handleSaveUserDirectEdit = () => {
    onUserUpdateCode(proposal.id, userText);
    setIsEditingMode(false);
    setFeedbackMessage('Müfettiş Müdahalesi Kaydedildi! (İrade-i Seniyye hazırdır)');
    setTimeout(() => setFeedbackMessage(null), 3000);
  };

  const handleApproveSeal = () => {
    // 1. Create backup snapshot in repo
    codeBackupRepo.createBackup(
      proposal.fileId,
      proposal.filePath,
      userText,
      proposal.fileLanguage,
      `İrade-i Seniyye Onayı: ${proposal.title}`
    );

    // 2. Call parent callback to merge into main codebase
    onApprove(proposal.id, userText);
  };

  return (
    <div className="flex-1 flex flex-col bg-[#0B0C0E] border border-slate-800 rounded-xl overflow-hidden font-mono shadow-2xl">
      {/* Diff View Header */}
      <div className="p-4 bg-[#14161A] border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
              <GitCompare className="w-3 h-3 text-emerald-400" /> Mukayese Meydanı (Diff Inspector)
            </span>
            <span className="text-xs text-slate-400 font-mono">ID: {proposal.id}</span>
            <span className="text-xs text-amber-400 font-mono px-2 py-0.5 rounded bg-amber-950/40 border border-amber-500/20">
              Teklif Eden: {proposal.proposedBy}
            </span>
          </div>

          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <FileCode className="w-5 h-5 text-cyan-400" />
            {proposal.title}
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">{proposal.description}</p>
        </div>

        {/* View Switcher & Action Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Mode Switchers */}
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-1 flex items-center gap-1 text-xs">
            <button
              onClick={() => setViewMode('diff')}
              className={`px-2.5 py-1 rounded font-mono transition flex items-center gap-1 ${
                viewMode === 'diff' 
                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <GitCompare className="w-3.5 h-3.5" /> Diff Mukayese
            </button>

            <button
              onClick={() => setViewMode('guarded')}
              className={`px-2.5 py-1 rounded font-mono transition flex items-center gap-1 ${
                viewMode === 'guarded' 
                  ? 'bg-purple-950 text-purple-300 border border-purple-500/40' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" /> Kuşatılmış Kod (Pre/Post)
            </button>

            <button
              onClick={() => setViewMode('backup')}
              className={`px-2.5 py-1 rounded font-mono transition flex items-center gap-1 ${
                viewMode === 'backup' 
                  ? 'bg-indigo-950 text-indigo-300 border border-indigo-500/40' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <History className="w-3.5 h-3.5" /> Yedek Havuzu ({backups.length})
            </button>
          </div>

          {/* User Edit Mode Toggle */}
          <button
            onClick={() => setIsEditingMode(!isEditingMode)}
            className={`px-3 py-1.5 text-xs rounded-lg font-mono border transition flex items-center gap-1.5 ${
              isEditingMode
                ? 'bg-amber-950/80 text-amber-300 border-amber-500/60 ring-1 ring-amber-500/30'
                : 'bg-slate-900 border-slate-700 text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Edit3 className="w-3.5 h-3.5 text-amber-400" />
            {isEditingMode ? 'Düzenlemeyi Kapat' : 'Müfettiş Müdahalesi (Manuel Edit)'}
          </button>
        </div>
      </div>

      {/* Feedback Alert Banner */}
      {feedbackMessage && (
        <div className="p-2.5 bg-amber-950/60 border-b border-amber-500/40 text-amber-200 text-xs font-mono flex items-center gap-2 px-4 animate-fadeIn">
          <Sparkles className="w-4 h-4 text-amber-400" />
          <span>{feedbackMessage}</span>
        </div>
      )}

      {/* Main Diff Content Container */}
      <div className="flex-1 flex flex-col overflow-hidden bg-[#07080A]">
        {/* Status Bar showing stats */}
        <div className="p-2 bg-[#0E1013] border-b border-slate-800 flex items-center justify-between text-xs font-mono px-4 text-slate-400">
          <div className="flex items-center gap-4">
            <span className="text-slate-300">Dosya: <strong className="text-cyan-400">{proposal.filePath}</strong></span>
            <span className="text-emerald-400">+{additionsCount} satır eklendi</span>
            <span className="text-rose-400">-{deletionsCount} satır çıkarıldı</span>
          </div>

          <div className="flex items-center gap-2 text-[11px]">
            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
              {proposal.fileLanguage.toUpperCase()} Lisanı
            </span>
          </div>
        </div>

        {/* View Mode 1: Diff Comparison & Edit Area */}
        {viewMode === 'diff' && (
          <div className="flex-1 flex flex-col md:flex-row overflow-hidden divide-y md:divide-y-0 md:divide-x divide-slate-800/80">
            {/* Left Side: Kadim / Original Code */}
            <div className="flex-1 flex flex-col overflow-hidden bg-[#0A0B0E]">
              <div className="p-2 bg-[#121418] border-b border-slate-800 text-[11px] text-slate-400 uppercase font-mono px-3 flex items-center justify-between">
                <span>Kadim Kod (Eski Hal)</span>
                <span className="text-slate-500">Salt Okunur</span>
              </div>
              <div className="flex-1 p-3 overflow-auto">
                <pre className="text-xs font-mono text-slate-400 leading-relaxed whitespace-pre-wrap">
                  <code>{proposal.originalCode}</code>
                </pre>
              </div>
            </div>

            {/* Right Side: Proposal or User Direct Editor */}
            <div className="flex-1 flex flex-col overflow-hidden bg-[#08090C]">
              <div className="p-2 bg-[#121418] border-b border-slate-800 text-[11px] text-slate-300 uppercase font-mono px-3 flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-emerald-400 font-bold">
                  {isEditingMode ? 'Müfettiş Manuel Düzenleme Alanı' : 'Teklif Edilen Yeni Kod'}
                </span>
                {isEditingMode && (
                  <button
                    onClick={handleSaveUserDirectEdit}
                    className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] hover:bg-amber-500/30 font-bold flex items-center gap-1"
                  >
                    <Save className="w-3 h-3 text-amber-400" /> Kaydet
                  </button>
                )}
              </div>

              <div className="flex-1 overflow-auto">
                {isEditingMode ? (
                  <textarea
                    value={userText}
                    onChange={(e) => setUserText(e.target.value)}
                    className="w-full h-full p-3 bg-[#050608] text-emerald-300 font-mono text-xs focus:outline-none resize-none leading-relaxed selection:bg-emerald-900"
                    placeholder="Müfettiş olarak kodu doğrudan burada değiştirebilirsiniz..."
                  />
                ) : (
                  <div className="divide-y divide-slate-900/60 text-xs font-mono">
                    {diffLines.map((line, idx) => {
                      if (line.type === 'added') {
                        return (
                          <div key={idx} className="flex bg-emerald-950/40 text-emerald-300 border-l-2 border-emerald-500 px-3 py-0.5">
                            <span className="w-8 shrink-0 text-emerald-600 select-none">{line.newLineNumber}</span>
                            <span className="w-4 shrink-0 font-bold text-emerald-400 select-none">+</span>
                            <span className="whitespace-pre-wrap">{line.content}</span>
                          </div>
                        );
                      }
                      if (line.type === 'removed') {
                        return (
                          <div key={idx} className="flex bg-rose-950/40 text-rose-300 border-l-2 border-rose-500 px-3 py-0.5 line-through opacity-80">
                            <span className="w-8 shrink-0 text-rose-600 select-none">{line.oldLineNumber}</span>
                            <span className="w-4 shrink-0 font-bold text-rose-400 select-none">-</span>
                            <span className="whitespace-pre-wrap">{line.content}</span>
                          </div>
                        );
                      }
                      return (
                        <div key={idx} className="flex text-slate-400 px-3 py-0.5 hover:bg-slate-900/40">
                          <span className="w-8 shrink-0 text-slate-600 select-none">{line.newLineNumber}</span>
                          <span className="w-4 shrink-0 text-slate-700 select-none"> </span>
                          <span className="whitespace-pre-wrap">{line.content}</span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* View Mode 2: Guarded Code with Pre/Post Injection */}
        {viewMode === 'guarded' && (
          <div className="flex-1 p-4 overflow-auto bg-[#050608] space-y-3">
            <div className="p-3 bg-purple-950/30 border border-purple-500/30 rounded-lg text-xs font-mono text-purple-200 flex items-start gap-2">
              <ShieldCheck className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
              <div>
                <strong className="block text-purple-300 uppercase">Pre/Post Injection Muhafaza Kalkanı</strong>
                Bu görünüm, kodun hem üstüne hem de altına otomatik eklenen âtıl (çalışmayan) pasif yorum bloklarını gösterir. 
                Python için <code>""" ... """</code>, C++ için <code>/* ... */</code> blokları ile kuşatılmıştır.
              </div>
            </div>

            {/* Header Block */}
            <div className="p-3 bg-slate-950 border border-amber-500/40 rounded-lg text-amber-300/90 text-xs">
              <span className="text-[10px] text-amber-500 uppercase font-bold block mb-1">Pre-Injection Header Block:</span>
              <pre><code>{header}</code></pre>
            </div>

            {/* Body Code */}
            <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-lg text-emerald-300 text-xs">
              <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">Executable Core Code:</span>
              <pre><code>{userText}</code></pre>
            </div>

            {/* Footer Block */}
            <div className="p-3 bg-slate-950 border border-amber-500/40 rounded-lg text-amber-300/90 text-xs">
              <span className="text-[10px] text-amber-500 uppercase font-bold block mb-1">Post-Injection Footer Block:</span>
              <pre><code>{footer}</code></pre>
            </div>
          </div>
        )}

        {/* View Mode 3: Backup Vault Repository */}
        {viewMode === 'backup' && (
          <div className="flex-1 p-4 overflow-auto bg-[#050608] space-y-3">
            <div className="p-3 bg-indigo-950/30 border border-indigo-500/30 rounded-lg text-xs font-mono text-indigo-200 flex items-start gap-2">
              <History className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
              <div>
                <strong className="block text-indigo-300 uppercase">Kadim Yedekleme Arşivi (Backup Vault)</strong>
                Onaylanan her kod mühürlenmeden önce otomatik olarak zayiatı önlemek adına yedek deposuna kaydedilir.
              </div>
            </div>

            {backups.length > 0 ? (
              <div className="space-y-3">
                {backups.map((b) => (
                  <div key={b.id} className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-lg space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-indigo-300 flex items-center gap-1.5">
                        <Terminal className="w-3.5 h-3.5 text-indigo-400" />
                        {b.id} ({b.timestamp})
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {b.note}
                      </span>
                    </div>
                    <pre className="p-2 bg-black/60 border border-slate-800 rounded text-[11px] text-slate-300 overflow-x-auto max-h-40">
                      <code>{b.guardedCode}</code>
                    </pre>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-slate-500 bg-slate-900/30 rounded-lg border border-slate-800/60">
                Henüz bu dosya için mühürlenmiş bir yedek kaydı bulunmuyor. Onay verildiğinde otomatik yedek oluşturulacaktır.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Approval & Action Seal Bar ("İrade-i Seniyye ve Hür Mühür") */}
      <div className="p-4 bg-[#14161A] border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <Lock className="w-4 h-4 text-emerald-400" />
          <span>Nihai Onay Mühürü: Kullanıcı onayı olmadan kodlar ana uygulamaya geçmez.</span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onReject(proposal.id)}
            className="px-4 py-2 rounded-lg bg-rose-950/60 border border-rose-500/40 text-rose-300 hover:bg-rose-900/80 text-xs font-mono font-bold flex items-center gap-1.5 transition"
          >
            <XCircle className="w-4 h-4 text-rose-400" />
            Teklifi Hükümsüz Kıl (Reddet)
          </button>

          <button
            onClick={handleApproveSeal}
            className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs font-mono flex items-center gap-2 shadow-lg shadow-emerald-950/60 transition transform active:scale-95"
          >
            <CheckCircle2 className="w-4 h-4 text-white" />
            İrade-i Seniyye: Mührü Vur ve Kabul Et
          </button>
        </div>
      </div>
    </div>
  );
};
