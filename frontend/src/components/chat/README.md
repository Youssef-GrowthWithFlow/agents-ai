# Chat Component Architecture

Clean and maintainable folder structure for the chat interface.

## Structure

```
chat/
├── index.ts                      # Public exports
├── ChatInterface.tsx             # Main container component
├── ChatInterface.module.css      # Main styles
├── ChatHeader.tsx                # Header component
├── ChatInputForm.tsx             # Input form component
├── messages/                     # Message components
│   ├── index.ts
│   ├── UserMessage.tsx          # User message bubble
│   └── AgentMessage.tsx         # AI agent message bubble
└── hooks/                        # Custom hooks
    ├── index.ts
    └── useChatMessages.ts       # Message handling logic
```

## Design Principles

1. **Separation of Concerns**: UI components separated from business logic
2. **Clean Imports**: Index files for cleaner import statements
3. **Grouped by Feature**: Related components grouped in subfolders
4. **Single Responsibility**: Each file has one clear purpose

## Usage

```tsx
// Import from the main chat module
import { ChatInterface } from './components/chat';

// Or import specific pieces if needed
import { useChatMessages } from './components/chat/hooks';
import { UserMessage, AgentMessage } from './components/chat/messages';
```

## Adding New Features

- **New message type?** → Add to `messages/`
- **New business logic?** → Add to `hooks/`
- **New UI component?** → Add at root level alongside ChatHeader/ChatInputForm
