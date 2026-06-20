import { MessageCircle, X } from 'lucide-react';
import { useChatbotStore } from '../store/useChatbotStore';

export default function ChatbotButton() {
  const { isOpen, toggleChatbot } = useChatbotStore();

  return (
    <button
      onClick={toggleChatbot}
      className="fixed bottom-8 right-8 p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 z-50 flex items-center justify-center text-white"
      style={{
        backgroundColor: isOpen ? 'var(--danger)' : 'var(--primary)',
        transform: isOpen ? 'scale(1.1)' : 'scale(1)',
      }}
      title={isOpen ? 'Close chat' : 'Open chat'}
      aria-label={isOpen ? 'Close chat' : 'Open chat'}
    >
      {isOpen ? (
        <X size={24} strokeWidth={2.5} />
      ) : (
        <MessageCircle size={24} strokeWidth={2.5} />
      )}
    </button>
  );
}
