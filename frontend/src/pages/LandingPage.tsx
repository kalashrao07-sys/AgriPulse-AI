import { useNavigate } from 'react-router-dom';
import { Sprout, ArrowRight, Leaf, CloudSun, Bug, Bot, BookOpen, ChevronRight } from 'lucide-react';
import { useFarm } from '../hooks/useFarm';

export default function LandingPage() {
  const navigate = useNavigate();
  const { loadDemoFarm, loading } = useFarm();

  const handleTryDemo = async () => {
    await loadDemoFarm();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white/95 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-forest-600 rounded-lg flex items-center justify-center">
              <Sprout className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-forest-800 text-lg">AgriSaarthi AI</span>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-gray-600">
            <a href="#features" className="hover:text-forest-700">Features</a>
            <a href="#how-it-works" className="hover:text-forest-700">How it works</a>
            <button
              onClick={handleTryDemo}
              disabled={loading}
              className="btn-primary flex items-center gap-2"
            >
              {loading ? 'Loading…' : 'Try Demo'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-16">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-forest-50 border border-forest-200 rounded-full text-forest-700 text-sm mb-6">
            <span className="w-2 h-2 bg-forest-500 rounded-full"></span>
            Hackathon Project — Problem Statement 14
          </div>
          <h1 className="text-5xl font-bold text-gray-900 leading-tight mb-6">
            Your Farm.<br />
            Your Data.<br />
            <span className="text-forest-600">Your AI Advisor.</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            AgriSaarthi combines crop knowledge, weather information, soil data and AI agents
            to provide personalized farming advice — powered by Ollama + Llama locally,
            and IBM watsonx.ai + Granite for deployment.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={handleTryDemo}
              disabled={loading}
              className="btn-primary text-base py-3 px-6 flex items-center justify-center gap-2"
            >
              {loading ? 'Loading Demo…' : '🚀 Load Demo Farm (Ramesh)'}
              {!loading && <ArrowRight className="w-5 h-5" />}
            </button>
            <button
              onClick={() => navigate('/advisor')}
              className="btn-secondary text-base py-3 px-6 flex items-center justify-center gap-2"
            >
              <Bot className="w-5 h-5" />
              Open AI Advisor
            </button>
          </div>
        </div>
      </section>

      {/* Architecture Diagram */}
      <section id="how-it-works" className="bg-forest-50 py-16">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">How AgriSaarthi Works</h2>
          <p className="text-gray-600 text-center mb-12">Multi-agent AI system routing your question to the right specialists</p>

          <div className="flex flex-col items-center gap-0 max-w-sm mx-auto">
            {/* Farmer */}
            <div className="bg-white border-2 border-forest-300 rounded-xl p-4 w-full text-center shadow-sm">
              <div className="text-3xl mb-1">👨‍🌾</div>
              <div className="font-semibold text-gray-800">Farmer</div>
              <div className="text-sm text-gray-500">Asks a question</div>
            </div>
            <div className="w-0.5 h-6 bg-forest-400"></div>
            <div className="text-forest-600 text-xs font-medium">Farm Profile</div>
            <div className="w-0.5 h-6 bg-forest-400"></div>

            {/* Supervisor */}
            <div className="bg-forest-700 border-2 border-forest-600 rounded-xl p-4 w-full text-center shadow-sm">
              <div className="text-3xl mb-1">🤖</div>
              <div className="font-semibold text-white">Farm Supervisor</div>
              <div className="text-sm text-forest-300">Routes to specialist agents</div>
            </div>
            <div className="w-0.5 h-6 bg-forest-400"></div>

            {/* Agents */}
            <div className="grid grid-cols-2 gap-3 w-full">
              {[
                { icon: '🌱', label: 'Crop Agent', desc: 'Fertilizer & Growth' },
                { icon: '🌦', label: 'Weather Agent', desc: 'Rain & Irrigation' },
                { icon: '🐛', label: 'Pest Agent', desc: 'Disease & Pests' },
                { icon: '📚', label: 'RAG Agent', desc: 'Knowledge Base' },
              ].map((a) => (
                <div key={a.label} className="bg-white border border-forest-200 rounded-lg p-3 text-center">
                  <div className="text-xl mb-0.5">{a.icon}</div>
                  <div className="text-xs font-semibold text-gray-800">{a.label}</div>
                  <div className="text-xs text-gray-500">{a.desc}</div>
                </div>
              ))}
            </div>
            <div className="w-0.5 h-6 bg-forest-400"></div>

            {/* AI */}
            <div className="bg-amber-50 border-2 border-amber-300 rounded-xl p-4 w-full text-center shadow-sm">
              <div className="text-3xl mb-1">⚡</div>
              <div className="font-semibold text-gray-800">Ollama + Llama</div>
              <div className="text-sm text-gray-500">→ IBM Granite (production)</div>
            </div>
            <div className="w-0.5 h-6 bg-forest-400"></div>

            {/* Result */}
            <div className="bg-forest-600 rounded-xl p-4 w-full text-center shadow-sm">
              <div className="text-3xl mb-1">✅</div>
              <div className="font-semibold text-white">Farm Action Plan</div>
              <div className="text-sm text-forest-200">Stored in PostgreSQL</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-16">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">What AgriSaarthi Does</h2>
          <p className="text-gray-600 text-center mb-12">Four specialized AI agents working together for your farm</p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: <Leaf className="w-6 h-6 text-forest-600" />,
                title: '🌱 Crop Advisory',
                desc: 'Growth stages, fertilizer schedules, harvesting guidance tailored to your crop.',
                color: 'bg-forest-50 border-forest-200',
              },
              {
                icon: <CloudSun className="w-6 h-6 text-blue-500" />,
                title: '🌦 Weather & Irrigation',
                desc: 'Real-time irrigation decisions based on rain probability and soil moisture.',
                color: 'bg-blue-50 border-blue-200',
              },
              {
                icon: <Bug className="w-6 h-6 text-red-500" />,
                title: '🐛 Pest & Disease',
                desc: 'Identify diseases from descriptions or images. Get treatment recommendations.',
                color: 'bg-red-50 border-red-200',
              },
              {
                icon: <BookOpen className="w-6 h-6 text-purple-500" />,
                title: '📚 RAG Knowledge',
                desc: 'Answers grounded in a real agricultural knowledge base using pgvector search.',
                color: 'bg-purple-50 border-purple-200',
              },
            ].map((f) => (
              <div key={f.title} className={`card p-6 border ${f.color}`}>
                <div className="mb-3">{f.icon}</div>
                <h3 className="font-bold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-600 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="bg-gray-50 py-12">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h3 className="text-lg font-semibold text-gray-700 mb-6">Technology Stack</h3>
          <div className="flex flex-wrap justify-center gap-3">
            {[
              'React + Vite', 'TypeScript', 'Tailwind CSS',
              'FastAPI', 'Python', 'PostgreSQL', 'pgvector',
              'Ollama + Llama', 'IBM Granite (ready)', 'Docker Compose',
            ].map((tech) => (
              <span key={tech} className="px-3 py-1.5 bg-white border border-gray-200 rounded-full text-sm text-gray-700 font-medium">
                {tech}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready for the Demo?</h2>
          <p className="text-gray-600 mb-8">Load the demo farm profile and ask your first farming question in under 30 seconds.</p>
          <button
            onClick={handleTryDemo}
            disabled={loading}
            className="btn-primary text-base py-3 px-8 inline-flex items-center gap-2"
          >
            {loading ? 'Setting up…' : '🌾 Load Demo Farm'}
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-6 text-center text-sm text-gray-500">
        <div className="flex items-center justify-center gap-2 mb-1">
          <Sprout className="w-4 h-4 text-forest-600" />
          <span className="font-medium text-forest-700">AgriSaarthi AI</span>
        </div>
        <p>Hackathon Project — Problem Statement 14 · AI Agent for Smart Farming Advice</p>
        <p className="mt-1">Built with Ollama + Llama · IBM watsonx.ai + Granite ready</p>
      </footer>
    </div>
  );
}
