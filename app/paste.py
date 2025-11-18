import WebSocket from 'ws';
import CircuitBreaker from 'opossum';
import logger from '../../common/logger';
import { TTSService } from '../interfaces/TTSService';
import { convertWavToMulaw8k } from '../../common/audio-utils';
import { circuitBreakerOptions } from '../../common/circuit-breaker';

interface QueuedRequest {
    text: string;
    resolve: (value: Uint8Array) => void;
    reject: (reason?: any) => void;
    requestId: string;
    timeout?: NodeJS.Timeout;
}

export class KokoroTTSWSService implements TTSService {
    private wsUrl: string;
    private breaker: CircuitBreaker;
    private defaultVoice: string;
    private defaultSpeed: number;
    private defaultFormat: string;

    // Persistent connection management
    private ws: WebSocket | null = null;
    private connectionPromise: Promise<void> | null = null;
    private requestQueue: QueuedRequest[] = []; // Changed: Queue instead of single request
    private currentRequest: QueuedRequest | null = null;
    private audioChunks: Buffer[] = [];
    private sampleRate: number = 24000;
    private isFloat32: boolean = true;
    private pingInterval: NodeJS.Timeout | null = null; // Added: Keep-alive mechanism
    private isConnecting: boolean = false; // Added: Prevent multiple connection attempts

    constructor() {
        this.wsUrl = process.env.KOKORO_TTS_WS_URL || `wss://whisperstream.exlservice.com:3000/ws`;
        this.defaultVoice = process.env.KOKORO_TTS_VOICE || 'af_heart';
        this.defaultSpeed = parseFloat(process.env.KOKORO_TTS_SPEED || '1.0');
        this.defaultFormat = process.env.KOKORO_TTS_FORMAT || 'f32';
        this.isFloat32 = this.defaultFormat === 'f32';

        // Circuit breaker with reasonable timeout
        const kokoroCircuitBreakerOptions = {
            ...circuitBreakerOptions,
            timeout: 60000 // 1 minute - more reasonable for real-time conversations
        };
        this.breaker = new CircuitBreaker(this.performSynthesis.bind(this), kokoroCircuitBreakerOptions);
    }

    private async ensureConnection(): Promise<void> {
        // Fix: Check if connection is healthy
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return; // Already connected
        }

        // Fix: Prevent multiple connection attempts
        if (this.isConnecting || this.connectionPromise) {
            return this.connectionPromise!;
        }

        this.isConnecting = true;

        // Fix: Implement proper retry logic with exponential backoff
        let retries = 3;
        let delay = 1000; // Start with 1 second

        while (retries > 0) {
            try {
                await this.createConnection();
                this.isConnecting = false;
                return;
            } catch (error) {
                retries--;
                logger.warn({ error }, `Connection attempt failed, ${retries} retries left:`);

                if (retries === 0) {
                    this.isConnecting = false;
                    throw error;
                }

                // Exponential backoff
                await new Promise(resolve => setTimeout(resolve, delay));
                delay *= 2; // Double the delay for next retry
            }
        }
    }

    private createConnection(): Promise<void> {
        return new Promise((resolve, reject) => {
            logger.info('Creating Kokoro TTS WebSocket connection');

            // Clean up existing connection
            this.cleanup();

            this.ws = new WebSocket(this.wsUrl);

            const connectionTimeout = setTimeout(() => {
                logger.error('WebSocket connection timeout');
                if (this.ws) {
                    this.ws.close();
                }
                reject(new Error('Connection timeout'));
            }, 10000); // 10 seconds connection timeout

            this.ws.on('open', () => {
                clearTimeout(connectionTimeout);
                logger.info('Kokoro TTS WebSocket connected');

                // Fix: Start keep-alive mechanism
                this.startKeepAlive();

                this.connectionPromise = null;
                resolve();

                // Process queued requests
                this.processQueue();
            });

            this.ws.on('error', (error) => {
                clearTimeout(connectionTimeout);
                logger.error({ error }, 'Kokoro TTS WebSocket connection error');
                this.connectionPromise = null;
                reject(error);
            });

            this.ws.on('close', (code, reason) => {
                clearTimeout(connectionTimeout);
                logger.warn(`Kokoro TTS WebSocket closed: ${code} ${reason ? reason.toString() : ''}`);

                this.cleanup();

                // Fix: Auto-reconnect on unexpected closure
                if (code !== 1000 && (this.requestQueue.length > 0 || this.currentRequest)) {
                    logger.info('Attempting to reconnect due to unexpected closure...');
                    setTimeout(() => {
                        this.ensureConnection().catch(error => {
                            logger.error('Reconnection failed:', error);
                            this.rejectAllRequests(new Error(`Connection lost: ${code}`));
                        });
                    }, 2000); // Wait 2 seconds before reconnecting
                }
            });

            // Handle all incoming messages
            this.ws.on('message', this.handleMessage.bind(this));
        });
    }

    // Fix: Add keep-alive mechanism for long idle periods
    private startKeepAlive(): void {
        this.stopKeepAlive(); // Clear any existing interval

        this.pingInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                // Send a ping frame to keep connection alive
                this.ws.ping();
                logger.debug('Sent WebSocket ping');
            }
        }, 30000); // Ping every 30 seconds
    }

    private stopKeepAlive(): void {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    private cleanup(): void {
        this.stopKeepAlive();
        this.ws = null;
        this.connectionPromise = null;
        this.isConnecting = false;
    }

    private rejectAllRequests(error: Error): void {
        // Reject current request
        if (this.currentRequest) {
            if (this.currentRequest.timeout) {
                clearTimeout(this.currentRequest.timeout);
            }
            this.currentRequest.reject(error);
            this.currentRequest = null;
        }

        // Reject all queued requests
        while (this.requestQueue.length > 0) {
            const request = this.requestQueue.shift()!;
            if (request.timeout) {
                clearTimeout(request.timeout);
            }
            request.reject(error);
        }

        this.audioChunks = [];
    }

    private handleMessage(data: WebSocket.Data): void {
        try {
            if (Buffer.isBuffer(data)) {
                try {
                    const jsonString = data.toString('utf8');
                    const message = JSON.parse(jsonString);
                    // logger.debug('Parsed JSON from buffer:', message);
                    this.handleControlMessage(message);
                } catch {
                    // logger.debug(`Received audio chunk: ${data.length} bytes`);
                    this.audioChunks.push(data);
                }
            } else {
                const message = JSON.parse(data.toString());
                // logger.debug('Received JSON message:', message);
                this.handleControlMessage(message);
            }
        } catch (error) {
            logger.error({ error }, 'Error processing WebSocket message');
            if (this.currentRequest) {
                if (this.currentRequest.timeout) {
                    clearTimeout(this.currentRequest.timeout);
                }
                this.currentRequest.reject(error);
                this.currentRequest = null;
                this.processQueue(); // Process next request
            }
        }
    }

    private handleControlMessage(message: any): void {
        switch (message.type) {
            case 'meta':
                this.sampleRate = parseInt(message.sample_rate) || 24000;
                this.isFloat32 = message.sample_format === 'f32';
                // logger.info(`Kokoro TTS meta: sr=${this.sampleRate}, fmt=${message.sample_format}`);
                break;

            case 'ttfa':
                // logger.info(`Kokoro TTS TTFA: ${message.ms}ms`);
                break;

            case 'done':
                if (message.error) {
                    logger.error(`Kokoro TTS error: ${message.error}`);
                    if (this.currentRequest) {
                        if (this.currentRequest.timeout) {
                            clearTimeout(this.currentRequest.timeout);
                        }
                        this.currentRequest.reject(new Error(`Kokoro TTS error: ${message.error}`));
                        this.currentRequest = null;
                    }
                } else {
                    logger.info(`Kokoro TTS done: gen=${message.total_ms}ms, audio=${message.audio_ms}ms`);

                    if (this.currentRequest) {
                        if (this.currentRequest.timeout) {
                            clearTimeout(this.currentRequest.timeout);
                        }
                        logger.info('Starting audio processing...');

                        // Process and resolve current request
                        this.processAudioChunks()
                            .then((result) => {
                                logger.info('Audio processing completed successfully');
                                this.currentRequest!.resolve(result);
                            })
                            .catch((error) => {
                                logger.error({ error }, 'Audio processing failed');
                                this.currentRequest!.reject(error);
                            })
                            .finally(() => {
                                this.currentRequest = null;
                                this.audioChunks = []; // Reset for next request
                                this.processQueue(); // Fix: Process next queued request
                            });
                    }
                }
                break;

            default:
                logger.debug(`Unknown message type: ${message.type}`);
        }
    }

    // Fix: Process queued requests
    private processQueue(): void {
        if (this.currentRequest || this.requestQueue.length === 0) {
            return; // Already processing or no requests queued
        }

        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return; // Connection not ready
        }

        const request = this.requestQueue.shift()!;
        this.currentRequest = request;
        this.audioChunks = [];

        // Send synthesis request
        const requestPayload = {
            text: request.text,
            voice: this.defaultVoice,
            speed: this.defaultSpeed,
            format: this.defaultFormat
        };

        logger.info({ text: request.text }, 'Processing queued synthesis request');
        this.ws.send(JSON.stringify(requestPayload));
    }

    private performSynthesis(text: string): Promise<Uint8Array> {
        return new Promise(async (resolve, reject) => {
            try {
                // Generate unique request ID
                const requestId = `kokoro-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

                // Set up timeout
                const timeout = setTimeout(() => {
                    // Find and reject the specific request
                    if (this.currentRequest && this.currentRequest.requestId === requestId) {
                        logger.warn('Current request timeout');
                        this.currentRequest.reject(new Error('Synthesis timeout after 60 seconds'));
                        this.currentRequest = null;
                        this.audioChunks = [];
                        this.processQueue(); // Process next request
                    } else {
                        // Remove from queue if still waiting
                        const queueIndex = this.requestQueue.findIndex(req => req.requestId === requestId);
                        if (queueIndex !== -1) {
                            logger.warn('Queued request timeout');
                            const timedOutRequest = this.requestQueue.splice(queueIndex, 1)[0];
                            timedOutRequest.reject(new Error('Synthesis timeout after 60 seconds'));
                        }
                    }
                }, 60000); // 1 minute timeout

                // Create request object
                const request: QueuedRequest = {
                    text,
                    resolve,
                    reject,
                    requestId,
                    timeout
                };

                // Fix: Add to queue instead of rejecting if busy
                if (this.currentRequest) {
                    logger.info('Adding request to queue (another request in progress)');
                    this.requestQueue.push(request);
                } else {
                    // Ensure we have a connection
                    await this.ensureConnection();

                    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                        throw new Error('WebSocket connection not available');
                    }

                    // Process immediately
                    this.currentRequest = request;
                    this.audioChunks = [];

                    // Send synthesis request
                    const requestPayload = {
                        text: text,
                        voice: this.defaultVoice,
                        speed: this.defaultSpeed,
                        format: this.defaultFormat
                    };

                    logger.info({ text }, 'Synthesizing speech with Kokoro TTS WebSocket');
                    this.ws.send(JSON.stringify(requestPayload));
                }

            } catch (error) {
                reject(error);
            }
        });
    }

    private async processAudioChunks(): Promise<Uint8Array> {
        if (this.audioChunks.length === 0) {
            throw new Error('No audio data received from Kokoro TTS');
        }

        // Concatenate chunks
        const audioBuffer = Buffer.concat(this.audioChunks);
        logger.info(`Processing ${audioBuffer.length} bytes of audio data (${this.sampleRate}Hz, ${this.isFloat32 ? 'float32' : 'int16'})`);

        try {
            let mulawData: Uint8Array;

            // Convert to WAV and then to mu-law 8kHz
            if (this.isFloat32) {
                // logger.info('Creating WAV buffer...');
                const wavBuffer = this.createWavBuffer(audioBuffer, this.sampleRate, this.isFloat32);
                
                // logger.info('Converting to mu-law 8kHz...');
                mulawData = convertWavToMulaw8k(wavBuffer);
            } else {
                mulawData = convertWavToMulaw8k(audioBuffer);
            }

            logger.info(`Conversion complete. Output size: ${mulawData.length} bytes (mu-law 8kHz)`);
            return mulawData;
        } catch (error) {
            logger.error({ error }, 'Error converting audio data');
            throw error;
        }
    }

    private createWavBuffer(audioData: Buffer, sampleRate: number, isFloat32: boolean): Buffer {
        const bytesPerSample = isFloat32 ? 4 : 2;
        const byteRate = sampleRate * 1 * bytesPerSample;
        const blockAlign = 1 * bytesPerSample;
        const bitsPerSample = bytesPerSample * 8;

        const header = Buffer.alloc(44);

        // RIFF header
        header.write('RIFF', 0);
        header.writeUInt32LE(36 + audioData.length, 4);
        header.write('WAVE', 8);

        // fmt chunk
        header.write('fmt ', 12);
        header.writeUInt32LE(16, 16);
        header.writeUInt16LE(isFloat32 ? 3 : 1, 20);
        header.writeUInt16LE(1, 22);
        header.writeUInt32LE(sampleRate, 24);
        header.writeUInt32LE(byteRate, 28);
        header.writeUInt16LE(blockAlign, 32);
        header.writeUInt16LE(bitsPerSample, 34);

        // data chunk
        header.write('data', 36);
        header.writeUInt32LE(audioData.length, 40);

        return Buffer.concat([header, audioData]);
    }

    synthesize(text: string): Promise<Uint8Array> {
        return this.breaker.fire(text) as Promise<Uint8Array>;
    }

    // Method to gracefully close connection when Genesys session ends
    public close(): void {
        logger.info('Closing Kokoro TTS WebSocket');

        // Reject all pending requests
        this.rejectAllRequests(new Error('Service closing'));

        if (this.ws) {
            this.ws.close();
        }

        // Clean up connection
        this.cleanup();        
    }
};

The KPipeline object relies on massive, Python-native libraries like PyTorch and NumPy. These libraries and their underlying C/C++ speed optimizations do not exist in the Node.js ecosystem.

You would have to rewrite the entire Kokoro engine in TypeScript, which is completely impractical.

The only way to use the existing, fast Python logic without the slow public network is to use Inter-Process Communication (IPC).

This involves:

Eliminating the WebSocket Server: Replace the FastAPI WebSocket server with a simple Python script.

Using Node.js as a Parent: Your TypeScript service uses Node.js's child_process to run the Python script.

Fast Communication: Text is passed to Python via stdin, and binary audio data is returned directly via stdout.

Impact: This bypasses the entire TCP/IP network stack and provides the minimum achievable latency while retaining the proven Python Kokoro engine.
