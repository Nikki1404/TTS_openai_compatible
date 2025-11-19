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


#gemini-tts
import { TTSService } from '../interfaces/TTSService';
import { GoogleGenerativeAI } from '@google/generative-ai';
import CircuitBreaker from 'opossum';
import { circuitBreakerOptions } from '../../common/circuit-breaker';

export class GeminiTTSService implements TTSService {
    private generativeAi: GoogleGenerativeAI;
    private breaker: CircuitBreaker;

    constructor() {
        const apiKey = process.env.GEMINI_API_KEY;
        if (!apiKey) {
            throw new Error('Gemini API key not configured.');
        }
        this.generativeAi = new GoogleGenerativeAI(apiKey);
        this.breaker = new CircuitBreaker(this.synthesizeSpeech.bind(this), circuitBreakerOptions);
    }

    private async synthesizeSpeech(text: string): Promise<Uint8Array> {
        const model = this.generativeAi.getGenerativeModel({ model: "gemini-1.5-flash-preview" });
        const result = await model.generateContent(text);
        const response = await result.response;
        // This is a placeholder for how to get the audio data.
        // The actual implementation will depend on the API response format.
        // For now, we'll assume the response has a method to get the audio as a Uint8Array.
        // Replace this with the actual method when the API is finalized.
        // const audio = await response.audio();
        // return new Uint8Array(audio);
        return new Uint8Array(); // Placeholder
    }

    synthesize(text: string): Promise<Uint8Array> {
        return this.breaker.fire(text) as Promise<Uint8Array>;
    }
}

#google_auth-utils.js
"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getGoogleAuthToken = void 0;
const google_auth_library_1 = require("google-auth-library");
const logger_1 = __importDefault(require("../common/logger"));
let cachedToken = null;
/**
 * Generates a short-lived OAuth2 access token for Google Cloud APIs.
 * Caches the token in memory to avoid generating a new one for every session.
 */
async function getGoogleAuthToken() {
    // If we have a valid, non-expired token, return it.
    if (cachedToken && cachedToken.expiry > Date.now() + 60 * 1000) { // 60s buffer
        return cachedToken.token;
    }
    try {
        logger_1.default.info('Generating new Google Cloud auth token.');
        const auth = new google_auth_library_1.GoogleAuth({
            scopes: 'https://www.googleapis.com/auth/cloud-platform',
        });
        const accessToken = await auth.getAccessToken();
        if (!accessToken) {
            throw new Error('Failed to retrieve access token or expiry from Google Auth.');
        }
        cachedToken = {
            token: accessToken,
            expiry: Date.now() + (60 * 1000),
        };
        return cachedToken.token;
    }
    catch (err) {
        logger_1.default.error({ err }, 'Error generating Google Cloud auth token');
        throw err;
    }
}
exports.getGoogleAuthToken = getGoogleAuthToken;
//# sourceMappingURL=google-auth-utils.js.map

google-auth-utils.ts

import { GoogleAuth } from 'google-auth-library';
import logger from '../common/logger';

let cachedToken: { token: string; expiry: number } | null = null;

/**
 * Generates a short-lived OAuth2 access token for Google Cloud APIs.
 * Caches the token in memory to avoid generating a new one for every session.
 */
export async function getGoogleAuthToken(): Promise<string> {
    // If we have a valid, non-expired token, return it.
    if (cachedToken && cachedToken.expiry > Date.now() + 60 * 1000) { // 60s buffer
        return cachedToken.token;
    }

    try {
        logger.info('Generating new Google Cloud auth token.');
        const auth = new GoogleAuth({
            scopes: 'https://www.googleapis.com/auth/cloud-platform',
        });
        const accessToken = await auth.getAccessToken();

        if (!accessToken) {
            throw new Error('Failed to retrieve access token or expiry from Google Auth.');
        }

        cachedToken = {
            token: accessToken,
            expiry: Date.now() + (60 * 1000),
        };

        return cachedToken.token;
    } catch (err) {
        logger.error({ err }, 'Error generating Google Cloud auth token');
        throw err;
    }
}

#google_tts.py
import time
from google.cloud import texttospeech

def measure_api_latency(text):
    client = texttospeech.TextToSpeechClient()

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-D",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MULAW,
        sample_rate_hertz=8000
    )

    synthesis_input = texttospeech.SynthesisInput(text=text)

    # --- Measure ONLY the API call time ---
    start = time.time()
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    end = time.time()

    latency_ms = round((end - start) * 1000, 2)

    print("\n---------------------------------------")
    print("Input Text:", text)
    print("Google TTS API Call Time:", latency_ms, "ms")
    print("Audio size:", len(response.audio_content), "bytes")
    print("---------------------------------------\n")

def main():
    print("🔊 Google TTS Latency Tester (Interactive Mode)")
    print("Type text and press Enter to measure latency.")
    print("Type 'exit' to quit.\n")

    while True:
        text = input("Enter text: ")

        if text.lower() == "exit":
            print("Exiting tester...")
            break

        if not text.strip():
            print(" Please enter some text.")
            continue

        measure_api_latency(text)

if __name__ == "__main__":
    main()
