import { useEffect, useState } from 'react';
import { Loader, AlertCircle } from 'lucide-react';
import { useFarm } from '../hooks/useFarm';
import { weatherApi } from '../api/client';
import type { WeatherData } from '../types';
import clsx from 'clsx';

export default function Weather() {
  const { farm, loadDemoFarm } = useFarm();
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!farm) {
      loadDemoFarm().then(() => fetchWeather());
    } else {
      fetchWeather();
    }
  }, [farm?.farm_id]);

  const fetchWeather = async () => {
    setLoading(true);
    try {
      const data = farm?.farm_id
        ? await weatherApi.get(farm.farm_id)
        : await weatherApi.getDemo();
      setWeather(data);
    } catch {
      // fallback demo
      const demo = await weatherApi.getDemo();
      setWeather(demo);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 text-forest-600 animate-spin" />
        <span className="ml-3 text-gray-600">Loading weather data…</span>
      </div>
    );
  }

  if (!weather) return null;

  const irr = weather.irrigation_recommendation;
  const irrColor = irr.color === 'red'
    ? 'bg-red-50 border-red-300 text-red-800'
    : irr.color === 'blue'
    ? 'bg-blue-50 border-blue-300 text-blue-800'
    : 'bg-amber-50 border-amber-300 text-amber-800';

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">🌤 Weather & Irrigation</h1>
          <p className="text-gray-500 mt-1">{farm?.location || 'Demo Location'}</p>
        </div>
        {weather.is_demo && (
          <span className="badge-amber">Demo Data</span>
        )}
      </div>

      {weather.demo_notice && (
        <div className="flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-700">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          {weather.demo_notice}
        </div>
      )}

      {/* Weather cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Temperature', value: `${weather.temperature_celsius}°C`, icon: '🌡', color: 'border-orange-400' },
          { label: 'Humidity', value: `${weather.humidity_percent}%`, icon: '💧', color: 'border-blue-400' },
          { label: 'Rain Probability', value: `${weather.rain_probability_percent}%`, icon: '🌧', color: 'border-indigo-400' },
          { label: 'Wind Speed', value: `${weather.wind_speed_kmh} km/h`, icon: '💨', color: 'border-gray-400' },
        ].map(card => (
          <div key={card.label} className={`card p-4 border-l-4 ${card.color}`}>
            <div className="text-2xl mb-2">{card.icon}</div>
            <div className="text-xl font-bold text-gray-900">{card.value}</div>
            <div className="text-xs text-gray-500 mt-0.5">{card.label}</div>
          </div>
        ))}
      </div>

      {/* Soil moisture */}
      <div className="card p-5">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-800">Soil Moisture</h3>
          <span className="text-lg font-bold text-gray-900">{weather.soil_moisture_percent}%</span>
        </div>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={clsx('h-full rounded-full transition-all', {
              'bg-red-500': weather.soil_moisture_percent < 35,
              'bg-amber-400': weather.soil_moisture_percent >= 35 && weather.soil_moisture_percent < 50,
              'bg-forest-500': weather.soil_moisture_percent >= 50 && weather.soil_moisture_percent <= 70,
              'bg-blue-500': weather.soil_moisture_percent > 70,
            })}
            style={{ width: `${weather.soil_moisture_percent}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Dry (0%)</span>
          <span>Optimal (50-70%)</span>
          <span>Saturated (100%)</span>
        </div>
      </div>

      {/* Irrigation recommendation */}
      <div className={`card p-6 border-2 ${irrColor}`}>
        <div className="flex items-center gap-3 mb-3">
          <span className="text-3xl">{irr.icon}</span>
          <div>
            <div className="text-sm font-medium opacity-75 uppercase tracking-wide">Irrigation Recommendation</div>
            <div className="text-2xl font-bold">{irr.decision}</div>
          </div>
        </div>
        <p className="text-sm opacity-80">{irr.reason}</p>
        <div className="mt-4 pt-4 border-t border-current border-opacity-20 grid grid-cols-2 gap-3 text-sm">
          <div>
            <div className="opacity-60 text-xs uppercase tracking-wide">Rain Probability</div>
            <div className="font-bold">{weather.rain_probability_percent}%</div>
          </div>
          <div>
            <div className="opacity-60 text-xs uppercase tracking-wide">Soil Moisture</div>
            <div className="font-bold">{weather.soil_moisture_percent}%</div>
          </div>
        </div>
      </div>

      {/* Weekly outlook */}
      <div className="card p-5">
        <h3 className="font-semibold text-gray-800 mb-4">7-Day Outlook (Demo)</h3>
        <div className="grid grid-cols-7 gap-2">
          {[
            { day: 'Mon', temp: 29, rain: 78, icon: '🌧' },
            { day: 'Tue', temp: 27, rain: 45, icon: '⛅' },
            { day: 'Wed', temp: 31, rain: 15, icon: '☀️' },
            { day: 'Thu', temp: 30, rain: 20, icon: '☀️' },
            { day: 'Fri', temp: 28, rain: 60, icon: '🌦' },
            { day: 'Sat', temp: 26, rain: 80, icon: '🌧' },
            { day: 'Sun', temp: 25, rain: 70, icon: '🌧' },
          ].map(d => (
            <div key={d.day} className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-xs text-gray-500 font-medium">{d.day}</div>
              <div className="text-lg my-1">{d.icon}</div>
              <div className="text-xs font-bold text-gray-800">{d.temp}°</div>
              <div className="text-xs text-blue-500">{d.rain}%</div>
            </div>
          ))}
        </div>
        <div className="text-xs text-gray-400 mt-2">* Demo data — live weather API not configured</div>
      </div>
    </div>
  );
}
