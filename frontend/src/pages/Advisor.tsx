import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader } from 'lucide-react';
import { useFarm } from '../hooks/useFarm';
import { advisorApi } from '../api/client';
import type { AdvisoryResponse } from '../types';
import clsx from 'clsx';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  data?: AdvisoryResponse;
  loading?: boolean;
}

const QUICK_QUESTIONS = [
  'Should I irrigate my tomato crop today?',
  'What fertilizer should I apply at flowering stage?',
  'My tomato leaves have yellow spots — what disease is this?',
  'When should I harvest my tomatoes?',
  'How can I improve soil health?',
];

export default function Advisor() {
  const { farm, loadDemoFarm } = useFarm();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: "Hello! I'm AgriPulse AI, your personal farm advisor. Ask me anything about your crops, irrigation, fertilizers, or diseases. I'll consult our specialist agents and provide you with the best advice.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!farm) loadDemoFarm();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (query: string) => {
    if (!query.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
    };

    const loadingMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      loading: true,
    };

    setMessages(prev => [...prev, userMsg, loadingMsg]);
    setInput('');
    setLoading(true);

    try {
      const result = await advisorApi.ask(query, farm?.farm_id);
      setMessages(prev => prev.map(m =>
        m.id === loadingMsg.id
          ? { ...m, content: result.recommendation, data: result, loading: false }
          : m
      ));
    } catch (err) {
      setMessages(prev => prev.map(m =>
        m.id === loadingMsg.id
          ? {
              ...m,
              content: 'Sorry, I could not get a response from the AI. Please make sure the backend and Ollama are running.',
              loading: false,
            }
          : m
      ));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-7rem)]">
      {/* Header */}
      <div className="card p-4 mb-4 flex items-center gap-3">
        <div className="w-10 h-10 bg-forest-600 rounded-xl flex items-center justify-center">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
          <div className="font-bold text-gray-900">AgriPulse AI Advisor</div>
          <div className="text-xs text-gray-500">
            {farm ? `Farm: ${farm.crop_name} · ${farm.location}` : 'Powered by Ollama + Llama'}
          </div>
        </div>
        {farm && (
          <div className="ml-auto flex items-center gap-2 text-xs text-forest-600 font-medium">
            <span className="w-2 h-2 bg-forest-500 rounded-full animate-pulse"></span>
            4 Agents Ready
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={clsx('flex gap-3', msg.role === 'user' ? 'justify-end' : 'justify-start')}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 bg-forest-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <Bot className="w-4 h-4 text-forest-600" />
              </div>
            )}

            <div className={clsx(
              'max-w-[85%] rounded-2xl',
              msg.role === 'user'
                ? 'bg-forest-600 text-white px-4 py-3'
                : 'bg-white border border-gray-200 shadow-sm p-4'
            )}>
              {msg.loading ? (
                <div className="flex items-center gap-2 text-gray-500 py-1">
                  <Loader className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Consulting AI agents…</span>
                </div>
              ) : (
                <>
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </div>

                  {/* Agent metadata */}
                  {msg.data && (
                    <div className="mt-4 pt-3 border-t border-gray-100 space-y-2">
                      {/* Agents used */}
                      <div>
                        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                          Agents Consulted
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {msg.data.agents_used.map(a => (
                            <span key={a} className="text-xs bg-forest-50 text-forest-700 border border-forest-200 px-2 py-0.5 rounded-full">
                              ✓ {a}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>
                          <strong className="text-gray-700">Confidence:</strong>{' '}
                          <span className={clsx(
                            'font-medium',
                            msg.data.confidence === 'High' ? 'text-forest-600' :
                            msg.data.confidence === 'Medium' ? 'text-amber-600' : 'text-red-500'
                          )}>
                            {msg.data.confidence}
                          </span>
                        </span>
                        {msg.data.sources?.length > 0 && (
                          <span>
                            <strong className="text-gray-700">Source:</strong>{' '}
                            {msg.data.sources.slice(0, 2).join(', ')}
                          </span>
                        )}
                      </div>

                      <div className="text-xs text-gray-400">
                        🤖 {msg.data.provider}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <User className="w-4 h-4 text-gray-600" />
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Quick questions */}
      {messages.length <= 1 && (
        <div className="mb-3">
          <div className="text-xs text-gray-500 mb-2 font-medium">Quick questions:</div>
          <div className="flex flex-wrap gap-2">
            {QUICK_QUESTIONS.map(q => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                className="text-xs bg-forest-50 hover:bg-forest-100 text-forest-700 border border-forest-200 px-3 py-1.5 rounded-full transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about your farm... (irrigation, fertilizer, disease)"
          className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-forest-600 hover:bg-forest-700 disabled:opacity-50 text-white p-3 rounded-xl transition-colors"
        >
          {loading ? <Loader className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
        </button>
      </form>
    </div>
  );
}
