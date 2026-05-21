import React from 'react';
import { Plus, Menu, MessageSquare, Settings, HelpCircle, History, Trash2 } from 'lucide-react';

export default function Sidebar({ isOpen, toggleSidebar, handleNewChat, chats, currentChatId, setCurrentChatId, handleDeleteChat }) {
  return (
    <aside className={`sidebar ${isOpen ? '' : 'closed'}`}>
      <div className="sidebar-header">
        <button className="menu-btn" onClick={toggleSidebar}>
          <Menu size={20} />
        </button>
      </div>

      <button className="btn-new-chat" onClick={handleNewChat}>
        <Plus size={18} /> New chat
      </button>

      <div className="history-list">
        <div className="history-section-title" style={{ padding: '16px 12px 8px', fontSize: '12px', fontWeight: '500', color: 'var(--text-secondary)' }}>
            Recent
        </div>
        {chats.map(chat => (
          <div 
            key={chat.id} 
            className={`history-item ${chat.id === currentChatId ? 'active' : ''}`}
            onClick={() => setCurrentChatId(chat.id)}
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
              <MessageSquare size={16} style={{ flexShrink: 0 }} /> 
              <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{chat.title}</span>
            </div>
            <button 
              className="delete-chat-btn" 
              onClick={(e) => handleDeleteChat(chat.id, e)}
              style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px' }}
              title="Delete chat"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>

      <div className="sidebar-footer" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '4px', marginTop: 'auto' }}>
        <div className="history-item">
            <HelpCircle size={18} /> Help
        </div>
        <div className="history-item">
            <History size={18} /> Activity
        </div>
        <div className="history-item">
            <Settings size={18} /> Settings
        </div>
      </div>
    </aside>
  );
}
