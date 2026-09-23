import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sprout } from 'lucide-react';
import { useFarm } from '../hooks/useFarm';
import { farmApi } from '../api/client';

const DEMO = {
  farmer_name: 'Ramesh',
  location: 'Belagavi, Karnataka',
  size_acres: 2.4,
  crop_name: 'Tomato',
  crop_age_days: 45,
  soil_type: 'Loamy',
  irrigation_method: 'Drip',
};

export default function FarmSetup() {
  const navigate = useNavigate();
  const { loadDemoFarm, loading } = useFarm();
  const [form, setForm] = useState(DEMO);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDemo = async () => {
    await loadDemoFarm();
    navigate('/dashboard');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await farmApi.setup(form);
      await loadDemoFarm();
      navigate('/dashboard');
    } catch {
      setError('Failed to save farm. Check backend connection.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-forest-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-forest-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Sprout className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Farm Setup</h1>
          <p className="text-gray-600 mt-1">Tell us about your farm to get personalized advice</p>
        </div>

        {/* Demo button */}
        <button
          onClick={handleDemo}
          disabled={loading}
          className="w-full bg-forest-600 hover:bg-forest-700 text-white font-semibold py-3 px-4 rounded-xl mb-6 flex items-center justify-center gap-2 transition-colors"
        >
          <span className="text-lg">🚀</span>
          {loading ? 'Loading Demo…' : 'Load Demo Farm (Ramesh — Belagavi, Karnataka)'}
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="flex-1 h-px bg-gray-200"></div>
          <span className="text-sm text-gray-500">or fill manually</span>
          <div className="flex-1 h-px bg-gray-200"></div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">{error}</div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Farmer Name</label>
              <input
                type="text"
                value={form.farmer_name}
                onChange={e => setForm(f => ({ ...f, farmer_name: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input
                type="text"
                value={form.location}
                onChange={e => setForm(f => ({ ...f, location: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Farm Size (acres)</label>
              <input
                type="number"
                step="0.1"
                value={form.size_acres}
                onChange={e => setForm(f => ({ ...f, size_acres: parseFloat(e.target.value) }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Crop</label>
              <input
                type="text"
                value={form.crop_name}
                onChange={e => setForm(f => ({ ...f, crop_name: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Crop Age (days)</label>
              <input
                type="number"
                value={form.crop_age_days}
                onChange={e => setForm(f => ({ ...f, crop_age_days: parseInt(e.target.value) }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Soil Type</label>
              <select
                value={form.soil_type}
                onChange={e => setForm(f => ({ ...f, soil_type: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400"
              >
                {['Loamy', 'Sandy', 'Clay', 'Silty', 'Black', 'Red'].map(s => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Irrigation Method</label>
            <select
              value={form.irrigation_method}
              onChange={e => setForm(f => ({ ...f, irrigation_method: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400"
            >
              {['Drip', 'Sprinkler', 'Flood', 'Furrow', 'Canal'].map(s => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full btn-primary py-3 text-base"
          >
            {submitting ? 'Saving…' : 'Save Farm & Open Dashboard'}
          </button>
        </form>
      </div>
    </div>
  );
}
