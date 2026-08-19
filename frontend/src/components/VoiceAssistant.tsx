import React, { useState } from 'react';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { SUPPORTED_LANGUAGES } from '../services/voice';
import { apiService } from '../services/api';
import { ParsedIntent } from '../types/intent';

export type VoiceState = 'IDLE' | 'LISTENING' | 'PROCESSING' | 'RESULT' | 'ERROR';

export const VoiceAssistant: React.FC = () => {
  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE');
  const [parsedResult, setParsedResult] = useState<ParsedIntent | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const handleFinalSpeech = async (finalText: string) => {
    if (!finalText || !finalText.trim()) return;

    setVoiceState('PROCESSING');
    setApiError(null);

    try {
      const result = await apiService.parseVoiceCommand(finalText);
      setParsedResult(result);
      setVoiceState('RESULT');
    } catch (err: any) {
      setApiError(err.message || 'Failed to understand command. Please try again.');
      setVoiceState('ERROR');
    }
  };

  const {
    isListening,
    transcript,
    interimTranscript,
    error: speechError,
    isSupported,
    selectedLanguage,
    setSelectedLanguage,
    startListening,
    stopListening,
    resetTranscript,
  } = useSpeechRecognition({
    initialLanguage: 'en-US',
    onFinalResult: handleFinalSpeech,
  });

  const handleMicClick = () => {
    if (isListening) {
      stopListening();
    } else {
      resetTranscript();
      setParsedResult(null);
      setApiError(null);
      setVoiceState('LISTENING');
      startListening();
    }
  };

  const handleReset = () => {
    stopListening();
    resetTranscript();
    setParsedResult(null);
    setApiError(null);
    setVoiceState('IDLE');
  };

  // Synchronize state if speech recognition encounters an error or stops
  const currentError = speechError || apiError;
  const activeState = currentError
    ? 'ERROR'
    : isListening
    ? 'LISTENING'
    : voiceState;

  return (
    <div className="voice-assistant-card">
      <header className="voice-card-header">
        <div className="title-group">
          <h2>Voice Command Assistant</h2>
          <span className="badge preview-badge">Preview Mode (Non-Executing)</span>
        </div>

        {/* Language Selector */}
        <div className="language-selector">
          <label htmlFor="lang-select">Language:</label>
          <select
            id="lang-select"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            disabled={isListening}
            className="lang-dropdown"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.label} ({lang.nativeName})
              </option>
            ))}
          </select>
        </div>
      </header>

      {/* Browser Support Banner */}
      {!isSupported && (
        <div className="alert alert-warning" id="browser-support-alert">
          🎤 Voice input is not supported in this browser. Please try Chrome or Edge.
        </div>
      )}

      {/* Main Microphone Interaction Area */}
      <div className="mic-section">
        <button
          className={`mic-button ${isListening ? 'listening' : ''} ${
            !isSupported ? 'disabled' : ''
          }`}
          onClick={handleMicClick}
          disabled={!isSupported}
          title={isListening ? 'Click to stop listening' : 'Click to start speaking'}
          aria-label="Toggle voice input"
        >
          <svg
            className="mic-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" y1="19" x2="12" y2="23" />
            <line x1="8" y1="23" x2="16" y2="23" />
          </svg>
        </button>

        {/* Status Prompt */}
        <div className="status-label">
          {activeState === 'IDLE' && <p>Tap the microphone to speak</p>}
          {activeState === 'LISTENING' && <p className="status-listening">Listening...</p>}
          {activeState === 'PROCESSING' && <p className="status-processing">Understanding command...</p>}
          {activeState === 'RESULT' && <p className="status-result">Command Parsed</p>}
          {activeState === 'ERROR' && <p className="status-error">Attention Required</p>}
        </div>
      </div>

      {/* Live Transcript Display */}
      {(transcript || interimTranscript) && (
        <div className="transcript-box">
          <span className="transcript-label">Recognized Speech:</span>
          <p className="transcript-text">
            {transcript}
            {interimTranscript && (
              <span className="interim-text"> {interimTranscript}...</span>
            )}
          </p>
        </div>
      )}

      {/* Error Display */}
      {currentError && (
        <div className="alert alert-error">
          <p>{currentError}</p>
          <button className="btn btn-sm btn-outline" onClick={handleReset}>
            Try Again
          </button>
        </div>
      )}

      {/* Parsed Intent Result Preview */}
      {activeState === 'RESULT' && parsedResult && (
        <div className="result-preview-card">
          <div className="result-header">
            <h3>Parsed Intent Result</h3>
            <span className={`intent-badge ${parsedResult.intent.toLowerCase()}`}>
              {parsedResult.intent}
            </span>
          </div>

          <div className="result-details">
            <div className="detail-row">
              <span className="detail-label">Recognized Command:</span>
              <span className="detail-value">"{parsedResult.original_text}"</span>
            </div>

            {parsedResult.item && (
              <div className="detail-row">
                <span className="detail-label">Item:</span>
                <span className="detail-value highlight">{parsedResult.item}</span>
              </div>
            )}

            {parsedResult.quantity !== undefined && parsedResult.quantity !== null && (
              <div className="detail-row">
                <span className="detail-label">Quantity:</span>
                <span className="detail-value">{parsedResult.quantity}</span>
              </div>
            )}

            {parsedResult.unit && (
              <div className="detail-row">
                <span className="detail-label">Unit:</span>
                <span className="detail-value">{parsedResult.unit}</span>
              </div>
            )}

            {parsedResult.max_price !== undefined && parsedResult.max_price !== null && (
              <div className="detail-row">
                <span className="detail-label">Max Price:</span>
                <span className="detail-value">${parsedResult.max_price}</span>
              </div>
            )}

            {parsedResult.min_price !== undefined && parsedResult.min_price !== null && (
              <div className="detail-row">
                <span className="detail-label">Min Price:</span>
                <span className="detail-value">${parsedResult.min_price}</span>
              </div>
            )}

            {parsedResult.brand && (
              <div className="detail-row">
                <span className="detail-label">Brand:</span>
                <span className="detail-value">{parsedResult.brand}</span>
              </div>
            )}
          </div>

          <div className="notice-footer">
            ℹ️ Voice commands are currently in <strong>Parse & Preview Mode</strong>. No backend data has been modified.
          </div>
        </div>
      )}

      {/* Action Bar */}
      {(transcript || parsedResult || currentError) && (
        <div className="card-actions">
          <button className="btn btn-secondary" onClick={handleReset}>
            Reset Voice Input
          </button>
        </div>
      )}
    </div>
  );
};
