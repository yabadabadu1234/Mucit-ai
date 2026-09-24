import React, { useState, useEffect } from 'react';
import { TreatiseDoc } from '../types';
import { BookOpen, Search, FileText, ChevronRight, Copy, Check } from 'lucide-react';

export const TreatisesReader: React.FC = () => {
  const [documents, setDocuments] = useState<TreatiseDoc[]>([]);
  const [selectedSlug, setSelectedSlug] = useState<string>('meleke_haritasi');
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [searchWord, setSearchWord] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function loadDocs() {
      try {
        const res = await fetch('/api/documents');
        const data = await res.json();
        if (data.success && data.documents.length > 0) {
          setDocuments(data.documents);
        }
      } catch (err) {
        console.error('Failed to load documents list:', err);
      }
    }
    loadDocs();
  }, []);

  useEffect(() => {
    if (!selectedSlug) return;
    async function loadDocContent() {
      setLoading(true);
      try {
        const res = await fetch(`/api/document/${selectedSlug}`);
        const data = await res.json();
        if (data.success) {
          setContent(data.content);
        }
      } catch (err) {
        console.error('Failed to load document content:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDocContent();
  }, [selectedSlug]);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const currentDoc = documents.find(d => d.slug === selectedSlug);

  return (
    <div className="flex flex-col lg:flex-row gap-6 w-full">
      {/* Sidebar: Document List */}
      <div className="w-full lg:w-80 flex flex-col space-y-3">
        <div className="bg-[#1c1810] border border-[#362f22] p-4 rounded-xl space-y-3">
          <div className="flex items-center gap-2 border-b border-[#362f22] pb-3">
            <BookOpen className="w-4 h-4 text-[#e08856]" />
            <h4 className="text-sm font-semibold text-[#ece3cf]">Külliyat &amp; Risaleler</h4>
          </div>

          <div className="space-y-1.5">
            {documents.map((doc) => (
              <button
                key={doc.slug}
                onClick={() => setSelectedSlug(doc.slug)}
                className={`w-full text-left p-3 rounded-lg border transition-all text-xs flex flex-col space-y-1 ${
                  selectedSlug === doc.slug
                    ? 'bg-[#3a2418] border-[#e08856] text-[#ece3cf]'
                    : 'bg-[#16130e] border-[#362f22] text-[#a89a78] hover:text-[#ece3cf] hover:border-[#6f6449]'
                }`}
              >
                <div className="flex items-center justify-between font-semibold">
                  <span>{doc.title.split('(')[0]}</span>
                  <ChevronRight className="w-3.5 h-3.5 text-[#e08856]" />
                </div>
                <p className="text-[10px] text-[#6f6449] line-clamp-2 leading-relaxed">
                  {doc.ozet}
                </p>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col space-y-4">
        <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#362f22] pb-4">
            <div>
              <span className="text-xs font-mono-code text-[#e08856] block">
                {currentDoc?.path || 'Metin'}
              </span>
              <h3 className="text-lg font-serif-fraunces font-bold text-[#ece3cf] mt-0.5">
                {currentDoc?.title || 'Risale'}
              </h3>
            </div>

            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-[#a89a78] absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Metin içinde ara..."
                  value={searchWord}
                  onChange={(e) => setSearchWord(e.target.value)}
                  className="bg-[#16130e] border border-[#362f22] rounded-lg pl-8 pr-3 py-1.5 text-xs text-[#ece3cf] placeholder-[#6f6449] focus:outline-none focus:border-[#e08856] w-44"
                />
              </div>

              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#16130e] border border-[#362f22] hover:border-[#6f6449] text-xs text-[#a89a78] hover:text-[#ece3cf] rounded-lg transition-colors"
                title="Metni Kopyala"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Kopyalandı' : 'Kopyala'}</span>
              </button>
            </div>
          </div>

          {loading ? (
            <div className="p-12 text-center text-[#a89a78]">
              Risale yükleniyor...
            </div>
          ) : (
            <div className="bg-[#16130e] p-5 rounded-lg border border-[#362f22] max-h-[640px] overflow-y-auto font-mono-code text-xs text-[#ece3cf] leading-relaxed whitespace-pre-wrap selection:bg-[#e08856] selection:text-[#16130e]">
              {searchWord ? (
                content.split(new RegExp(`(${searchWord})`, 'gi')).map((part, i) =>
                  part.toLowerCase() === searchWord.toLowerCase() ? (
                    <mark key={i} className="bg-[#e08856] text-[#16130e] px-0.5 rounded font-bold">
                      {part}
                    </mark>
                  ) : (
                    part
                  )
                )
              ) : (
                content
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
