import { create } from 'zustand';

export const useChatbotStore = create((set) => ({
  isOpen: false,
  messages: [
    {
      id: 1,
      type: 'bot',
      text: "Hello! 👋 Welcome to MedPredict. How can I assist you today?",
      timestamp: new Date(),
    },
  ],

  toggleChatbot: () => set((state) => ({ isOpen: !state.isOpen })),
  
  addMessage: (message, type = 'user') =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: state.messages.length + 1,
          type,
          text: message,
          timestamp: new Date(),
        },
      ],
    })),

  clearMessages: () =>
    set({
      messages: [
        {
          id: 1,
          type: 'bot',
          text: "Hello! 👋 Welcome to MedPredict. How can I assist you today?",
          timestamp: new Date(),
        },
      ],
    }),
}));
