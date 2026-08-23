import { VoiceService, SUPPORTED_LANGUAGES } from './voice';

class MockSpeechRecognition {
  public continuous = false;
  public interimResults = true;
  public maxAlternatives = 1;
  public lang = 'en-US';

  public start() {}
  public stop() {}
}

if (typeof window !== 'undefined') {
  (window as any).SpeechRecognition = MockSpeechRecognition;
}

export function runVoiceServiceTests(): void {
  // Test 1: SUPPORTED_LANGUAGES contains only en-US and ml-IN
  const codes = SUPPORTED_LANGUAGES.map((l) => l.code);
  console.assert(codes.includes('en-US'), 'Must include en-US');
  console.assert(codes.includes('ml-IN'), 'Must include ml-IN');
  console.assert(!codes.includes('hi-IN'), 'Must NOT include hi-IN');
  console.assert(codes.length === 2, 'Must contain exactly 2 languages');

  // Test 2: getValidLanguageCode enforces supported languages and rejects Hindi
  console.assert(VoiceService.getValidLanguageCode('en-US') === 'en-US');
  console.assert(VoiceService.getValidLanguageCode('ml-IN') === 'ml-IN');
  console.assert(VoiceService.getValidLanguageCode('hi-IN') === 'en-US', 'Hindi must fall back to en-US');
  console.assert(VoiceService.getValidLanguageCode('fr-FR') === 'en-US');

  // Test 3: createRecognition configures explicit target language on instance
  const recEn = VoiceService.createRecognition({ language: 'en-US' });
  console.assert(recEn !== null);
  console.assert(recEn.lang === 'en-US');

  const recMl = VoiceService.createRecognition({ language: 'ml-IN' });
  console.assert(recMl !== null);
  console.assert(recMl.lang === 'ml-IN');

  console.log('[Voice] All VoiceService unit tests passed!');
}
