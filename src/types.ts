export interface Meleke {
  id: string;
  no: number;
  ad: string;
  tier: number;
  tierAd: string;
  rol: 'kurucu' | 'koruyucu' | 'çözücü';
  tanim: string;
  kapiTipi: string;
  girisler: string[];
  cikislar: string[];
  detay: string;
}

export interface ArcGridPair {
  input: number[][];
  output: number[][];
}

export interface ArcTask {
  train: ArcGridPair[];
  test: Array<{
    input: number[][];
    output?: number[][];
  }>;
}

export interface ReasoningTraceStep {
  tier: string;
  meleke: string;
  eylem: string;
  sure: string;
  status: string;
}

export interface ArcSimulationResult {
  success: boolean;
  detectedRule: string;
  trace: ReasoningTraceStep[];
  predictedGrid: number[][];
  accuracyConfidence: number;
  fubiniStudyMetric: number;
  elapsedMs: number;
}

export interface QuditState {
  quditIndex: number;
  cartanPhase: number;
  real: number;
  imag: number;
  probability: number;
}

export interface TelemetrySummary {
  ayar: string;
  parametre: number;
  sure_sn: number;
  kayip_cagrisi: number;
  sadakat: Record<string, any>;
  son_sadakat: number;
  mizan: Record<string, any>;
  kademe_gorevi: string;
  talim_gunlugu: string[];
  kefeler: Record<string, any>;
  darbogazlar: Array<{
    meleke: string;
    sure: number;
    pay: number;
    ameliye: string;
  }>;
}

export interface TreatiseDoc {
  title: string;
  slug: string;
  ozet: string;
  path: string;
}
