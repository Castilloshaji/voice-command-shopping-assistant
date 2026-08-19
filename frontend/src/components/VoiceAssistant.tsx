import React, { useState } from 'react';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { SUPPORTED_LANGUAGES } from '../services/voice';
import { apiService, CommandExecutionResponse } from '../services/api';

export type VoiceState = 'IDLE' | 'LISTENING' | 'PROCESSING' | 'EXECUTING' | 'RESULT' | 'ERROR';

export const VoiceAssistant: React.FC = () => {
  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE');
  const [executionResult, setExecutionResult] = useState<CommandExecutionResponse | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const handleFinalSpeech = async (finalText: string) => {
    if (!finalText || !finalText.trim()) return;

    setVoiceState('PROCESSING');
    setApiError(null);

    try {
      setVoiceState('EXECUTING');
      const result = await apiService.executeVoiceCommand(finalText);
      setExecutionResult(result);
      setVoiceState('RESULT');
    } catch (err: any) {
      setApiError(err.message || 'Failed to execute command. Please try again.');
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
      setExecutionResult(null);
      setApiError(null);
      setVoiceState('LISTENING');
      startListening();
    }
  };

  const handleReset = () => {
    stopListening();
    resetTranscript();
    setExecutionResult(null);
    setApiError(null);
    setVoiceState('IDLE');
  };

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
          <span className="badge preview-badge">Live Execution Active</span>
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

        {/* Status Label */}
        <div className="status-label">
          {activeState === 'IDLE' && <p>Tap the microphone to speak</p>}
          {activeState === 'LISTENING' && <p className="status-listening">Listening...</p>}
          {activeState === 'PROCESSING' && <p className="status-processing">Understanding command...</p>}
          {activeState === 'EXECUTING' && <p className="status-processing">Executing command...</p>}
          {activeState === 'RESULT' && <p className="status-result">Command Executed</p>}
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

      {/* Execution Result Display */}
      {activeState === 'RESULT' && executionResult && (
        <div className={`result-preview-card ${executionResult.success ? 'success-card' : 'failure-card'}`}>
          <div className="result-header">
            <h3>{executionResult.success ? 'Execution Successful' : 'Execution Status'}</h3>
            <span className={`intent-badge ${executionResult.intent.toLowerCase()}`}>
              {executionResult.intent}
            </span>
          </div>

          <div className="result-details">
            <p className="execution-message">{executionResult.message}</p>

            {executionResult.data && (
              <div className="data-preview">
                <span className="detail-label">Response Data:</span>
                <pre className="json-display">
                  {JSON.stringify(executionResult.data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Action Bar */}
      {(transcript || executionResult || currentError) && (
        <div className="card-actions">
          <button className="btn btn-secondary" onClick={handleReset}>
            Reset Voice Input
          </button>
        </div>
      )}
    </div>
  );
};
