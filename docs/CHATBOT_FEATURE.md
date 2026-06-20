# MedPredict Chatbot Feature

## Overview

The floating chatbot button provides users with an always-accessible conversation interface on authenticated pages. It offers a modern, animated chat experience with message history and timestamps.

## User Interface

### Floating Button
- **Location**: Bottom-right corner of the screen (fixed position)
- **Open State**: Blue circle with message icon
- **Closed State**: Red circle with X icon
- **Animation**: Smooth scale and color transition

### Chat Window
- **Size**: 384px wide × 500px tall
- **Styling**: Glass-morphism design with gradient header
- **Sections**:
  - Header: MedPredict Assistant title + tagline
  - Messages: Scrollable message history
  - Input: Text field + Send button
  - Timestamps: Each message shows send time

### Message Display
- **User Messages**: Right-aligned, blue background
- **Bot Messages**: Left-aligned, white background with border
- **Auto-scroll**: Window scrolls to latest message automatically

## Technical Implementation

### Files

```
frontend/src/
├── components/
│   ├── ChatbotButton.jsx      # Toggle button
│   ├── ChatbotWindow.jsx      # Chat window UI
│   └── Layout.jsx              # Integrated into main layout
├── store/
│   └── useChatbotStore.js     # State management
└── index.css                   # Animations & styling
```

### State Management (Zustand)

```javascript
// Store structure
{
  isOpen: boolean,              // Window visibility
  messages: [
    {
      id: number,
      type: 'user' | 'bot',
      text: string,
      timestamp: Date
    }
  ],
  
  // Actions
  toggleChatbot(): void,
  addMessage(text, type): void,
  clearMessages(): void
}
```

### Animations

- **Window Entrance**: `slideUp` animation (0.3s, cubic-bezier easing)
- **Button Toggle**: Scale change (0.3s transition)
- **Color Shift**: Blue ↔ Red (0.3s transition)

## Usage

### For Users
1. Click the blue message button in the bottom-right corner
2. Type your message and press Enter or click Send
3. Receive an instant bot response
4. View your conversation history with timestamps
5. Click the red X button to close the chat

### For Developers

#### Opening/Closing Programmatically
```javascript
import { useChatbotStore } from '@/store/useChatbotStore';

const MyComponent = () => {
  const toggleChatbot = useChatbotStore(state => state.toggleChatbot);
  return <button onClick={toggleChatbot}>Open Chat</button>;
};
```

#### Adding Messages Programmatically
```javascript
const addMessage = useChatbotStore(state => state.addMessage);
addMessage('Hello!', 'user');
addMessage('Hi there! How can I help?', 'bot');
```

#### Clearing Chat History
```javascript
const clearMessages = useChatbotStore(state => state.clearMessages);
clearMessages();
```

## Current Features

✅ Open/close toggle  
✅ Message history with timestamps  
✅ User and bot message differentiation  
✅ Auto-scrolling to latest message  
✅ Responsive design  
✅ Glass-morphism styling  
✅ Smooth animations  
✅ Zustand state persistence during session  

## Future Enhancements

### Backend Integration
- [ ] Create Django endpoint: `/api/chatbot/message/`
- [ ] Send user message to backend
- [ ] Receive AI-powered responses
- [ ] Optional: Stream responses for real-time feel

### Features to Add
- [ ] Chat history persistence (localStorage or backend)
- [ ] Clear chat button
- [ ] Typing indicator while bot responds
- [ ] Message reactions/emoji support
- [ ] File/image upload
- [ ] Mobile-optimized layout
- [ ] Dark mode support
- [ ] Notification badge for unread bot messages
- [ ] Integration with appointment scheduling
- [ ] Quick reply buttons for common queries

### Example Backend Integration
```javascript
// In ChatbotWindow.jsx handleSendMessage
const handleSendMessage = async (e) => {
  e.preventDefault();
  if (inputValue.trim()) {
    addMessage(inputValue, 'user');
    setInputValue('');
    
    try {
      const response = await api.post('/chatbot/message/', {
        message: inputValue
      });
      addMessage(response.data.reply, 'bot');
    } catch (error) {
      addMessage('Sorry, I couldn\'t process that. Please try again.', 'bot');
    }
  }
};
```

## Styling Customization

### Colors (from CSS Variables in `index.css`)
```css
--primary: #2563eb         /* Blue button when closed */
--danger: #f43f5e          /* Red button when open */
--text-main: #0f172a       /* Message text */
```

### Sizes
- Button diameter: 56px (p-4)
- Window width: 384px (w-96)
- Window height: 500px (h-[500px])
- Border radius: 16px (rounded-2xl)

### Breakpoints
Currently not mobile-responsive. To add mobile support:
```javascript
// In ChatbotWindow.jsx className
<div className="...w-96 md:w-80 sm:w-72...">
```

## Troubleshooting

**Button not appearing?**
- Check that Layout component imports ChatbotButton
- Verify z-index 50 is not being overridden
- Check browser console for errors

**Window not opening?**
- Ensure useChatbotStore is properly imported
- Check that toggleChatbot action is bound correctly
- Verify isOpen state is updating

**Styles not applying?**
- Verify index.css animations are loaded
- Check Tailwind config for class conflicts
- Clear browser cache (Ctrl+Shift+Delete)

**Hot reload not working?**
- Restart Vite dev server: `docker compose down && docker compose up -d`
- Check frontend container logs: `docker compose logs frontend -f`

## Performance Notes

- Store uses Zustand without persistence (session-only state)
- No heavy computations in message rendering
- Auto-scroll uses smooth behavior (minimal repaints)
- Message list grows unbounded (consider pagination for long chats)

## Accessibility

### Current
- Button has `title` attribute for tooltips
- Focus states use default browser styling
- Color contrast is WCAG AA compliant (blue/white, red/white)

### To Improve
- Add `aria-label` to button
- Add `role="dialog"` to window
- Keyboard navigation (Tab, Escape to close)
- Screen reader announcements for new messages
- ARIA live region for typing indicators
