import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sprout, CloudSun, Droplets, AlertTriangle, MessageSquare, Loader } from 'lucide-react';
import { useFarm } from '../hooks/useFarm';
import { healthApi } from '../api/client';
import type { HealthStatus } from '../types';
import clsx from 'clsx';

export default function Dashboard() {
  const { farm, loadDemoFarm, loading } = useFarm();
  const navigate = useNavigate();
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    healthApi.check().then(setHealth).catch(() => {});
  }, []);

  useEffect(() => {
    if (!farm) {
      loadDemoFarm();
    }
  }, []);

  const getRiskLevel = () => {
    if (!farm) return { level: 'Unknown', color: 'text-gray-500', bg: 'bg-gray-100' };
    const rain = farm.rain_probability;
    const moisture = farm.soil_moisture;
    if (rain > 70 || moisture > 75) return { level: 'Medium', color: 'text-amber-700', bg: 'bg-amber-100' };
    if (moisture < 35) return { level: 'High', color: 'text-red-700', bg: 'bg-red-100' };
    return { level: 'Low', color: 'text-forest-700', bg: 'bg-forest-100' };
  };

  const getTimeOfDay = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good Morning';
    if (h < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const getActionPlan = () => {
    if (!farm) return [];
    const plan = [];
    if (farm.rain_probability >= 60 || farm.soil_moisture >= 60) {
      plan.push({ icon: '💧', title: 'Delay irrigation', desc: `Rain is expected (${farm.rain_probability}%) and soil moisture is adequate (${farm.soil_moisture}%).`, type: 'info' });
    } else if (farm.soil_moisture < 40) {
      plan.push({ icon: '💧', title: 'Irrigate today', desc: `Soil moisture is low at ${farm.soil_moisture}%. Crop needs water.`, type: 'urgent' });
    }
    if (farm.crop_age_days >= 30 && farm.crop_age_days <= 70) {
      plan.push({ icon: '🐛', title: 'Inspect crop leaves', desc: 'Crop is in flowering/fruiting stage — check for pest and disease symptoms.', type: 'info' });
    }
    if (farm.rain_probability >= 70) {
      plan.push({ icon: '🌧', title: 'Check drainage', desc: 'Prepare the farm for expected rainfall. Ensure drainage channels are clear.', type: 'warning' });
    }
    if (farm.crop_age_days % 15 === 0) {
      plan.push({ icon: '🌱', title: 'Fertilizer check', desc: `${farm.crop_name} at ${farm.crop_age_days} days — verify NPK application schedule.`, type: 'info' });
    }
    if (plan.length === 0) {
      plan.push({ icon: '✅', title: 'All systems normal', desc: 'No urgent actions required today. Continue regular monitoring.', type: 'ok' });
    }
    return plan;
  };

  const risk = getRiskLevel();

  if (loading && !farm) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 text-forest-600 animate-spin" />
        <span className="ml-3 text-gray-600">Loading farm data…</span>
      </div>
    );
  }

  if (!farm) {
    return (
      <div className="text-center py-16">
        <Sprout className="w-16 h-16 text-forest-300 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-700 mb-2">No farm profile found</h2>
        <p className="text-gray-500 mb-6">Set up your farm to get personalized AI recommendations.</p>
        <button onClick={() => navigate('/setup')} className="btn-primary">
          Set Up Farm
        </button>
      </div>
    );
  }

  const actionPlan = getActionPlan();

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {getTimeOfDay()}, {farm.farmer_name} 👋
          </h1>
          <p className="text-gray-500 mt-1">{farm.location} · {farm.size_acres} acres · {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}</p>
        </div>
        {farm.is_demo_weather && (
          <span className="badge-amber text-xs">Demo Weather Data</span>
        )}
      </div>

      {/* Farm cards */}
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Your Farm Today</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Crop */}
          <div className="card p-4 border-l-4 border-forest-500">
            <div className="flex items-center gap-2 mb-2">
              <Sprout className="w-4 h-4 text-forest-600" />
              <span className="text-xs font-medium text-gray-500 uppercase">Crop</span>
            </div>
            <div className="text-xl font-bold text-gray-900">{farm.crop_name}</div>
            <div className="text-sm text-gray-500">{farm.crop_age_days} Days · {farm.growth_stage}</div>
          </div>

          {/* Weather */}
          <div className="card p-4 border-l-4 border-blue-400">
            <div className="flex items-center gap-2 mb-2">
              <CloudSun className="w-4 h-4 text-blue-500" />
              <span className="text-xs font-medium text-gray-500 uppercase">Weather</span>
            </div>
            <div className="text-xl font-bold text-gray-900">{farm.temperature}°C</div>
            <div className="text-sm text-gray-500">Rain: {farm.rain_probability}%</div>
          </div>

          {/* Soil */}
          <div className="card p-4 border-l-4 border-amber-400">
            <div className="flex items-center gap-2 mb-2">
              <Droplets className="w-4 h-4 text-amber-500" />
              <span className="text-xs font-medium text-gray-500 uppercase">Soil</span>
            </div>
            <div className="text-xl font-bold text-gray-900">{farm.soil_moisture}%</div>
            <div className="text-sm text-gray-500">Moisture · {farm.soil_type}</div>
          </div>

          {/* Risk */}
          <div className="card p-4 border-l-4 border-red-400">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4 text-red-500" />
              <span className="text-xs font-medium text-gray-500 uppercase">Risk</span>
            </div>
            <div className={`text-xl font-bold ${risk.color}`}>{risk.level}</div>
            <div className="text-sm text-gray-500">Overall risk level</div>
          </div>
        </div>
      </div>

      {/* Action plan + AI agents */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Action Plan */}
        <div className="lg:col-span-2 card p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">📋 Today's Farm Action Plan</h2>
          <div className="space-y-3">
            {actionPlan.map((item, i) => (
              <div
                key={i}
                className={clsx(
                  'flex items-start gap-3 p-3 rounded-lg border',
                  item.type === 'urgent' ? 'bg-red-50 border-red-200' :
                  item.type === 'warning' ? 'bg-amber-50 border-amber-200' :
                  item.type === 'ok' ? 'bg-forest-50 border-forest-200' :
                  'bg-blue-50 border-blue-200'
                )}
              >
                <span className="text-xl flex-shrink-0">{item.icon}</span>
                <div>
                  <div className="font-semibold text-gray-900 text-sm">{item.title}</div>
                  <div className="text-sm text-gray-600 mt-0.5">{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
          <button
            onClick={() => navigate('/advisor')}
            className="mt-4 btn-primary flex items-center gap-2 text-sm"
          >
            <MessageSquare className="w-4 h-4" />
            Ask AI Advisor for Details
          </button>
        </div>

        {/* AI Farm Team */}
        <div className="card p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">🤖 AI Farm Team</h2>
          <div className="space-y-3">
            {[
              { name: 'Crop Agent', icon: '🌱', key: 'crop_agent' },
              { name: 'Weather Agent', icon: '🌦', key: 'weather_agent' },
              { name: 'Pest/Disease Agent', icon: '🐛', key: 'pest_agent' },
              { name: 'RAG Agent', icon: '📚', key: 'rag_agent' },
            ].map((agent) => {
              const status = health?.agents[agent.key] || 'checking';
              const isReady = status === 'ready';
              return (
                <div key={agent.key} className="flex items-center gap-3 py-2 border-b border-gray-100 last:border-0">
                  <span className="text-lg">{agent.icon}</span>
                  <span className="flex-1 text-sm font-medium text-gray-800">{agent.name}</span>
                  {health ? (
                    isReady ? (
                      <span className="flex items-center gap-1 text-xs text-forest-600">
                        <span className="w-2 h-2 bg-forest-500 rounded-full"></span>
                        Ready
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs text-amber-600">
                        <span className="w-2 h-2 bg-amber-400 rounded-full"></span>
                        {status}
                      </span>
                    )
                  ) : (
                    <span className="w-4 h-4 border-2 border-forest-300 border-t-forest-600 rounded-full animate-spin"></span>
                  )}
                </div>
              );
            })}
          </div>

          {health && (
            <div className="mt-4 pt-4 border-t border-gray-100 space-y-1 text-xs text-gray-500">
              <div className="flex justify-between">
                <span>AI Provider</span>
                <span className="font-medium text-gray-700 truncate max-w-28 text-right">{health.config.ai_provider}</span>
              </div>
              <div className="flex justify-between">
                <span>AI Available</span>
                <span className={health.ai_available ? 'text-forest-600 font-medium' : 'text-red-500 font-medium'}>
                  {health.ai_available ? '✓ Yes' : '✗ No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>RAG Chunks</span>
                <span className="font-medium text-gray-700">{health.rag_chunks}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Ask AI', icon: '💬', to: '/advisor', color: 'bg-forest-600 text-white' },
          { label: 'Crop Health', icon: '🔬', to: '/crop-health', color: 'bg-blue-600 text-white' },
          { label: 'Weather', icon: '🌤', to: '/weather', color: 'bg-amber-500 text-white' },
          { label: 'Timeline', icon: '📅', to: '/timeline', color: 'bg-purple-600 text-white' },
        ].map(a => (
          <button
            key={a.to}
            onClick={() => navigate(a.to)}
            className={`${a.color} rounded-xl p-4 text-center hover:opacity-90 transition-opacity`}
          >
            <div className="text-2xl mb-1">{a.icon}</div>
            <div className="font-medium text-sm">{a.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
