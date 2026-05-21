import React, { useState, useRef } from 'react';
import { Send, Image as ImageIcon, Mic, Paperclip, X, Square } from 'lucide-react';

export default function InputArea({ onSendMessage }) {
  const [text, setText] = useState('');
  const [stagedFiles, setStagedFiles] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const fileInputRef = useRef(null);
  const mediaInputRef = useRef(null);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const handleSend = () => {
    if (text.trim() === '' && stagedFiles.length === 0) return;
    onSendMessage(text, stagedFiles, null);
    setText('');
    setStagedFiles([]);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      setStagedFiles(prev => [...prev, ...files]);
    }
    // Reset inputs
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (mediaInputRef.current) mediaInputRef.current.value = '';
  };

  const removeStagedFile = (index) => {
    setStagedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const audioFile = new File([audioBlob], 'grabacion_audio.webm', { type: 'audio/webm' });
        setStagedFiles(prev => [...prev, audioFile]);
        
        // Clean up tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("No se pudo acceder al micrófono.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="input-wrapper">
      {stagedFiles.length > 0 && (
        <div className="staged-files-container" style={{ display: 'flex', gap: '8px', padding: '8px', flexWrap: 'wrap', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px 8px 0 0' }}>
          {stagedFiles.map((file, index) => (
            <div key={index} className="staged-file" style={{ position: 'relative', display: 'flex', alignItems: 'center', background: 'var(--bg-primary)', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
              <span style={{ maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{file.name}</span>
              <button 
                onClick={() => removeStagedFile(index)} 
                style={{ background: 'none', border: 'none', cursor: 'pointer', marginLeft: '4px', color: 'var(--text-secondary)' }}
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
      <div className="input-box-container" style={stagedFiles.length > 0 ? { borderRadius: '0 0 24px 24px' } : {}}>
        <div className="input-box">
          <input 
            type="file" 
            multiple
            ref={fileInputRef} 
            style={{ display: 'none' }} 
            onChange={handleFileUpload} 
          />
          <button className="icon-btn" onClick={() => fileInputRef.current?.click()} title="Upload files">
            <Paperclip size={20} />
          </button>

          <input 
            type="file" 
            multiple
            accept="image/*,video/*,audio/*"
            ref={mediaInputRef} 
            style={{ display: 'none' }} 
            onChange={handleFileUpload} 
          />
          <button className="icon-btn" onClick={() => mediaInputRef.current?.click()} title="Upload media">
            <ImageIcon size={20} />
          </button>

          <input
            type="text"
            placeholder={isRecording ? "Recording audio..." : "Enter a prompt here"}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isRecording}
          />

          {(text.trim() || stagedFiles.length > 0) ? (
              <button className="icon-btn send active" onClick={handleSend} title="Send">
                <Send size={20} />
              </button>
          ) : (
              <button 
                className={`icon-btn ${isRecording ? 'recording' : ''}`} 
                title={isRecording ? "Stop recording" : "Use microphone"} 
                onClick={toggleRecording}
                style={isRecording ? { color: 'red' } : {}}
              >
                {isRecording ? <Square size={20} fill="currentColor" /> : <Mic size={20} />}
              </button>
          )}
        </div>
      </div>
    </div>
  );
}
