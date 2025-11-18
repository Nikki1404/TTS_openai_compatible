import { TTSService } from '../interfaces/TTSService';
import { TextToSpeechClient } from '@google-cloud/text-to-speech';
import CircuitBreaker from 'opossum';
import { circuitBreakerOptions } from '../../common/circuit-breaker';
import logger from '../../common/logger';

export class GoogleTTSService implements TTSService {
    private client: TextToSpeechClient;
    private breaker: CircuitBreaker;

    constructor() {
        const projectId = process.env.GOOGLE_PROJECT_ID || "emr-dgt-autonomous-uctr1-snbx";
        if (!projectId) {
            const errorMessage = 'GOOGLE_PROJECT_ID environment variable is not set.';
            logger.error(errorMessage);
            throw new Error(errorMessage);
        }

        const location = process.env.GOOGLE_LOCATION || 'global';
        const clientOptions = location === 'global' ? {} : { apiEndpoint: `${location}-texttospeech.googleapis.com` };
        this.client = new TextToSpeechClient({});
        this.breaker = new CircuitBreaker(this.synthesizeSpeech.bind(this), circuitBreakerOptions);
    }

    private async synthesizeSpeech(text: string): Promise<Uint8Array> {
        try {
            logger.info({ text }, 'Synthesizing speech with Google TTS');
            const voiceName = process.env.GOOGLE_TTS_VOICE_NAME || 'en-US-Wavenet-D';
            const ssmlGender = (process.env.GOOGLE_TTS_VOICE_GENDER || 'MALE') as ('MALE' | 'FEMALE' | 'NEUTRAL' | 'SSML_VOICE_GENDER_UNSPECIFIED');
            const audioEncoding = (process.env.GOOGLE_TTS_VOICE_AUDIO_ENCODING || 'MULAW') as ('MULAW' | 'LINEAR16' | 'MP3' | 'OGG_OPUS' | 'ALAW' | 'PCM' | 'AUDIO_ENCODING_UNSPECIFIED');
            const sampleRateHertz = typeof process.env.GOOGLE_TTS_VOICE_SAMPLE_RATE_HERTZ === 'string'
                ? parseInt(process.env.GOOGLE_TTS_VOICE_SAMPLE_RATE_HERTZ, 10)
                : (process.env.GOOGLE_TTS_VOICE_SAMPLE_RATE_HERTZ || 8000);

            const isSSML = /<speak[\s>]|<prosody[\s>]|<break[\s>]|<emphasis[\s>]|<google:style[\s>]/i.test(text);
            const request = {
                input: isSSML ? { ssml: text } : { text },
                voice: {
                    languageCode: process.env.GOOGLE_TTS_VOICE_LANGUAGE_CODE || 'en_US',
                    name: voiceName,
                    ssmlGender: ssmlGender,
                },
                audioConfig: { audioEncoding: audioEncoding, sampleRateHertz: sampleRateHertz },
            };

            const [response] = await this.client.synthesizeSpeech(request);
            if (!response.audioContent) {
                throw new Error('No audio content in Google TTS response.');
            }
            return response.audioContent as Uint8Array;
        } catch (err) {
            logger.error({ err, text }, 'Error synthesizing speech with Google TTS');
            throw err;
        }
    }

    synthesize(text: string): Promise<Uint8Array> {
        return this.breaker.fire(text) as Promise<Uint8Array>;
    }
}
