import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, TrendingUp, Calendar, Check, BookOpen, AlertCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function StudyPlanner({ student }) {
  const [activeTab, setActiveTab] = useState('analysis'); // 'analysis' | 'schedule'

  // --- 🛡️ GUARD CLAUSE 1: COMPLETE NULL CHECK ---
  if (!student) {
    return (
      <div className="p-8 text-center border border-slate-200 rounded-xl bg-slate-50">
        <p className="text-slate-400 italic">Select a student to view their AI Study Plan.</p>
      </div>
    );
  }

  // --- 🛡️ GUARD CLAUSE 2: SAFE PROPERTY ACCESS ---
  // We use logical OR (||) to provide fallbacks if backend sends nulls
  const safeStudent = {
    study_hours: parseFloat(student.study_hours) || 0,
    name: student.name || "Student",
  };

  // --- MOCK LOGIC: TOPPER BENCHMARK ---
  const topperBenchmark = {
    avgHours: 8.5,
    distribution: [
      { subject: 'Core', hours: 4 },
      { subject: 'Labs', hours: 3 },
      { subject: 'Rev.', hours: 1.5 },
    ]
  };

  const gap = Math.max(0, topperBenchmark.avgHours - safeStudent.study_hours);

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm mt-6">
      {/* HEADER TABS */}
      <div className="flex border-b border-slate-100">
        <button
          onClick={() => setActiveTab('analysis')}
          className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
            activeTab === 'analysis' ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-600' : 'text-slate-500 hover:bg-slate-50'
          }`}
        >
          <TrendingUp className="w-4 h-4" /> Gap Analysis
        </button>
        <button
          onClick={() => setActiveTab('schedule')}
          className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
            activeTab === 'schedule' ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-600' : 'text-slate-500 hover:bg-slate-50'
          }`}
        >
          <Calendar className="w-4 h-4" /> AI Schedule
        </button>
      </div>

      <div className="p-6">
        {activeTab === 'analysis' && (
          <AnalysisView studentHours={safeStudent.study_hours} benchmark={topperBenchmark} gap={gap} />
        )}
        {activeTab === 'schedule' && (
          <ScheduleView gap={gap} />
        )}
      </div>
    </div>
  );
}

// --- SUB-VIEW: ANALYSIS ---
function AnalysisView({ studentHours, benchmark, gap }) {
  const data = [
    { name: 'You', hours: studentHours, fill: '#6366f1' }, // Indigo
    { name: 'Topper', hours: benchmark.avgHours, fill: '#10b981' }, // Emerald
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-4 bg-slate-50 p-4 rounded-lg border border-slate-100">
        <div className="p-2 bg-white rounded-full shadow-sm shrink-0">
          <AlertCircle className={`w-6 h-6 ${gap > 2 ? 'text-rose-500' : 'text-amber-500'}`} />
        </div>
        <div>
          <h4 className="font-bold text-slate-800 text-sm">Performance Gap Detected</h4>
          <p className="text-xs text-slate-600 mt-1 leading-relaxed">
            You are studying <strong>{gap.toFixed(1)} hours less</strong> than the class average. 
            Recommended increase: +1.5h/day.
          </p>
        </div>
      </div>

      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" barSize={32}>
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="name" width={60} tick={{fontSize: 12, fill: '#64748b'}} axisLine={false} tickLine={false} />
            <Tooltip cursor={{fill: 'transparent'}} />
            <Bar dataKey="hours" radius={[0, 4, 4, 0]} label={{ position: 'right', fill: '#64748b', fontSize: 12 }} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// --- SUB-VIEW: SCHEDULE ---
function ScheduleView({ gap }) {
  const [adopted, setAdopted] = useState(false);

  const slots = [
    { time: '18:00', label: 'Deep Work: Core Subject', type: 'core', duration: '1.5h' },
    { time: '19:30', label: 'Break (Topper Habit)', type: 'break', duration: '15m' },
    { time: '19:45', label: 'Revision & Notes', type: 'rev', duration: '1h' },
  ];

  if (gap > 3) {
    slots.push({ time: '20:45', label: 'Remedial: Video Recap', type: 'remedial', duration: '45m' });
  }

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        {slots.map((slot, i) => (
          <div key={i} className="flex items-center gap-4 group cursor-pointer">
            <div className="w-12 text-right text-xs text-slate-400 font-mono">{slot.time}</div>
            <div className={`flex-1 p-3 rounded-lg border flex justify-between items-center transition-all ${
              slot.type === 'break' ? 'bg-amber-50 border-amber-100 text-amber-800' : 
              slot.type === 'remedial' ? 'bg-rose-50 border-rose-100 text-rose-800' :
              'bg-white border-slate-200 shadow-sm'
            }`}>
              <div className="flex items-center gap-3">
                {slot.type === 'break' ? <Clock className="w-4 h-4 shrink-0"/> : <BookOpen className="w-4 h-4 shrink-0"/>}
                <span className="text-sm font-medium truncate">{slot.label}</span>
              </div>
              <span className="text-xs opacity-75 whitespace-nowrap ml-2">{slot.duration}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="pt-4 border-t border-slate-100">
        {!adopted ? (
          <button 
            onClick={() => setAdopted(true)}
            className="w-full py-3 bg-slate-900 text-white rounded-xl font-semibold hover:bg-slate-800 transition flex items-center justify-center gap-2 shadow-lg shadow-slate-200"
          >
            <Calendar className="w-4 h-4" /> Adopt This Schedule
          </button>
        ) : (
          <button disabled className="w-full py-3 bg-emerald-500 text-white rounded-xl font-semibold flex items-center justify-center gap-2 cursor-default">
            <Check className="w-5 h-5" /> Schedule Saved
          </button>
        )}
      </div>
    </div>
  );
}