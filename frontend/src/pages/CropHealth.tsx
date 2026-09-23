import { useState, useEffect } from 'react';
import { Upload, Loader, AlertCircle } from 'lucide-react';
import { useFarm } from '../hooks/useFarm';
import { cropHealthApi } from '../api/client';
import type { CropHealthResult } from '../types';
import clsx from 'clsx';

export default function CropHealth() {
  const { farm, loadDemoFarm } = useFarm();
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [symptoms, setSymptoms] = useState('');
  const [result, setResult] = useState<CropHealthResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!farm) loadDemoFarm();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      if (image) formData.append('image', image);
      if (farm?.farm_id) formData.append('farm_id', farm.farm_id.toString());
      if (farm?.crop_name) formData.append('crop_name', farm.crop_name);
      if (symptoms) formData.append('symptoms', symptoms);

      const data = await cropHealthApi.analyze(formData);
      setResult(data);
    } catch {
      setError('Analysis failed. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'none': return 'text-forest-600 bg-forest-50 border-forest-200';
      case 'low': return 'text-amber-600 bg-amber-50 border-amber-200';
      case 'medium': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">🔬 Crop Health Analysis</h1>
        <p className="text-gray-500 mt-1">Upload a crop image or describe symptoms for AI-powered disease detection</p>
        {farm && (
          <div className="mt-2">
            <span className="badge-green">Crop: {farm.crop_name}</span>
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Upload panel */}
        <div className="card p-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Upload Crop Image</h2>

          {/* Drop zone */}
          <label className={clsx(
            'block border-2 border-dashed rounded-xl cursor-pointer transition-colors',
            preview ? 'border-forest-400 p-2' : 'border-gray-300 hover:border-forest-400 p-8 text-center'
          )}>
            {preview ? (
              <img src={preview} alt="Crop preview" className="w-full rounded-lg object-cover max-h-48" />
            ) : (
              <div>
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                <div className="text-sm font-medium text-gray-700">Click to upload or drag & drop</div>
                <div className="text-xs text-gray-500 mt-1">JPG, PNG up to 10MB</div>
              </div>
            )}
            <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
          </label>

          {preview && (
            <button onClick={() => { setImage(null); setPreview(null); setResult(null); }}
              className="text-xs text-red-500 hover:text-red-700">
              Remove image
            </button>
          )}

          {/* Symptoms */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Describe Symptoms (optional)
            </label>
            <textarea
              value={symptoms}
              onChange={e => setSymptoms(e.target.value)}
              placeholder="e.g., Yellow spots on lower leaves, brown edges..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none h-20 focus:outline-none focus:ring-2 focus:ring-forest-400"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading || (!image && !symptoms)}
            className="w-full btn-primary py-2.5 flex items-center justify-center gap-2"
          >
            {loading ? (
              <><Loader className="w-4 h-4 animate-spin" /> Analyzing…</>
            ) : (
              '🔍 Analyze Crop Health'
            )}
          </button>

          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              {error}
            </div>
          )}
        </div>

        {/* Results panel */}
        <div className="card p-6">
          {!result && !loading && (
            <div className="h-full flex flex-col items-center justify-center text-center py-8">
              <div className="text-5xl mb-4">🌿</div>
              <div className="text-gray-500 text-sm">
                Upload a crop image or describe symptoms to get AI-powered health analysis
              </div>
            </div>
          )}

          {loading && (
            <div className="h-full flex flex-col items-center justify-center py-8">
              <Loader className="w-8 h-8 text-forest-600 animate-spin mb-4" />
              <div className="text-sm text-gray-600">Analyzing crop health…</div>
            </div>
          )}

          {result && !loading && (
            <div className="space-y-4">
              {/* Demo notice */}
              {result.is_demo && (
                <div className="flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                  <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div className="text-xs text-amber-700">
                    <strong>⚠️ DEMO ANALYSIS</strong> — Not produced by a real vision model. For accurate diagnosis, use a trained plant disease model.
                  </div>
                </div>
              )}

              {/* Disease detected */}
              <div>
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Detection Result</div>
                <div className="text-lg font-bold text-gray-900">{result.disease_detected}</div>
                <div className="flex items-center gap-3 mt-1">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${getSeverityColor(result.severity)}`}>
                    Severity: {result.severity}
                  </span>
                  <span className="text-sm text-gray-500">
                    Confidence: {result.confidence_percent?.toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Confidence bar */}
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Confidence</span>
                  <span>{result.confidence_percent?.toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-forest-500 rounded-full"
                    style={{ width: `${result.confidence_percent || 0}%` }}
                  />
                </div>
              </div>

              {/* Details */}
              <div className="space-y-3">
                <div>
                  <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Symptoms</div>
                  <div className="text-sm text-gray-700">{result.symptoms}</div>
                </div>
                <div>
                  <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Recommended Treatment</div>
                  <div className="text-sm text-gray-700">{result.treatment}</div>
                </div>
                <div>
                  <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Prevention</div>
                  <div className="text-sm text-gray-700">{result.prevention}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
