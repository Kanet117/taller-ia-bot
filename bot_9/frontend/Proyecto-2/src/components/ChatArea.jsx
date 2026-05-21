import React, { useEffect, useRef, useState } from 'react';
import { Volume2, VolumeX, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { ttsConfig } from '../config';

export default function ChatArea({ messages, isTyping }) {
  const bottomRef = useRef(null);
  const [playingIndex, setPlayingIndex] = useState(null);
  const audioRef = useRef(null);

  // Auto-scroll al último mensaje
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSpeak = (msg, index) => {
      // If currently playing the same index, stop it
      if (playingIndex === index) {
          if (audioRef.current) {
              audioRef.current.pause();
              audioRef.current.currentTime = 0;
          }
          setPlayingIndex(null);
          return;
      }

      // Stop any existing audio
      if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
      }

      if (msg.audioData) {
          try {
              // Gemini returns raw 24kHz 16-bit mono PCM. We need to wrap it in a WAV header.
              const binaryString = atob(msg.audioData);
              const len = binaryString.length;
              const bytes = new Uint8Array(len);
              for (let i = 0; i < len; i++) {
                  bytes[i] = binaryString.charCodeAt(i);
              }

              const sampleRate = 24000;
              const numChannels = 1;
              const bitsPerSample = 16;
              const blockAlign = (numChannels * bitsPerSample) / 8;
              const byteRate = sampleRate * blockAlign;
              const dataSize = len;
              const chunkSize = 36 + dataSize;

              const buffer = new ArrayBuffer(44 + dataSize);
              const view = new DataView(buffer);

              const writeString = (v, offset, str) => {
                  for (let i = 0; i < str.length; i++) {
                      v.setUint8(offset + i, str.charCodeAt(i));
                  }
              };

              writeString(view, 0, 'RIFF');
              view.setUint32(4, chunkSize, true);
              writeString(view, 8, 'WAVE');
              writeString(view, 12, 'fmt ');
              view.setUint32(16, 16, true);
              view.setUint16(20, 1, true);
              view.setUint16(22, numChannels, true);
              view.setUint32(24, sampleRate, true);
              view.setUint32(28, byteRate, true);
              view.setUint16(32, blockAlign, true);
              view.setUint16(34, bitsPerSample, true);
              writeString(view, 36, 'data');
              view.setUint32(40, dataSize, true);

              new Uint8Array(buffer, 44).set(bytes);

              const blob = new Blob([view], { type: 'audio/wav' });
              const audioUrl = URL.createObjectURL(blob);

              const audio = new Audio(audioUrl);
              audioRef.current = audio;
              audio.onended = () => setPlayingIndex(null);
              audio.onerror = () => setPlayingIndex(null);
              setPlayingIndex(index);
              audio.play();
          } catch (error) {
              console.error("Error playing audio:", error);
              setPlayingIndex(null);
          }
      } else {
          alert('No audio available for this message.');
      }
  };

  // Stop audio on unmount
  useEffect(() => {
      return () => {
          if (audioRef.current) {
              audioRef.current.pause();
          }
      };
  }, []);

  const renderMedia = (media) => {
      if (!media.mediaType || media.mediaType === 'text') return null;

      const mediaContainerStyle = { display: 'flex', flexDirection: 'column', gap: '4px', maxWidth: '100%', marginBottom: '8px' };
      const linkStyle = { fontSize: '0.85rem', color: 'var(--accent-color)', textDecoration: 'none', display: 'inline-block', marginTop: '4px' };

      switch (media.mediaType) {
          case 'image':
              return (
                  <div style={mediaContainerStyle}>
                      <img src={media.fileUrl} alt={media.mediaContent || "Imagen"} style={{ maxWidth: '100%', maxHeight: '200px', borderRadius: '8px', objectFit: 'contain' }} />
                      <a href={media.fileUrl} target="_blank" rel="noopener noreferrer" style={linkStyle}>🔍 Abrir imagen</a>
                  </div>
              );
          case 'video':
              return (
                  <div style={mediaContainerStyle}>
                      <video src={media.fileUrl} controls style={{ maxWidth: '100%', maxHeight: '200px', borderRadius: '8px' }} />
                      <a href={media.fileUrl} target="_blank" rel="noopener noreferrer" style={linkStyle}>▶️ Abrir video</a>
                  </div>
              );
          case 'audio':
              return (
                  <div style={mediaContainerStyle}>
                      <audio src={media.fileUrl} controls style={{ maxWidth: '100%' }} />
                      <a href={media.fileUrl} target="_blank" rel="noopener noreferrer" style={linkStyle}>🎵 Descargar audio</a>
                  </div>
              );
          case 'file':
              return (
                  <div className="file-attachment" style={{ display: 'inline-block', padding: '12px', background: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                      <div style={{ marginBottom: '8px' }}>📄 {media.mediaContent || "Archivo"}</div>
                      <a href={media.fileUrl} target="_blank" rel="noopener noreferrer" download style={linkStyle}>⬇️ Descargar archivo</a>
                  </div>
              );
          default:
              return null;
      }
  };

  return (
    <div className="messages-container">
      {messages.length === 0 && (
        <div className="welcome-screen">
            <h1>Hello</h1>
            <h2>How can I help you today?</h2>
        </div>
      )}

      {messages.map((msg, index) => (
        <div key={index} className={`message ${msg.role}`}>
          <div className="message-content">
            <div className={`avatar ${msg.role}`}>
              {msg.role === 'ai' ? '✦' : 'U'}
            </div>
            <div className="text-wrapper" style={{ width: '100%' }}>
                {msg.mediaInfos && msg.mediaInfos.length > 0 && (
                    <div className="media-attachments-container" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '8px' }}>
                        {msg.mediaInfos.map((media, mIndex) => (
                            <div key={mIndex} className={`media-attachment ${media.mediaType === 'file' ? 'file-attachment' : ''}`}>
                                {renderMedia(media)}
                            </div>
                        ))}
                    </div>
                )}
                {/* Legacy support just in case */}
                {msg.mediaType && msg.mediaType !== 'text' && !msg.mediaInfos && (
                    <div className={`media-attachment ${msg.mediaType === 'file' ? 'file-attachment' : ''}`}>
                        {renderMedia(msg)}
                    </div>
                )}
                {msg.text && (
                    <div className="text-content">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>
                )}
                {msg.generated_image && (
                    <div className="generated-image-container" style={{ marginTop: '10px' }}>
                        <img src={`data:image/jpeg;base64,${msg.generated_image}`} alt="Generated" style={{ maxWidth: '100%', borderRadius: '8px' }} />
                    </div>
                )}
                {msg.role === 'ai' && (
                    <div className="action-buttons">
                        {msg.audioData && (
                            <button 
                                className="action-btn" 
                                title={playingIndex === index ? "Stop speaking" : "Listen"}
                                onClick={() => handleSpeak(msg, index)}
                            >
                                {playingIndex === index ? <VolumeX size={16} /> : <Volume2 size={16} />}
                            </button>
                        )}
                        <button className="action-btn" title="Copy text" onClick={() => navigator.clipboard.writeText(msg.text)}>
                            <Copy size={16} />
                        </button>
                        <button className="action-btn" title="Good response">
                            <ThumbsUp size={16} />
                        </button>
                        <button className="action-btn" title="Bad response">
                            <ThumbsDown size={16} />
                        </button>
                    </div>
                )}
            </div>
          </div>
        </div>
      ))}
      
      {isTyping && (
        <div className="message ai">
          <div className="message-content">
            <div className="avatar ai">✦</div>
            <div className="text-wrapper" style={{ width: '100%', display: 'flex', alignItems: 'center' }}>
                <div className="typing-indicator" style={{ display: 'flex', gap: '4px', padding: '8px 0' }}>
                    <span style={{ width: '8px', height: '8px', background: 'var(--accent-color, #888)', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out both' }}></span>
                    <span style={{ width: '8px', height: '8px', background: 'var(--accent-color, #888)', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out both', animationDelay: '0.2s' }}></span>
                    <span style={{ width: '8px', height: '8px', background: 'var(--accent-color, #888)', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out both', animationDelay: '0.4s' }}></span>
                </div>
                <style>{`
                  @keyframes bounce {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1); }
                  }
                `}</style>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
