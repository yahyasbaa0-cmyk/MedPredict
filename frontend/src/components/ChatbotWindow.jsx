import { X, Send } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { useChatbotStore } from '../store/useChatbotStore';
import api from '../services/api';

export default function ChatbotWindow() {
  const { isOpen, messages, addMessage } = useChatbotStore();
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const textToSend = inputValue.trim();
    if (textToSend) {
      addMessage(textToSend, 'user');
      setInputValue('');
      setIsTyping(true);

      try {
        const historyData = messages.map(m => ({ type: m.type, text: m.text }));
        const res = await api.post('/auth/chatbot/', {
          message: textToSend,
          history: historyData
        });
        addMessage(res.data.reply, 'bot');
      } catch (err) {
        console.error(err);
        addMessage("Désolé, une erreur est survenue lors de la communication avec l'assistant.", 'bot');
      } finally {
        setIsTyping(false);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed bottom-24 right-8 w-96 h-[500px] rounded-2xl shadow-2xl flex flex-col z-50 animate-slideUp"
      style={{
        backgroundColor: 'var(--bg-card)',
        border: `1px solid var(--glass-border)`,
      }}
    >
      {/* Header */}
      <div 
        className="p-4 rounded-t-2xl flex justify-between items-center text-white"
        style={{
          background: `linear-gradient(to right, var(--primary), var(--secondary))`,
        }}
      >
        <div>
          <h3 className="font-semibold text-lg">MedPredict Assistant</h3>
          <p className="text-xs opacity-90">Always here to help</p>
        </div>
      </div>

      {/* Messages Container */}
      <div 
        className="flex-1 overflow-y-auto p-4 space-y-3"
        style={{
          backgroundColor: 'var(--bg-main)',
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.type === 'user'
                  ? 'rounded-br-none'
                  : 'rounded-bl-none'
              }`}
              style={{
                backgroundColor: msg.type === 'user' ? 'var(--primary)' : 'var(--bg-card)',
                color: msg.type === 'user' ? 'white' : 'var(--text-main)',
                border: msg.type === 'user' ? 'none' : `1px solid var(--glass-border)`,
              }}
            >
              <p className="text-sm">{msg.text}</p>
              <span 
                className="text-xs mt-1 block"
                style={{
                  color: msg.type === 'user' ? 'rgba(255, 255, 255, 0.7)' : 'var(--text-light)'
                }}
              >
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div 
              className="max-w-xs px-4 py-2 rounded-lg rounded-bl-none"
              style={{
                backgroundColor: 'var(--bg-card)',
                color: 'var(--text-main)',
                border: `1px solid var(--glass-border)`,
              }}
            >
              <div className="flex items-center gap-1.5 py-1">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }}></span>
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '150ms' }}></span>
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '300ms' }}></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form 
        onSubmit={handleSendMessage} 
        className="p-4 rounded-b-2xl"
        style={{
          borderTop: `1px solid var(--glass-border)`,
          backgroundColor: 'var(--bg-card)',
        }}
      >
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 rounded-lg focus:outline-none transition-all text-sm"
            style={{
              backgroundColor: 'var(--bg-main)',
              color: 'var(--text-main)',
              border: `1px solid var(--glass-border)`,
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--primary)';
              e.target.style.boxShadow = `0 0 0 3px var(--primary-light)`;
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--glass-border)';
              e.target.style.boxShadow = 'none';
            }}
          />
          <button
            type="submit"
            className="text-white px-4 py-2 rounded-lg transition-all hover:shadow-lg flex items-center gap-2"
            style={{
              backgroundColor: 'var(--primary)',
            }}
          >
            <Send size={16} />
          </button>
        </div>
      </form>
    </div>
  );
}
