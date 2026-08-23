export interface LanguageOption {
  code: string;
  label: string;
  nativeName: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: 'en-US', label: 'English (US)', nativeName: 'English' },
  { code: 'ml-IN', label: 'Malayalam', nativeName: 'മലയാളം' },
];

export interface VoiceServiceConfig {
  language: string;
  continuous?: boolean;
  interimResults?: boolean;
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

  public static createRecognition(config: VoiceServiceConfig): any | null {
    if (!VoiceService.isSupported()) {
      return null;
    }
    const SpeechRecognitionClass =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognitionClass();
    recognition.continuous = config.continuous ?? false;
    recognition.interimResults = config.interimResults ?? true;
    recognition.lang = config.language || 'en-US';
    return recognition;
  }
}
