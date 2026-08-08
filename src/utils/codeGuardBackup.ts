/**
 * NİZAMNAME & TALİMAT-I KATİYE: KUŞATMA VE YEDEKLEME MOTORU
 * Birinci Vazife: Pre/Post Injection & Backup System
 */

export interface CodeBackupSnapshot {
  id: string;
  fileId: string;
  filePath: string;
  timestamp: string;
  language: 'python' | 'cpp';
  originalCode: string;
  preInjectionHeader: string;
  postInjectionFooter: string;
  guardedCode: string;
  note: string;
}

// Pre/Post injection templates
export const PYTHON_PRE_HEADER = `"""
================================================================================
[NİZAMNAME KUŞATMASI - PRE-INJECTION HEADER BLOCK]
KÜLLÎ SANAL GPU SÜRÜCÜSÜ MUHAFAZA MÜHÜRÜ (KULLI_GPU DRIVER PROTECTION SEAL)
Sistem Durumu: Âtıl / Pasif Koruma Bloğu
================================================================================
"""`;

export const PYTHON_POST_FOOTER = `"""
================================================================================
[NİZAMNAME MÜHÜR - POST-INJECTION FOOTER BLOCK]
KÜLLÎ SANAL GPU DRIVER BACKUP INTEGRITY VERIFIED (ZAYİATSIZ MÜHÜR)
Sistem Durumu: Âtıl / Pasif Sonlandırma Bloğu
================================================================================
"""`;

export const CPP_PRE_HEADER = `/*
 * ================================================================================
 * [NİZAMNAME KUŞATMASI - PRE-INJECTION HEADER BLOCK]
 * KÜLLÎ C++ CUDA VMM LOW-LEVEL DRIVER PROTECTION SEAL
 * System Status: Non-executable Passive Guard Block
 * ================================================================================
 */`;

export const CPP_POST_FOOTER = `/*
 * ================================================================================
 * [NİZAMNAME MÜHÜR - POST-INJECTION FOOTER BLOCK]
 * KÜLLÎ C++ CUDA DRIVER BACKUP INTEGRITY VERIFIED (ZAYİATSIZ MÜHÜR)
 * System Status: Non-executable Passive Guard Block
 * ================================================================================
 */`;

/**
 * Encapsulates code with non-executable pre/post injection blocks
 */
export function injectPrePostGuards(code: string, language: 'python' | 'cpp'): {
  guardedCode: string;
  header: string;
  footer: string;
} {
  const header = language === 'python' ? PYTHON_PRE_HEADER : CPP_PRE_HEADER;
  const footer = language === 'python' ? PYTHON_POST_FOOTER : CPP_POST_FOOTER;

  // Check if already injected to avoid duplicate wrapping
  if (code.startsWith(header.trim()) && code.endsWith(footer.trim())) {
    return { guardedCode: code, header, footer };
  }

  const guardedCode = `${header}\n\n${code.trim()}\n\n${footer}`;
  return { guardedCode, header, footer };
}

/**
 * Removes pre/post injection blocks to get clean executable body
 */
export function stripPrePostGuards(code: string, language: 'python' | 'cpp'): string {
  const header = language === 'python' ? PYTHON_PRE_HEADER : CPP_PRE_HEADER;
  const footer = language === 'python' ? PYTHON_POST_FOOTER : CPP_POST_FOOTER;

  let cleaned = code;
  if (cleaned.startsWith(header)) {
    cleaned = cleaned.substring(header.length).trim();
  }
  if (cleaned.endsWith(footer)) {
    cleaned = cleaned.substring(0, cleaned.length - footer.length).trim();
  }
  return cleaned;
}

// Global Backup Storage
class BackupRepository {
  private backups: Map<string, CodeBackupSnapshot[]> = new Map();

  createBackup(
    fileId: string, 
    filePath: string, 
    code: string, 
    language: 'python' | 'cpp',
    note: string = 'Otomatik Nizamname Yedegi'
  ): CodeBackupSnapshot {
    const existing = this.backups.get(fileId) || [];
    
    // DEBOUNCE & SINGLE-TRIGGER MANDATE: Check if an identical backup for this file already exists
    if (existing.length > 0 && existing[0].originalCode.trim() === code.trim()) {
      return existing[0]; // Return existing snapshot without duplicating
    }

    const { guardedCode, header, footer } = injectPrePostGuards(code, language);

    const snapshot: CodeBackupSnapshot = {
      id: `BACKUP_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
      fileId,
      filePath,
      timestamp: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      language,
      originalCode: code,
      preInjectionHeader: header,
      postInjectionFooter: footer,
      guardedCode,
      note
    };

    this.backups.set(fileId, [snapshot, ...existing]);
    return snapshot;
  }

  getBackupsForFile(fileId: string): CodeBackupSnapshot[] {
    return this.backups.get(fileId) || [];
  }

  getAllBackups(): CodeBackupSnapshot[] {
    const all: CodeBackupSnapshot[] = [];
    this.backups.forEach((list) => all.push(...list));
    return all.sort((a, b) => b.id.localeCompare(a.id));
  }
}

// Singleton Instance
export const codeBackupRepo = new BackupRepository();
