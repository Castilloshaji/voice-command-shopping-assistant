export interface VoiceServiceConfig {
  language: string;
  continuous: boolean;
  interimResults: boolean;
}

export interface SpeechRecognitionResultHandler {
  onResult: (transcript: string, isFinal: boolean) => void;
  onError: (error: string) => void;
  onEnd: () => void;
}

export class VoiceService {
  public static isSupported(): boolean {
    return 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
  }
}
