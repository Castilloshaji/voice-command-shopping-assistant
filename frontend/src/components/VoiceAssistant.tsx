import React, { useState } from 'react';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { SUPPORTED_LANGUAGES } from '../services/voice';
import { apiService, CommandExecutionResponse } from '../services/api';

export type VoiceState = 'IDLE' | 'LISTENING' | 'PROCESSING' | 'EXECUTING' | 'RESULT' | 'ERROR';

interface VoiceAssistantProps {
  onCommandExecuted?: () => void;
}

export const VoiceAssistant: React.FC<VoiceAssistantProps> = ({ onCommandExecuted }) => {
  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE');
  const [executionResult, setExecutionResult] = useState<CommandExecutionResponse | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [manualText, setManualText] = useState<string>('');

  const handleExecuteCommandText = async (text: string) => {
    if (!text || !text.trim()) return;

    setVoiceState('PROCESSING');
    setApiError(null);

    try {
      setVoiceState('EXECUTING');
      const result = await apiService.executeVoiceCommand(text);
      setExecutionResult(result);
      setVoiceState('RESULT');
      if (onCommandExecuted) onCommandExecuted();
    } catch (err: any) {
      setApiError(err.message || 'Failed to execute command. Please try again.');
      setVoiceState('ERROR');
    }
  };

  const handleFinalSpeech = (finalText: string) => {
    handleExecuteCommandText(finalText);
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

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualText.trim()) return;
    const cmd = manualText.trim();
    setManualText('');
    handleExecuteCommandText(cmd);
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
    <div className="section-card voice-assistant-card">
      <header className="voice-card-header">
        <div className="title-group">
          <p className="eyebrow">Voice command</p>
          <h2>What&apos;s on your shopping list?</h2>
          <p className="section-intro">Say what you need and we&apos;ll take care of the list.</p>
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
            aria-label="Select voice recognition language"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.label} ({lang.nativeName})
              </option>
            ))}
          </select>
        </div>
      </header>

      {/* Browser Support Alert */}
      {!isSupported && (
        <div className="alert alert-warning" role="alert">
          🎤 Voice input is not supported in this browser. Please try Chrome or Edge.
        </div>
      )}

      {/* Microphone Interaction Area */}
      <div className="mic-section">
        <button
          type="button"
          className={`mic-button ${isListening ? 'listening' : ''} ${!isSupported ? 'disabled' : ''}`}
          onClick={handleMicClick}
          disabled={!isSupported}
          title={isListening ? 'Click to stop listening' : 'Click to start speaking'}
          aria-label={
            isListening
              ? 'Stop listening voice input'
              : 'Start listening voice input'
          }
        >
          <svg
            className="mic-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" y1="19" x2="12" y2="23" />
            <line x1="8" y1="23" x2="16" y2="23" />
          </svg>
        </button>

        {/* Status Label with Live Region */}
        <div className="status-label" aria-live="polite">
          {activeState === 'IDLE' && <p>Tap to speak</p>}
          {activeState === 'LISTENING' && <p className="status-listening">Listening…</p>}
          {activeState === 'PROCESSING' && <p className="status-processing">Understanding command...</p>}
          {activeState === 'EXECUTING' && <p className="status-processing">Executing command...</p>}
          {activeState === 'RESULT' && <p className="status-result">Command Executed Successfully</p>}
          {activeState === 'ERROR' && <p className="status-error">Attention Required</p>}
        </div>
      </div>

      {/* Manual Text Command Input Bar */}
      <form className="manual-command-form" onSubmit={handleManualSubmit}>
        <input
          type="text"
          className="manual-command-input"
          placeholder="Or type a voice command (e.g. 'Add 2 bottles of milk')"
          value={manualText}
          onChange={(e) => setManualText(e.target.value)}
          aria-label="Type a command input"
        />
        <button type="submit" className="btn btn-secondary" disabled={!manualText.trim()}>
          Run Command
        </button>
      </form>
      <div className="command-examples" aria-label="Example voice commands">
        <span>Try saying</span>
        <button type="button" onClick={() => setManualText('Add milk to my list')}>“Add milk”</button>
        <button type="button" onClick={() => setManualText('Add 2 bottles of milk')}>“Add 2 bottles of milk”</button>
      </div>

      {/* Live Transcript Display */}
      {(transcript || interimTranscript) && (
        <div className="transcript-box" aria-live="polite">
          <span className="transcript-label">Recognized Speech:</span>
          <p className="transcript-text">
            {transcript}
            {interimTranscript && <span className="interim-text"> {interimTranscript}...</span>}
          </p>
        </div>
      )}

      {/* Error Display */}
      {currentError && (
        <div className="alert alert-error" role="alert">
          <p>{currentError}</p>
          <button type="button" className="btn btn-sm btn-outline" onClick={handleReset}>
            Try Again
          </button>
        </div>
      )}

      {/* Action Execution Result Banner */}
      {activeState === 'RESULT' && executionResult && (
        <div className={`result-banner ${executionResult.success ? 'success-banner' : 'failure-banner'}`}>
          <div className="banner-header">
            <span className="result-icon" aria-hidden="true">{executionResult.success ? '✓' : '!'}</span>
            <span className="execution-message">{executionResult.message}</span>
          </div>
          {!executionResult.success && executionResult.data?.suggestions && executionResult.data.suggestions.length > 0 && (
            <div className="suggestion-actions" style={{ marginTop: '0.75rem' }}>
              <p style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem' }}>Did you mean?</p>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {executionResult.data.suggestions.map((sug: { product_id: number; name: string }) => (
                  <button
                    key={sug.product_id}
                    type="button"
                    className="btn btn-sm btn-outline"
                    onClick={() => handleExecuteCommandText(`Add ${sug.name}`)}
                  >
                    Add {sug.name} instead
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
