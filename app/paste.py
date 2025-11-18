import { TTSService } from '../interfaces/TTSService';
import CircuitBreaker from 'opossum';
import { circuitBreakerOptions } from '../../common/circuit-breaker';
import logger from '../../common/logger';
import axios from 'axios';
import { convertWavToMulaw8k } from '../../common/audio-utils';

export class KokoroTTSService implements TTSService {
    private apiUrl: string;
    private breaker: CircuitBreaker;

    constructor() {
        this.apiUrl = process.env.KOKORO_TTS_API_URL || 'https://whisperstream.exlservice.com/speech-api/v1/audio/speech';
        
        if (!this.apiUrl) {
            const errorMessage = 'KOKORO_TTS_API_URL environment variable is not set.';
            logger.error(errorMessage);
            throw new Error(errorMessage);
        }

        this.breaker = new CircuitBreaker(this.synthesizeSpeech.bind(this), circuitBreakerOptions);
    }

    private async synthesizeSpeech(text: string): Promise<Uint8Array> {
        try {
            logger.info({ text }, 'Synthesizing speech with Kokoro TTS');
            
            const model = process.env.KOKORO_TTS_MODEL || 'tts-1';
            const voice = process.env.KOKORO_TTS_VOICE || 'af_heart';
            const responseFormat = process.env.KOKORO_TTS_RESPONSE_FORMAT || 'wav';

            const requestBody = {
                model: model,
                voice: voice,
                input: text,
                response_format: responseFormat
            };

            const response = await axios.post(this.apiUrl, requestBody, {
                headers: {
                    'Content-Type': 'application/json'
                },
                responseType: 'arraybuffer',
                timeout: 30000 // 30 seconds timeout
            });

            if (!response.data) {
                throw new Error('No audio content in Kokoro TTS response.');
            }

            return convertWavToMulaw8k(Buffer.from(response.data))
        } catch (err) {
            logger.error({ err, text }, 'Error synthesizing speech with Kokoro TTS');
            throw err;
        }
    }

    synthesize(text: string): Promise<Uint8Array> {
        return this.breaker.fire(text) as Promise<Uint8Array>;
    }
}
