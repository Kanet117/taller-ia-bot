import React, { useState, useEffect, useRef } from 'react';

export default function App() {
  const initialMessage = { 
    role: 'ai', 
    text: 'Sistema listo. Puedes escribir un mensaje o adjuntar una imagen para analizar.' 
  };
  const [messages, setMessages] = useState([initialMessage]);
  const [input, setInput] = useState('');
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleImage = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setImage(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleNuevoChat = async () => {
    try {
      await fetch("http://127.0.0.1:8001/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: "restart" }),
      });
    } catch (e) {
      console.error("Error al reiniciar chat en el servidor", e);
    }
    window.location.reload();
  };

  const processLogic = async () => {
    if (!input.trim() && !image) return;

    const currentInput = input;
    const currentImg = image;

    setMessages(prev => [...prev, { role: 'user', text: currentInput, img: currentImg }]);
    setLoading(true);
    setInput('');
    setImage(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          texto: currentInput || "Mira esta imagen", 
          imagen: currentImg 
        }),
      });

      if (!response.ok) {
        throw new Error("Error en la conexión con el servidor");
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, { role: "ai", text: data.respuesta, audio: data.audio }]);
    } catch (error) {
      console.error("Error al conectar:", error);
      setMessages(prev => [...prev, { role: "ai", text: "Hubo un error al conectar con el servidor." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.statusDot}></div>
          <h2 style={styles.headerTitle}>AI Assistant <span style={styles.version}>Multimodal</span></h2>
        </div>
        <button onClick={handleNuevoChat} style={styles.clearBtn}>Nuevo Chat</button>
      </header>

      <main style={styles.chatArea}>
        {messages.map((m, i) => (
          <div key={i} style={{ ...styles.messageRow, justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{ 
              ...styles.bubble, 
              backgroundColor: m.role === 'user' ? '#4f46e5' : '#1e293b',
              borderRadius: m.role === 'user' ? '18px 18px 2px 18px' : '18px 18px 18px 2px'
            }}>
              <p style={styles.roleLabel}>{m.role === 'user' ? 'Usuario' : 'IA'}</p>
              {m.img && <img src={m.img} style={styles.chatImg} alt="adjunto" />}
              <div style={styles.text}>{m.text}</div>
              {m.audio && (
                <audio controls src={m.audio} style={styles.audioPlayer} autoPlay />
              )}
            </div>
          </div>
        ))}
        {loading && <div style={styles.loadingText}>Procesando...</div>}
        <div ref={chatEndRef} />
      </main>

      <footer style={styles.footer}>
        {image && (
          <div style={styles.previewContainer}>
            <img src={image} style={styles.previewImg} alt="preview" />
            <button onClick={() => setImage(null)} style={styles.removeImg}>✕</button>
          </div>
        )}

        <div style={styles.inputWrapper}>
          <label style={styles.iconBtn}>
            📷
            <input type="file" style={{ display: 'none' }} onChange={handleImage} accept="image/*" />
          </label>
          
          <input 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            onKeyDown={(e) => e.key === 'Enter' && processLogic()}
            placeholder="Escribe o envía una imagen..."
            style={styles.input}
          />
          
          <button onClick={processLogic} disabled={loading} style={styles.sendBtn}>
            {loading ? '...' : 'Enviar'}
          </button>
        </div>
      </footer>
    </div>
  );
}

const styles = {
  container: { backgroundColor: '#0f172a', color: '#f1f5f9', height: '100vh', display: 'flex', flexDirection: 'column', fontFamily: 'sans-serif' },
  header: { padding: '16px 24px', background: '#1e293b', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  headerContent: { display: 'flex', alignItems: 'center', gap: '10px' },
  statusDot: { width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#22c55e' },
  headerTitle: { fontSize: '16px', margin: 0 },
  version: { fontSize: '10px', color: '#64748b' },
  clearBtn: { background: 'transparent', border: '1px solid #334155', color: '#94a3b8', padding: '5px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '11px' },
  chatArea: { flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' },
  messageRow: { display: 'flex', width: '100%' },
  bubble: { maxWidth: '75%', padding: '12px 16px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
  chatImg: { width: '100%', maxWidth: '300px', borderRadius: '10px', marginBottom: '8px', display: 'block' },
  audioPlayer: { width: '100%', marginTop: '10px', height: '40px', borderRadius: '8px' },
  roleLabel: { fontSize: '9px', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px', opacity: 0.5 },
  text: { fontSize: '15px', lineHeight: '1.5', whiteSpace: 'pre-wrap' },
  loadingText: { padding: '10px', fontSize: '12px', color: '#64748b', fontStyle: 'italic' },
  footer: { padding: '10px 20px 20px', background: '#0f172a' },
  previewContainer: { display: 'inline-flex', position: 'relative', marginBottom: '10px', padding: '5px', background: '#1e293b', borderRadius: '8px' },
  previewImg: { height: '50px', borderRadius: '4px' },
  removeImg: { position: 'absolute', top: '-5px', right: '-5px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '50%', width: '18px', height: '18px', cursor: 'pointer', fontSize: '10px' },
  inputWrapper: { maxWidth: '800px', margin: '0 auto', display: 'flex', gap: '8px', backgroundColor: '#1e293b', padding: '6px', borderRadius: '12px', border: '1px solid #334155' },
  iconBtn: { padding: '10px', cursor: 'pointer', fontSize: '18px', display: 'flex', alignItems: 'center' },
  input: { flex: 1, background: 'transparent', border: 'none', color: 'white', padding: '10px', outline: 'none' },
  sendBtn: { background: '#4f46e5', color: 'white', border: 'none', padding: '0 15px', borderRadius: '8px', cursor: 'pointer' },
};