import { useState, useCallback, useRef, useEffect } from 'react';
import { VoiceService } from '../services/voice';

export interface UseSpeechRecognitionOptions {
  initialLanguage?: string;
  onFinalResult?: (finalText: string) => void;
}

export function useSpeechRecognition(options: UseSpeechRecognitionOptions = {}) {
  const { initialLanguage = 'en-US', onFinalResult } = options;

  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguageState] = useState<string>(
    VoiceService.getValidLanguageCode(initialLanguage)
  );

  const recognitionRef = useRef<any>(null);
  const isSupported = VoiceService.isSupported();

  const setSelectedLanguage = useCallback((lang: string) => {
    const validLang = VoiceService.getValidLanguageCode(lang);
    setSelectedLanguageState(validLang);
  }, []);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // Ignore errors on stopping an already stopped instance
      }
      recognitionRef.current = null;
    }
    setIsListening(false);
  }, []);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setError(null);
  }, []);

  const startListening = useCallback(() => {
    if (!isSupported) {
      setError('Voice input is not supported in this browser.');
      return;
    }

    // Always destroy any previous instance to prevent stale recognition language
    stopListening();
    setError(null);

    const validLang = VoiceService.getValidLanguageCode(selectedLanguage);

    try {
      const recognition = VoiceService.createRecognition({
        language: validLang,
        continuous: false,
        interimResults: true,
        maxAlternatives: 1,
      });

      if (!recognition) {
        setError('Failed to initialize speech recognition.');
        return;
      }

      // Explicitly enforce target language directly on instance prior to start
      recognition.lang = validLang;
      console.log(`[Voice] Recognition language explicitly set to: ${recognition.lang}`);

      recognitionRef.current = recognition;

      recognition.onstart = () => {
        setIsListening(true);
        console.log(`[Voice] Speech recognition started in ${recognition.lang}`);
      };

      recognition.onresult = (event: any) => {
        let currentInterim = '';
        let currentFinal = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          const text = result[0]?.transcript || '';
          if (result.isFinal) {
            currentFinal += text;
          } else {
            currentInterim += text;
          }
        }

        if (currentFinal) {
          const trimmedFinal = currentFinal.trim();

          // Script sanity check: If English mode returns Hindi/Devanagari script, reject transcript
          const containsDevanagari = /[\u0900-\u097F]/.test(trimmedFinal);
          if (validLang === 'en-US' && containsDevanagari) {
            console.warn('[Voice] Devanagari script detected in en-US mode:', trimmedFinal);
            setError("I couldn't reliably recognize that as English. Please try again.");
            setIsListening(false);
            return;
          }

          setTranscript(trimmedFinal);
          setInterimTranscript('');
          if (onFinalResult) {
            onFinalResult(trimmedFinal);
          }
        } else {
          setInterimTranscript(currentInterim);
        }
      };

      recognition.onerror = (event: any) => {
        const errType = event.error;
        console.error(`[Voice] Speech recognition error: ${errType}`);
        if (errType === 'not-allowed' || errType === 'service-not-allowed') {
          setError('Microphone access was denied. Please allow microphone permissions.');
        } else if (errType === 'no-speech') {
          setError('No speech was detected. Please try speaking again.');
        } else if (errType === 'network') {
          setError('Network error occurred during speech recognition.');
        } else if (errType !== 'aborted') {
          setError(`Speech recognition error: ${errType}`);
        }
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } catch (e: any) {
      console.error('[Voice] Exception starting recognition:', e);
      setError('Failed to start microphone. Please check permissions.');
      setIsListening(false);
    }
  }, [isSupported, selectedLanguage, stopListening, onFinalResult]);

  // Stop active listening if user switches language while active
  useEffect(() => {
    if (isListening) {
      stopListening();
    }
  }, [selectedLanguage]);

  useEffect(() => {
    return () => {
      stopListening();
    };
  }, [stopListening]);

  return {
    isListening,
    transcript,
    interimTranscript,
    error,
    isSupported,
    selectedLanguage,
    setSelectedLanguage,
    startListening,
    stopListening,
    resetTranscript,
  };
}
