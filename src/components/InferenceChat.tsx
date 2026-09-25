import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Trash2,
  Copy,
  Check,
  Shield,
  Sparkles,
  Bot,
  User,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  CheckCircle2,
  Atom,
  Scale,
  BookOpen
} from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'user' | 'model';
  metin: string;
  zaman: string;
  sonuc?: any;
  hata?: boolean;
}

export function InferenceChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'model',
      metin:
        'Selamlar! Ben Küllî İdrak Genel Dil Modeli. Bana dilediğiniz herhangi bir suali sorabilir, felsefi, ahlaki, mantıki, lügat veya ilmi meseleleri danışabilir, incelemek istediğiniz iddia ve kaziyeleri serbestçe yöneltebilirsiniz.\n\nFerman 1-G (Ya İspat Ya Sükût) ve fıtrat terazisi gereğince kaziyenizi 1,048,576 Qudit zırhında ve kadîm külliyat zemininde muhakeme edip intaç kelâmımı sunarım.',
      zaman: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedDetails, setExpandedDetails] = useState<Record<string, boolean>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Textarea auto-resize
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const toggleDetail = (id: string) => {
    setExpandedDetails((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleClear = () => {
    setMessages([
      {
        id: 'welcome-' + Date.now(),
        sender: 'model',
        metin:
          'Sohbet hafızası sıfırlandı. Yeni bir sual veya kaziye yöneltebilirsiniz. Küllî İdrak dinlemededir.',
        zaman: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMsgId = 'user-' + Date.now();
    const modelMsgId = 'model-' + (Date.now() + 1);
    const nowStr = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });

    const userMessage: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      metin: trimmed,
      zaman: nowStr
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setLoading(true);

    try {
      const response = await fetch('/api/cikarim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metin: trimmed })
      });

      const data = await response.json();

      if (data.success && data.sonuc) {
        const res = data.sonuc;
        const kelamMetni =
          res.kelam ||
          res.nihai_hukum ||
          'Kaziye kuantum zırhında çözümlendi ve intaç halkasına nakşedildi.';

        const modelMessage: ChatMessage = {
          id: modelMsgId,
          sender: 'model',
          metin: kelamMetni,
          zaman: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
          sonuc: res
        };
        setMessages((prev) => [...prev, modelMessage]);
      } else {
        const errorMsg = data.error || 'Çıkarım motorundan beklenmeyen bir yanıt alındı.';
        setMessages((prev) => [
          ...prev,
          {
            id: modelMsgId,
            sender: 'model',
            metin: `Hata: ${errorMsg}`,
            zaman: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
            hata: true
          }
        ]);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: modelMsgId,
          sender: 'model',
          metin: `Bağlantı Hatası: ${err.message || 'Sunucuya erişilemedi.'}`,
          zaman: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
          hata: true
        }
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => textareaRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] min-h-[580px] bg-[#16130e] border border-[#362f22] rounded-2xl overflow-hidden shadow-2xl">
      {/* Top Header Bar */}
      <div className="px-5 py-3.5 bg-[#1c1810] border-b border-[#362f22] flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#3a2418] border border-[#e08856]/50 flex items-center justify-center text-[#e08856] shadow-sm">
            <span className="text-lg font-serif-fraunces font-bold">ن</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-serif-fraunces font-bold text-[#ece3cf] tracking-wide">
                Genel Dil Modeli &middot; Sual, Kelâm ve Muhakeme Bölümü
              </h2>
              <span className="flex items-center gap-1 text-[10px] font-mono-code px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/40">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Faal
              </span>
            </div>
            <p className="text-[11px] text-[#a89a78] flex items-center gap-2">
              <span>1,048,576 Qudit Zırhı</span>
              <span>&bull;</span>
              <span>Bedihi Mantık &amp; Fıtrat Terazisi</span>
              <span>&bull;</span>
              <span>Serbest Soru &amp; Çıkarım</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleClear}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#241d13] hover:bg-[#33291b] border border-[#362f22] hover:border-[#544834] text-xs text-[#a89a78] hover:text-[#ece3cf] transition-all cursor-pointer"
            title="Sohbet geçmişini temizle"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Temizle</span>
          </button>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5 font-sans">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          const isCerh = msg.sonuc?.tenakuz_raporu?.tenakuz_var || msg.sonuc?.nihai_hukum?.includes('CERH');
          const isExpanded = !!expandedDetails[msg.id];

          return (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-4xl ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold shadow-sm ${
                  isUser
                    ? 'bg-[#33291b] border border-[#544834] text-[#ece3cf]'
                    : isCerh
                    ? 'bg-rose-950 border border-rose-800/60 text-rose-300'
                    : 'bg-[#3a2418] border border-[#e08856]/60 text-[#e08856]'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div
                className={`flex flex-col gap-1.5 max-w-[85%] sm:max-w-[78%] rounded-2xl px-4 py-3 text-xs leading-relaxed shadow-md ${
                  isUser
                    ? 'bg-[#2a2216] border border-[#443825] text-[#ece3cf] rounded-tr-none'
                    : msg.hata
                    ? 'bg-rose-950/60 border border-rose-800/70 text-rose-200 rounded-tl-none'
                    : 'bg-[#1c1810] border border-[#362f22] text-[#ece3cf] rounded-tl-none'
                }`}
              >
                {/* Header inside bubble for Model */}
                {!isUser && (
                  <div className="flex items-center justify-between pb-1 border-b border-[#362f22]/70 text-[10px] text-[#a89a78]">
                    <div className="flex items-center gap-1.5">
                      <Sparkles className="w-3 h-3 text-[#e08856]" />
                      <span className="font-semibold text-[#e08856]">Küllî İdrak Kelâmı</span>
                      {msg.sonuc?.kelam_detay?.tarz && (
                        <span className="px-1.5 py-0.2 rounded bg-[#2a2216] border border-[#3d321f] text-[9px] font-mono-code text-[#a89a78]">
                          {msg.sonuc.kelam_detay.tarz}
                        </span>
                      )}
                    </div>
                    <span>{msg.zaman}</span>
                  </div>
                )}

                {/* User Message Header */}
                {isUser && (
                  <div className="flex items-center justify-between text-[10px] text-[#a89a78] pb-0.5">
                    <span className="font-medium text-[#c4b693]">Sualiniz</span>
                    <span>{msg.zaman}</span>
                  </div>
                )}

                {/* Main Message Text */}
                <div className="whitespace-pre-wrap text-[13px] leading-relaxed text-[#f4efe4] font-sans">
                  {msg.metin}
                </div>

                {/* Model Result Badges & Details */}
                {!isUser && msg.sonuc && (
                  <div className="pt-2 mt-1 border-t border-[#362f22]/60 space-y-2">
                    {/* Hüküm Status Badge */}
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-medium border ${
                          isCerh
                            ? 'bg-rose-950/50 border-rose-800/60 text-rose-300'
                            : 'bg-emerald-950/50 border-emerald-800/60 text-emerald-300'
                        }`}
                      >
                        {isCerh ? (
                          <AlertTriangle className="w-3 h-3 text-rose-400" />
                        ) : (
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                        )}
                        <span>{msg.sonuc.nihai_hukum || 'Hüküm mühürlendi.'}</span>
                      </div>

                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => handleCopy(msg.id, msg.metin)}
                          className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] text-[#a89a78] hover:text-[#ece3cf] bg-[#241d13] border border-[#362f22] hover:border-[#544834] transition-all cursor-pointer"
                          title="Cevabı panoya kopyala"
                        >
                          {copiedId === msg.id ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span className="text-emerald-400">Kopyalandı</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Kopyala</span>
                            </>
                          )}
                        </button>

                        <button
                          onClick={() => toggleDetail(msg.id)}
                          className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] text-[#e08856] hover:text-[#f4b591] bg-[#3a2418]/60 border border-[#e08856]/40 hover:border-[#e08856] transition-all cursor-pointer"
                        >
                          <span>Teftiş</span>
                          {isExpanded ? (
                            <ChevronUp className="w-3 h-3" />
                          ) : (
                            <ChevronDown className="w-3 h-3" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Expandable Mathematical Proof & Quantum Armor Inspection */}
                    {isExpanded && (
                      <div className="mt-2 p-3 rounded-xl bg-[#120f0a] border border-[#3d321f] text-[11px] font-mono-code space-y-2.5 text-[#cfc4ac]">
                        <div className="flex items-center justify-between border-b border-[#2d2516] pb-1.5 text-[#e08856] font-semibold text-[10px]">
                          <div className="flex items-center gap-1.5">
                            <Shield className="w-3.5 h-3.5" />
                            <span>1,048,576 Qudit Zırhı &amp; Riyazi İntaç Kayıtları</span>
                          </div>
                          <span>Ferman 1-G &middot; Şerh 6706</span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[10px]">
                          <div className="p-2 rounded bg-[#1c1810] border border-[#2d2516]">
                            <div className="text-[#a89a78] mb-0.5 flex items-center gap-1">
                              <Atom className="w-3 h-3 text-sky-400" />
                              <span>Zırh Sadakati &amp; Geometri:</span>
                            </div>
                            <div>
                              Sadakat: <strong className="text-emerald-400">
                                {msg.sonuc.bir_milyon_qudit_zirhi?.kapi_51_tetabuk?.sadakat ?? '0.999'}
                              </strong>
                            </div>
                            <div>
                              d_FS Mesafesi: <span className="text-[#ece3cf]">{msg.sonuc.bir_milyon_qudit_zirhi?.fubini_study_mesafe ?? '1.57'}</span>
                            </div>
                            <div>
                              Aktif Qudit: <span className="text-[#ece3cf]">{msg.sonuc.bir_milyon_qudit_zirhi?.aktif_qudit ?? '6'}</span> / 1,048,576
                            </div>
                          </div>

                          <div className="p-2 rounded bg-[#1c1810] border border-[#2d2516]">
                            <div className="text-[#a89a78] mb-0.5 flex items-center gap-1">
                              <Scale className="w-3 h-3 text-amber-400" />
                              <span>İntaç &amp; Faz Manifoldu:</span>
                            </div>
                            <div>
                              Topoloji: <span className="text-[#ece3cf]">{msg.sonuc.intac_manifoldu?.topoloji}</span>
                            </div>
                            <div>
                              Koherans (r_K): <span className="text-emerald-400">{msg.sonuc.intac_manifoldu?.r_n}</span>
                            </div>
                            <div>
                              Faz (Φ_K): <span className="text-sky-300">{msg.sonuc.intac_manifoldu?.phi_n} rad</span>
                            </div>
                          </div>
                        </div>

                        {msg.sonuc.kelam_detay?.intac_jetonlari && msg.sonuc.kelam_detay.intac_jetonlari.length > 0 && (
                          <div className="p-2 rounded bg-[#1c1810] border border-[#2d2516] text-[10px]">
                            <div className="text-[#e08856] flex items-center gap-1 mb-1">
                              <Sparkles className="w-3 h-3" />
                              <span>J1-J5 Konuşma Makinesi Rezonans Jetonları (Determinist Fubini-Study):</span>
                            </div>
                            <div className="flex flex-wrap gap-1">
                              {msg.sonuc.kelam_detay.intac_jetonlari.map((tok: string, idx: number) => (
                                <span
                                  key={idx}
                                  className="px-2 py-0.5 rounded bg-[#2a2013] border border-[#e08856]/30 text-amber-200 text-[10px]"
                                >
                                  {tok}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {msg.sonuc.kelam_detay?.referans_kayit && (
                          <div className="p-2 rounded bg-[#1c1810] border border-[#2d2516] text-[10px]">
                            <div className="text-[#a89a78] flex items-center gap-1 mb-0.5">
                              <BookOpen className="w-3 h-3 text-[#e08856]" />
                              <span>Tâlim Edilmiş Semantik Lif Referansı:</span>
                            </div>
                            <div className="text-[#ece3cf] italic">
                              "{msg.sonuc.kelam_detay.referans_kayit}"
                            </div>
                            <div className="text-[9px] text-[#8e8267] mt-0.5">
                              Benzerlik Skoru: {msg.sonuc.kelam_detay.benzerlik} &bull; Güven: {msg.sonuc.kelam_detay.guven}
                            </div>
                          </div>
                        )}

                        {msg.sonuc.kuantum_mantik_usulleri && (
                          <div className="p-2 rounded bg-[#1c1810] border border-[#2d2516] text-[10px] space-y-0.5">
                            <span className="text-[#a89a78] font-semibold">Mantık Usulleri (Silojizma &amp; Bell):</span>
                            <div>&bull; Barbara: {msg.sonuc.kuantum_mantik_usulleri.barbara_aaa1}</div>
                            <div>&bull; Munfasıla: {msg.sonuc.kuantum_mantik_usulleri.munfasila_bell}</div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex gap-3 max-w-4xl mr-auto">
            <div className="w-8 h-8 rounded-xl bg-[#3a2418] border border-[#e08856]/60 flex items-center justify-center shrink-0 text-[#e08856] animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-[#1c1810] border border-[#362f22] rounded-2xl rounded-tl-none px-4 py-3 text-xs text-[#a89a78] flex items-center gap-3 shadow-md">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#e08856] animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-[#e08856] animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full bg-[#e08856] animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span className="text-[12px] text-[#cfc4ac]">
                Küllî İdrak muhakeme ediyor, fıtrat ve zırh mizanında tartılıyor...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 sm:p-4 bg-[#1c1810] border-t border-[#362f22]">
        <div className="max-w-4xl mx-auto flex items-end gap-2 bg-[#16130e] border border-[#362f22] focus-within:border-[#e08856] rounded-2xl p-2 transition-all shadow-inner">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Bir sual sorun, teorem veya iddia yazın (Enter ile gönder, Shift+Enter ile alt satır)..."
            disabled={loading}
            className="flex-1 bg-transparent px-3 py-2 text-xs sm:text-sm text-[#ece3cf] placeholder:text-[#6e634c] focus:outline-none resize-none max-h-40 overflow-y-auto leading-relaxed"
          />

          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="p-2.5 sm:px-4 sm:py-2.5 rounded-xl bg-[#e08856] hover:bg-[#eb9a6c] disabled:bg-[#2b2419] disabled:text-[#5f543e] text-[#16130e] font-bold text-xs transition-all flex items-center justify-center gap-1.5 shadow-md cursor-pointer disabled:cursor-not-allowed shrink-0"
            title="Kelâmı intaç et"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Gönder</span>
          </button>
        </div>

        <div className="max-w-4xl mx-auto mt-2 px-1 flex items-center justify-between text-[10px] text-[#6e634c]">
          <span>Küllî İdrak Genel Dil Modeli &middot; Ferman 1-G &amp; Ferman 2-Ø</span>
          <span>Herhangi bir serbest metin veya kaziye ile çalışır</span>
        </div>
      </div>
    </div>
  );
}
