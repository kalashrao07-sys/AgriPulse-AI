import axios from 'axios';
import type { FarmData, AdvisoryResponse, CropHealthResult, WeatherData, TimelineEvent, HealthStatus } from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || '';
const api = axios.create({ baseURL: BASE_URL });

export const farmApi = {
  loadDemo: async (): Promise<FarmData> => {
    const res = await api.get('/api/farm/demo');
    return res.data;
  },

  setup: async (data: {
    farmer_name: string;
    location: string;
    size_acres: number;
    crop_name: string;
    crop_age_days: number;
    soil_type: string;
    irrigation_method: string;
  }) => {
    const res = await api.post('/api/farm/setup', data);
    return res.data;
  },

  get: async (farmId: number): Promise<FarmData> => {
    const res = await api.get(`/api/farm/${farmId}`);
    return res.data;
  },
};

export const advisorApi = {
  ask: async (query: string, farmId?: number): Promise<AdvisoryResponse> => {
    const res = await api.post('/api/advisor/ask', {
      query,
      farm_id: farmId,
    });
    return res.data;
  },

  history: async (farmId: number) => {
    const res = await api.get(`/api/advisor/history/${farmId}`);
    return res.data;
  },
};

export const cropHealthApi = {
  analyze: async (formData: FormData): Promise<CropHealthResult> => {
    const res = await api.post('/api/crop-health/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};

export const weatherApi = {
  get: async (farmId: number): Promise<WeatherData> => {
    const res = await api.get(`/api/weather/${farmId}`);
    return res.data;
  },

  getDemo: async (): Promise<WeatherData> => {
    const res = await api.get('/api/weather/demo/current');
    return res.data;
  },
};

export const timelineApi = {
  get: async (farmId: number): Promise<TimelineEvent[]> => {
    const res = await api.get(`/api/timeline/${farmId}`);
    return res.data;
  },
};

export const healthApi = {
  check: async (): Promise<HealthStatus> => {
    const res = await api.get('/api/health');
    return res.data;
  },
};
