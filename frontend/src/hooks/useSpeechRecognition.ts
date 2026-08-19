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
  const [selectedLanguage, setSelectedLanguage] = useState<string>(initialLanguage);

  const recognitionRef = useRef<any>(null);
  const isSupported = VoiceService.isSupported();

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

    // Stop any existing instance
    stopListening();
    setError(null);

    try {
      const recognition = VoiceService.createRecognition({
        language: selectedLanguage,
        continuous: false,
        interimResults: true,
      });

      if (!recognition) {
        setError('Failed to initialize speech recognition.');
        return;
      }

      recognitionRef.current = recognition;

      recognition.onstart = () => {
        setIsListening(true);
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
          setTranscript(currentFinal);
          setInterimTranscript('');
          if (onFinalResult) {
            onFinalResult(currentFinal);
          }
        } else {
          setInterimTranscript(currentInterim);
        }
      };

      recognition.onerror = (event: any) => {
        const errType = event.error;
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
      setError('Failed to start microphone. Please check permissions.');
      setIsListening(false);
    }
  }, [isSupported, selectedLanguage, stopListening, onFinalResult]);

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
