export interface LanguageOption {
  code: string;
  label: string;
  nativeName: string;
}

export const SUPPORTED_VOICE_LANGUAGES: Record<string, LanguageOption> = {
  en: { code: 'en-US', label: 'English (US)', nativeName: 'English' },
  ml: { code: 'ml-IN', label: 'Malayalam', nativeName: 'മലയാളം' },
};

export const SUPPORTED_LANGUAGES: LanguageOption[] = Object.values(SUPPORTED_VOICE_LANGUAGES);

export interface VoiceServiceConfig {
  language: string;
  continuous?: boolean;
  interimResults?: boolean;
  maxAlternatives?: number;
}

// Extend global Window interface for SpeechRecognition typescript support
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export class VoiceService {
  public static isSupported(): boolean {
    return (
      typeof window !== 'undefined' &&
      ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)
    );
  }

  public static getValidLanguageCode(language: string): string {
    const validCodes = SUPPORTED_LANGUAGES.map((l) => l.code);
    if (validCodes.includes(language)) {
      return language;
    }
    // Strict fallback: never allow hi-IN or unknown codes
    return 'en-US';
  }

  public static createRecognition(config: VoiceServiceConfig): any | null {
    if (!VoiceService.isSupported()) {
      return null;
    }
    const SpeechRecognitionClass =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognitionClass();

    const targetLang = VoiceService.getValidLanguageCode(config.language);

    recognition.continuous = config.continuous ?? false;
    recognition.interimResults = config.interimResults ?? true;
    recognition.maxAlternatives = config.maxAlternatives ?? 1;
    recognition.lang = targetLang;

    console.log(`[Voice] Recognition initialized with language: ${recognition.lang}`);
    return recognition;
  }
}
