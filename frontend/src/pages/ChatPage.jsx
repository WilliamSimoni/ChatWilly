import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Send, User, Brain, Square } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import logoImg from '../assets/logo.png';
import profileImg from '../assets/profile.png';

// ─── Tool name formatter ──────────────────────────────────────────────────────
const formatToolName = (name = '') =>
  name
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .replace(/^Search\s+/i, '');

// ─── ToolCallPill ─────────────────────────────────────────────────────────────
const TOOL_CALL_PHRASES = [
  'Extrapolating my memories from',
  'Digging through my brain for',
  'Let me think… pulling from',
  'Refreshing my memory via',
  'Consulting my inner archive:',
  'Hang on, checking my notes on',
  'Oh, I know this — fetching from',
  'Connecting the dots using',
  'Give me a sec, looking into',
  'Reaching deep into my memory:',
];

const getRandomPhrase = () =>
  TOOL_CALL_PHRASES[Math.floor(Math.random() * TOOL_CALL_PHRASES.length)];

// ─── ToolCallPill ─────────────────────────────────────────────────────────────
const ToolCallPill = ({ name }) => {
  const phraseRef = useRef(getRandomPhrase());

  return (
    <div className="flex justify-start w-full">
      <div className="flex items-center gap-2 py-1.5 px-3.5 rounded-full bg-white border border-gray-200 shadow-sm text-[12px] font-semibold text-gray-500 my-1 ml-11">
        <Brain size={12} className="text-[#F3D38D] flex-shrink-0" style={{ strokeWidth: 2.5 }} />
        <span>{phraseRef.current}</span>
        <span className="text-gray-700">{formatToolName(name)}</span>
      </div>
    </div>
  );
};

// ─── GuardrailBadge ───────────────────────────────────────────────────────────
const GuardrailBadge = () => (
  <span className="inline-flex items-center gap-1.5 text-[10px] font-bold tracking-widest uppercase text-amber-600 bg-amber-50 border border-amber-200 rounded-full px-2.5 py-0.5 mb-1.5">
    🪄 Out of my magic scope
  </span>
);

// ─── ChatPage ─────────────────────────────────────────────────────────────────
const ChatPage = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm ChatWilly. What would you like to know about William?" }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [bioExpanded, setBioExpanded] = useState(false);
  const [pressTimer, setPressTimer] = useState(null);
  const [resetProgress, setResetProgress] = useState(0);
  const [conversationId, setConversationId] = useState(null);
  const textareaRef = useRef(null);
  const abortControllerRef = useRef(null);

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handlePressStart = () => {
    const start = Date.now();
    const interval = setInterval(() => {
      const progress = Math.min((Date.now() - start) / 2000, 1);
      setResetProgress(progress);
      if (progress >= 1) {
        clearInterval(interval);
        setMessages([{ role: 'assistant', content: "Hi! I'm ChatWilly. What would you like to know about William?" }]);
        setConversationId(null);
        setResetProgress(0);
      }
    }, 16);
    setPressTimer(interval);
  };

  const handlePressEnd = () => {
    if (pressTimer) clearInterval(pressTimer);
    setPressTimer(null);
    setResetProgress(0);
  };

  const API_BASE_URL = import.meta.env.BACKEND_API_URL || 'http://localhost:8000';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = '56px';
    }
    setIsLoading(true);

    setMessages((prev) => [...prev, { role: 'assistant', content: '', isGuardrail: false }]);

    abortControllerRef.current = new AbortController();


    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: abortControllerRef.current.signal,
        body: JSON.stringify({
          message: { role: 'user', content: input },
          ...(conversationId && { conversation_id: conversationId }),
        }),
      });

      if (!response.ok) {
        const errorDetail = await response.json();
        console.error('Backend Validation Error:', errorDetail);
        throw new Error('Network response was not ok');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;

        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;

            const dataStr = line.substring(6).trim();

            let event;
            try {
              event = JSON.parse(dataStr);
            } catch {
              console.error('Failed to parse SSE JSON:', dataStr);
              continue;
            }

            const { type } = event;

            if (type === 'conversation_start') {
              setConversationId(event.conversation_id);
            }

            if (type === 'done') {
              done = true;
              break;
            }

            if (type === 'message_chunk') {
              setMessages((prev) => {
                const last = prev[prev.length - 1];
                return [
                  ...prev.slice(0, -1),
                  { ...last, content: last.content + event.content },
                ];
              });
            }

            if (type === 'guardrail_block') {
              setMessages((prev) => {
                const last = prev[prev.length - 1];
                return [
                  ...prev.slice(0, -1),
                  { ...last, content: event.content, isGuardrail: true },
                ];
              });
            }

            if (type === 'tool_call') {
              setMessages((prev) => {
                const last = prev[prev.length - 1];
                return [
                  ...prev.slice(0, -1),
                  { role: 'tool_call', toolName: event.name },
                  last,
                ];
              });
            }
          }
        }
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last.role === 'assistant' && last.content === '') {
            return prev.slice(0, -1);
          }
          return prev;
        });
      } else {
        console.error('Chat error:', error);
        setMessages((prev) => [
          ...prev.slice(0, -1),
          { role: 'assistant', content: "Sorry, I'm having trouble connecting right now." },
        ]);
      }
    } finally {
      abortControllerRef.current = null;
      setIsLoading(false);
    }
  };
  return (
    <div className="max-w-4xl mx-auto px-4 py-6 flex flex-col h-full overflow-hidden relative">
      {/* Header */}
      <header className="flex justify-between items-center mb-10">
        <div className="flex items-center">
          <img
            src={logoImg}
            alt="ChatWilly Logo"
            className="h-12 md:h-16 w-auto object-contain"
          />
        </div>
        <div className="flex items-center gap-3">
          <div
            className="relative cursor-pointer select-none w-9 h-9 flex items-center justify-center"
            onMouseDown={handlePressStart}
            onMouseUp={handlePressEnd}
            onMouseLeave={handlePressEnd}
            onTouchStart={handlePressStart}
            onTouchEnd={handlePressEnd}
            title="Hold to reset conversation"
          >
            <div className="absolute inset-0 rounded-full bg-white border border-gray-200 shadow-sm" />
            {resetProgress > 0 && (
              <svg className="absolute inset-0 w-full h-full -rotate-90">
                <circle
                  cx="50%" cy="50%" r="47%"
                  fill="none" stroke="#F3D38D" strokeWidth="3"
                  strokeDasharray={`${resetProgress * 100} 100`}
                  pathLength="100"
                  strokeLinecap="round"
                />
              </svg>
            )}
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="relative text-gray-400">
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
              <path d="M3 3v5h5"/>
            </svg>
          </div>
          <Link to="/about" className="text-sm font-semibold hover:underline">About William</Link>
        </div>
      </header>

      {/* Hero Card */}
      <div className="bg-white rounded-[2rem] p-6 md:p-10 shadow-sm flex flex-col md:flex-row gap-8 items-center md:items-start mb-10 border border-gray-100 relative">
        {/* Mobile */}
        <div className="flex md:hidden w-full items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 bg-[#F3D38D] border-2 border-white shadow-md">
              <img src={profileImg} alt="William Simoni" className="w-full h-full object-cover" />
            </div>
            <h1 className="text-xl font-extrabold tracking-tight">WILLIAM SIMONI</h1>
          </div>
          <button
            onClick={() => setBioExpanded(!bioExpanded)}
            className="text-xs font-semibold text-gray-400 underline ml-2 flex-shrink-0"
          >
            {bioExpanded ? 'Less' : 'More'}
          </button>
        </div>
        {bioExpanded && (
          <p className="md:hidden text-gray-600 leading-relaxed text-sm mt-2">
            I'm <strong className="text-black">William</strong>. As I always say, I want to be a <em>Magician</em>. A magician who waves <em className="text-gray-400">dreams</em>, evokes <em className="text-gray-400">laughs</em> and inspires people to live their <em className="text-gray-400">best lives</em>.
          </p>
        )}
        {/* Desktop */}
        <div className="hidden md:flex w-full gap-8 items-start">
          <div className="w-32 h-32 rounded-full overflow-hidden flex-shrink-0 bg-[#F3D38D] border-4 border-white shadow-md">
            <img src={profileImg} alt="William Simoni" className="w-full h-full object-cover" />
          </div>
          <div className="flex-1 text-left">
            <h1 className="text-4xl font-extrabold mb-4 tracking-tight">WILLIAM SIMONI</h1>
            <p className="text-gray-600 leading-relaxed text-sm md:text-base max-w-xl">
              I'm <strong className="text-black">William</strong>. As I always say, I want to be a <em className="italic">Magician</em>. A magician who waves <em className="italic text-gray-400">dreams</em>, evokes <em className="italic text-gray-400">laughs</em> and inspires people to live their <em className="italic text-gray-400">best lives</em>.
            </p>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-4 w-full max-w-3xl mx-auto">
        {messages.map((msg, idx) => {
          // ── Tool call pill ───────────────────────────────────────────────
          if (msg.role === 'tool_call') {
            return <ToolCallPill key={idx} name={msg.toolName} />;
          }

          // ── Regular chat bubble ──────────────────────────────────────────
          return (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} w-full`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-[#F3D38D] border border-white shadow-sm flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                  <span className="text-xs font-bold">CW</span>
                </div>
              )}
              <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} max-w-[85%]`}>
                <span className="text-xs font-bold uppercase mb-1 flex items-center gap-1 text-gray-500">
                  {msg.role === 'user' ? 'USER' : 'CHATWILLY'}
                  {msg.role === 'user' && (
                    <div className="w-5 h-5 rounded-full bg-[#FF5A5F] flex items-center justify-center text-white ml-1">
                      <User size={12} />
                    </div>
                  )}
                </span>

                {/* Guardrail badge shown above the bubble */}
                {msg.isGuardrail && <GuardrailBadge />}

                <div className={`p-5 rounded-3xl text-[15px] leading-relaxed shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-white rounded-tr-sm border border-gray-100'
                    : msg.isGuardrail
                      ? 'bg-amber-50 rounded-tl-sm border border-amber-100'
                      : 'bg-[#F3D38D] rounded-tl-sm'
                }`}>
                  {msg.content === '' && isLoading && idx === messages.length - 1 ? (
                    <span className="flex gap-1 items-center">
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:0ms]" />
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:150ms]" />
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:300ms]" />
                    </span>
                  ) : (
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                        strong: ({ children }) => <strong className="font-bold">{children}</strong>,
                        em: ({ children }) => <em className="italic">{children}</em>,
                        h3: ({ children }) => <h3 className="font-bold text-base mb-1 mt-2">{children}</h3>,
                        ul: ({ children }) => <ul className="list-disc ml-4 mb-2">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal ml-4 mb-2">{children}</ol>,
                        li: ({ children }) => <li className="mb-1">{children}</li>,
                        code: ({ children }) => <code className="bg-black/10 rounded px-1 text-sm font-mono">{children}</code>,
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
        <div className="h-32 md:h-28 flex-shrink-0" />
      </div>

      {/* Input Area */}
      <div className="fixed bottom-0 left-0 w-full bg-gradient-to-t from-[#FCFAF6] via-[#FCFAF6] to-transparent pt-6 pb-5 px-4 z-50">
        <div className="max-w-2xl mx-auto flex flex-col items-center">
          <form onSubmit={handleSubmit} className="w-full relative flex items-center">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px';
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                  e.preventDefault();
                  if (!isLoading && input.trim()) handleSubmit(e);
                }
              }}
              placeholder="Ask about my projects, skills, or magic..."
              rows={1}
              className="w-full bg-white border border-gray-200 rounded-[1.5rem] py-4 pl-6 pr-14 outline-none focus:ring-2 focus:ring-[#F3D38D] shadow-sm transition-all resize-none overflow-hidden leading-relaxed"
              disabled={false}
              style={{ minHeight: '56px', maxHeight: '160px' }}
            />
            <button
              type={isLoading ? 'button' : 'submit'}
              onClick={isLoading ? handleStop : undefined}
              disabled={!isLoading && !input.trim()}
              className="absolute right-2 bottom-2 w-10 h-10 bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-500 rounded-full flex items-center justify-center transition-colors disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <svg className="absolute inset-0 w-full h-full -rotate-90 animate-[spin_2s_linear_infinite]">
                    <circle
                      cx="50%" cy="50%" r="47%"
                      fill="none" stroke="#F3D38D" strokeWidth="3"
                      strokeDasharray="60 100"
                      pathLength="100"
                      strokeLinecap="round"
                    />
                  </svg>
                  <Square size={14} fill="currentColor" />
                </>
              ) : (
                <Send size={18} />
              )}
            </button>
          </form>
          <p className="text-[10px] font-bold tracking-[0.2em] text-gray-400 mt-4 uppercase">
            Software Engineer • Photographer • Video Maker • Thinker
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
