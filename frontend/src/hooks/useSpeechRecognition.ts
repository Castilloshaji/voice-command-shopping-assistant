import { useState, useCallback } from 'react';

export interface UseSpeechRecognitionOptions {
  language?: string;
}

export function useSpeechRecognition(options: UseSpeechRecognitionOptions = {}) {
  const { language = 'en-US' } = options;
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);

  const startListening = useCallback(() => {
    setError(null);
    setIsListening(true);
    // SpeechRecognition instance wiring will be expanded in Phase 6
  }, [language]);

  const stopListening = useCallback(() => {
    setIsListening(false);
  }, []);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setError(null);
  }, []);

  return {
    isListening,
    transcript,
    error,
    startListening,
    stopListening,
    resetTranscript,
    isSupported: typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window),
  };
}
