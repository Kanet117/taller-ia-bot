import React, { useState, useEffect } from 'react';
import localforage from 'localforage';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import InputArea from './components/InputArea';
import { ttsConfig } from './config';

function App() {
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const loadChats = async () => {
      try {
        const savedChats = await localforage.getItem('bot9_chats');
        if (savedChats && savedChats.length > 0) {
          setChats(savedChats);
          setCurrentChatId(savedChats[0].id);
        } else {
          const initialChats = [{ id: 1, title: 'New Conversation', messages: [{ role: 'ai', text: 'Hello! I am your assistant. How can I help you today?' }] }];
          setChats(initialChats);
          setCurrentChatId(1);
          await localforage.setItem('bot9_chats', initialChats);
        }
      } catch (e) {
        console.error('Failed to load chats from localforage', e);
      } finally {
        setIsLoaded(true);
      }
    };
    loadChats();
  }, []);

  useEffect(() => {
    if (isLoaded) {
      localforage.setItem('bot9_chats', chats).catch(e => console.error('Failed to save chats', e));
    }
  }, [chats, isLoaded]);

  // Helper to get current chat messages
  const currentMessages = chats.find(c => c.id === currentChatId)?.messages || [];

  const handleNewChat = () => {
    const newId = chats.length > 0 ? Math.max(...chats.map(c => c.id)) + 1 : 1;
    setChats(prev => [...prev, { id: newId, title: 'New Conversation', messages: [{ role: 'ai', text: 'Hello! I am your assistant. How can I help you today?' }] }]);
    setCurrentChatId(newId);
  };

  const handleDeleteChat = (id, e) => {
    e.stopPropagation();
    const newChats = chats.filter(c => c.id !== id);
    setChats(newChats);
    if (currentChatId === id) {
      setCurrentChatId(newChats.length > 0 ? newChats[newChats.length - 1].id : null);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  }

  const fileToBase64 = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });

  const handleSendMessage = async (text, files, audioBlob) => {
    if (!text && (!files || files.length === 0) && !audioBlob) return;

    let mediaInfos = [];

    if (files && files.length > 0) {
      for (const file of files) {
        let mediaType = 'file';
        if (file.type.startsWith('image/')) mediaType = 'image';
        else if (file.type.startsWith('video/')) mediaType = 'video';
        else if (file.type.startsWith('audio/')) mediaType = 'audio';
        
        const base64Url = await fileToBase64(file);
        
        mediaInfos.push({
          mediaType,
          mediaContent: file.name,
          fileUrl: base64Url
        });
      }
    } else if (audioBlob) {
        const base64Url = await fileToBase64(audioBlob);
        mediaInfos.push({
          mediaType: 'audio',
          mediaContent: 'Audio Recording',
          fileUrl: base64Url
        });
    }

    const newUserMsg = { 
        role: 'user', 
        text: text,
        mediaInfos: mediaInfos
    };
    
    // Update messages for current chat
    setChats(prevChats => prevChats.map(chat => {
      if (chat.id === currentChatId) {
        // Optionally update title if it's "New Conversation"
        const newTitle = chat.title === 'New Conversation' && text ? text.substring(0, 20) + '...' : chat.title;
        return { ...chat, title: newTitle, messages: [...chat.messages, newUserMsg] };
      }
      return chat;
    }));

    try {
      setIsTyping(true);
      const formData = new FormData();
      if (text) {
        formData.append('text', text);
      }
      formData.append('voice', ttsConfig.voiceName || 'Aoede');

      const historyForBackend = currentMessages.map(msg => ({
        role: msg.role === 'ai' ? 'model' : 'user',
        parts: [msg.text].filter(Boolean)
      }));
      formData.append('history', JSON.stringify(historyForBackend));
      
      if (files && files.length > 0) {
        files.forEach(file => {
          formData.append('files', file);
        });
      } else if (audioBlob) {
        formData.append('files', audioBlob, 'audio.webm');
      }

      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      
      setChats(prevChats => prevChats.map(chat => {
        if (chat.id === currentChatId) {
          return { ...chat, messages: [...chat.messages, { role: 'ai', text: data.response, audioData: data.audio, generated_image: data.generated_image }] };
        }
        return chat;
      }));

    } catch (error) {
      console.error('Error sending message:', error);
      setChats(prevChats => prevChats.map(chat => {
        if (chat.id === currentChatId) {
          return { ...chat, messages: [...chat.messages, { role: 'ai', text: 'Sorry, there was an error communicating with the server.' }] };
        }
        return chat;
      }));
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar 
        isOpen={isSidebarOpen} 
        toggleSidebar={toggleSidebar} 
        handleNewChat={handleNewChat}
        chats={chats}
        currentChatId={currentChatId}
        setCurrentChatId={setCurrentChatId}
        handleDeleteChat={handleDeleteChat}
      />
      <main className="main-content">
        <ChatArea messages={currentMessages} isTyping={isTyping} />
        <InputArea onSendMessage={handleSendMessage} />
      </main>
    </div>
  );
}

export default App;
