import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Send, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

import logoImg from '../assets/logo.png';
import profileImg from '../assets/profile.png';

const ChatPage = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm ChatWilly. What would you like to know about William?" }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  const [bioExpanded, setBioExpanded] = useState(false);
  const [pressTimer, setPressTimer] = useState(null);
  const [resetProgress, setResetProgress] = useState(0);

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
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

    try {
      // 2. Use the dynamic API_BASE_URL here
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

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
            if (line.startsWith('data: ')) {
              const dataStr = line.substring(6).trim();
              if (dataStr === '[DONE]') break;

              try {
                const data = JSON.parse(dataStr);
                if (data.content) {
                  setMessages((prev) => {
                    const lastMsg = prev[prev.length - 1];
                    const updatedMsg = { ...lastMsg, content: lastMsg.content + data.content };
                    return [...prev.slice(0, -1), updatedMsg];
                  });
                }
              } catch (err) {
                console.error("Failed to parse SSE JSON:", err);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { role: 'assistant', content: "Sorry, I'm having trouble connecting right now." }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 flex flex-col h-full overflow-hidden relative">
      {/* Header */}
      <header className="flex justify-between items-center mb-10">
        <div className="flex items-center">
          {/* Full Logo replacing the circle and text */}
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
            {/* Background circle */}
            <div className="absolute inset-0 rounded-full bg-white border border-gray-200 shadow-sm" />

            {/* Progress ring */}
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

            {/* Icon */}
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

        {/* Mobile: compact header row */}
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

        {/* Mobile: expandable bio text */}
        {bioExpanded && (
          <p className="md:hidden text-gray-600 leading-relaxed text-sm mt-2">
            I'm <strong className="text-black">William</strong>. As I always say, I want to be a <em>Magician</em>. A magician who waves <em className="text-gray-400">dreams</em>, evokes <em className="text-gray-400">laughs</em> and inspires people to live their <em className="text-gray-400">best lives</em>.
          </p>
        )}

        {/* Desktop: original full layout */}
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
      <div className="flex-1 overflow-y-auto flex flex-col gap-6 w-full max-w-3xl mx-auto">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} w-full`}>

            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-[#F3D38D] border border-white shadow-sm flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                <span className="text-xs font-bold">CW</span>
              </div>
            )}

            <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} max-w-[85%]`}>
               <span className="text-xs font-bold uppercase mb-1 flex items-center gap-1 text-gray-500">
                  {msg.role === 'user' ? 'USER' : 'CHATWILLY'}
                  {msg.role === 'user' && <div className="w-5 h-5 rounded-full bg-[#FF5A5F] flex items-center justify-center text-white ml-1"><User size={12} /></div>}
               </span>

              <div className={`p-5 rounded-3xl text-[15px] leading-relaxed shadow-sm ${
                msg.role === 'user'
                  ? 'bg-white rounded-tr-sm border border-gray-100'
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
        ))}
        <div ref={messagesEndRef} />
        <div className="h-32 md:h-28 flex-shrink-0" />
      </div>

      {/* Input Area (Sticky Bottom) */}
      <div className="fixed bottom-0 left-0 w-full bg-gradient-to-t from-[#FCFAF6] via-[#FCFAF6] to-transparent pt-6 pb-5 px-4 z-50">
        <div className="max-w-2xl mx-auto flex flex-col items-center">
          <form onSubmit={handleSubmit} className="w-full relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about my projects, skills, or magic..."
              className="w-full bg-white border border-gray-200 rounded-full py-4 pl-6 pr-14 outline-none focus:ring-2 focus:ring-[#F3D38D] shadow-sm transition-all"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-500 rounded-full flex items-center justify-center transition-colors disabled:opacity-50"
            >
              <Send size={18} />
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
