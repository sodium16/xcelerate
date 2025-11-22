import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload, Users, AlertTriangle, GraduationCap,
  Activity, X, Search, Award, CheckCircle2,
  BarChart3, Loader2, Building2, Stethoscope,
  Calculator, Briefcase, School, UserPlus,
  FileSpreadsheet, ArrowLeft, ArrowUpDown,
} from "lucide-react";

import StudyPlanner from "./components/StudyPlanner";


const API_BASE = "http://localhost:8000/api/v1";

// --- CONFIGURATION WITH DYNAMIC FIELDS ---
const DOMAINS = [
  {
    id: "engineering",
    label: "Engineering",
    icon: <Building2 className="w-8 h-8" />,
    color: "from-blue-500 to-indigo-600",
    desc: "B.Tech / B.E.",
    fields: [
      {
        name: "project_score",
        label: "Project Score (0-100)",
        placeholder: "85",
      },
      {
        name: "coding_skills",
        label: "Coding Rating (1-10)",
        placeholder: "7",
      },
    ],
  },
  {
    id: "med",
    label: "Medical",
    icon: <Stethoscope className="w-8 h-8" />,
    color: "from-emerald-400 to-teal-600",
    desc: "MBBS / BDS",
    fields: [
      {
        name: "clinical_score",
        label: "Clinical Rotation (0-100)",
        placeholder: "90",
      },
      {
        name: "hospital_hours",
        label: "Hospital Hours/Week",
        placeholder: "12",
      },
    ],
  },
  {
    id: "ca",
    label: "C.A.",
    icon: <Calculator className="w-8 h-8" />,
    color: "from-amber-400 to-orange-600",
    desc: "Chartered Accountancy",
    fields: [
      {
        name: "audit_hours",
        label: "Audit Hours Logged",
        placeholder: "20",
      },
      {
        name: "law_score",
        label: "Corporate Law Score",
        placeholder: "65",
      },
    ],
  },
  {
    id: "mba",
    label: "MBA",
    icon: <Briefcase className="w-8 h-8" />,
    color: "from-purple-500 to-pink-600",
    desc: "Business Admin",
    fields: [
      {
        name: "internship_score",
        label: "Internship Rating",
        placeholder: "8.5",
      },
      {
        name: "case_studies",
        label: "Case Studies Solved",
        placeholder: "15",
      },
    ],
  },
  {
    id: "school",
    label: "School",
    icon: <School className="w-8 h-8" />,
    color: "from-sky-400 to-cyan-600",
    desc: "K-12 Education",
    fields: [
      {
        name: "homework_rate",
        label: "Homework Completion %",
        placeholder: "95",
      },
      {
        name: "parent_meetings",
        label: "Parent Meetings Attended",
        placeholder: "4",
      },
    ],
  },
];

export default function App() {
  const [domain, setDomain] = useState(null);
  const [mode, setMode] = useState("single");
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ total: 0, risk: 0, aid: 0 });
  const [selectedStudent, setSelectedStudent] = useState(null);

  // --- SORTING STATE ---
  const [sortConfig, setSortConfig] = useState({
    key: "risk_score",
    direction: "desc",
  });

  const [formData, setFormData] = useState({
    name: "",
    id: "",
    attendance: "",
    cgpa: "",
    studyHours: "",
    failures: "0",
    income: "High",
    scholarship: "No",
  });

  const [customData, setCustomData] = useState({});

  useEffect(() => {
    setCustomData({});
  }, [domain]);

  const handleSinglePredict = async (e) => {
    e.preventDefault();
    setLoading(true);

    const baseHeaders =
      "student_id,name,attendance_rate,cgpa,study_hours_per_day,past_failures,family_income,scholarship";
    const baseValues = `${formData.id},${formData.name},${formData.attendance},${formData.cgpa},${formData.studyHours},${formData.failures},${formData.income},${formData.scholarship}`;

    const customFields = domain.fields || [];
    const customHeaders = customFields.map((f) => f.name).join(",");
    const customValStr = customFields
      .map((f) => customData[f.name] || "0")
      .join(",");

    const finalCsv = `${baseHeaders},${customHeaders}\n${baseValues},${customValStr}`;

    const blob = new Blob([finalCsv], { type: "text/csv" });
    const file = new File([blob], "single_entry.csv", { type: "text/csv" });

    await processFile(file);
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    await processFile(file);
  };

  const processFile = async (file) => {
    setLoading(true);
    const payload = new FormData();
    payload.append("file", file);

    try {
      await new Promise((r) => setTimeout(r, 1500));
      const res = await axios.post(`${API_BASE}/predict/${domain.id}`, payload);

      setStudents(res.data.data);
      setStats({
        total: res.data.total_students,
        risk: res.data.at_risk_count,
        aid: res.data.data.filter((s) => s.financial_flag).length,
      });

      if (mode === "single" && res.data.data.length > 0) {
        setSelectedStudent(res.data.data[0]);
      }
    } catch (err) {
      alert(`Error: ${err.response?.data?.detail || "Backend Offline"}`);
    } finally {
      setLoading(false);
    }
  };

  const triggerCall = async (studentId) => {
    try {
      await axios.post(`${API_BASE}/agent/call/${studentId}`);
      return true;
    } catch (e) {
      return false;
    }
  };

  // --- SORTING LOGIC ---
  const handleSort = (key) => {
    let direction = "asc";
    if (sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    setSortConfig({ key, direction });
  };

  const sortedStudents = [...students].sort((a, b) => {
    if (a[sortConfig.key] < b[sortConfig.key]) {
      return sortConfig.direction === "asc" ? -1 : 1;
    }
    if (a[sortConfig.key] > b[sortConfig.key]) {
      return sortConfig.direction === "asc" ? 1 : -1;
    }
    return 0;
  });

  // ---------- SCREEN 1: SELECT DOMAIN ----------
  if (!domain) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-indigo-600 rounded-full blur-[128px] opacity-30" />
        <div className="max-w-5xl w-full relative z-10">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 bg-slate-800/50 border border-slate-700 px-4 py-1.5 rounded-full text-indigo-400 text-sm font-medium mb-6 backdrop-blur-sm">
              <Activity className="w-4 h-4" /> EduPulse AI System v2.0
            </div>
            <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight mb-6">
              Select Your{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
                Domain
              </span>
            </h1>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {DOMAINS.map((d) => (
              <motion.button
                key={d.id}
                whileHover={{ y: -5 }}
                onClick={() => setDomain(d)}
                className="group relative bg-slate-800/50 hover:bg-slate-800 border border-slate-700 hover:border-indigo-500/50 p-6 rounded-2xl text-left transition-all overflow-hidden"
              >
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${d.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`}
                />
                <div className="mb-4 text-slate-300 group-hover:text-white transition-colors">
                  {d.icon}
                </div>
                <h3 className="text-white font-bold text-lg">{d.label}</h3>
                <p className="text-slate-500 text-xs mt-1 group-hover:text-slate-400">
                  {d.desc}
                </p>
              </motion.button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ---------- MAIN DASHBOARD ----------
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setDomain(null)}
              className="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-700 transition"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white">
                {domain.icon}
              </div>
              <div>
                <h1 className="font-bold text-lg leading-none text-slate-800">
                  EduPulse AI
                </h1>
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                  {domain.label} Module
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center bg-slate-100 p-1 rounded-lg">
            <button
              onClick={() => setMode("single")}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all flex items-center gap-2 ${
                mode === "single"
                  ? "bg-white shadow-sm text-indigo-700"
                  : "text-slate-500"
              }`}
            >
              <UserPlus className="w-4 h-4" /> Individual
            </button>
            <button
              onClick={() => setMode("batch")}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all flex items-center gap-2 ${
                mode === "batch"
                  ? "bg-white shadow-sm text-indigo-700"
                  : "text-slate-500"
              }`}
            >
              <FileSpreadsheet className="w-4 h-4" /> Batch Upload
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* LEFT COLUMN: FORM */}
          <div className="lg:col-span-1">
            <AnimatePresence mode="wait">
              {mode === "single" ? (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                    <h2 className="font-bold text-lg text-slate-800 mb-4">
                      Student Parameters
                    </h2>
                    <form
                      onSubmit={handleSinglePredict}
                      className="space-y-4"
                    >
                      <div className="grid grid-cols-2 gap-4">
                        <Input
                          label="Student ID"
                          value={formData.id}
                          onChange={(e) =>
                            setFormData({ ...formData, id: e.target.value })
                          }
                          placeholder="201"
                        />
                        <Input
                          label="Name"
                          value={formData.name}
                          onChange={(e) =>
                            setFormData({ ...formData, name: e.target.value })
                          }
                          placeholder="John Doe"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <Input
                          label="Attendance (%)"
                          type="number"
                          value={formData.attendance}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              attendance: e.target.value,
                            })
                          }
                          placeholder="85"
                        />
                        <Input
                          label="CGPA"
                          type="number"
                          value={formData.cgpa}
                          onChange={(e) =>
                            setFormData({ ...formData, cgpa: e.target.value })
                          }
                          placeholder="7.5"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <Input
                          label="Study Hours"
                          type="number"
                          value={formData.studyHours}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              studyHours: e.target.value,
                            })
                          }
                          placeholder="4"
                        />
                        <Input
                          label="Failures"
                          type="number"
                          value={formData.failures}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              failures: e.target.value,
                            })
                          }
                          placeholder="0"
                        />
                      </div>

                      {domain.fields && (
                        <div className="pt-4 border-t border-slate-100">
                          <div className="flex items-center gap-2 mb-3">
                            <span className="text-xs font-bold text-indigo-600 uppercase bg-indigo-50 px-2 py-1 rounded">
                              Specialization Data
                            </span>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            {domain.fields.map((field) => (
                              <Input
                                key={field.name}
                                label={field.label}
                                type="number"
                                value={customData[field.name] || ""}
                                onChange={(e) =>
                                  setCustomData({
                                    ...customData,
                                    [field.name]: e.target.value,
                                  })
                                }
                                placeholder={field.placeholder}
                              />
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="pt-2 border-t border-slate-100">
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                          Financial Profile
                        </label>
                        <div className="grid grid-cols-2 gap-4">
                          <select
                            className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
                            value={formData.income}
                            onChange={(e) =>
                              setFormData({
                                ...formData,
                                income: e.target.value,
                              })
                            }
                          >
                            <option value="High">High Income</option>
                            <option value="Low">Low Income</option>
                          </select>
                          <select
                            className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
                            value={formData.scholarship}
                            onChange={(e) =>
                              setFormData({
                                ...formData,
                                scholarship: e.target.value,
                              })
                            }
                          >
                            <option value="No">No Scholarship</option>
                            <option value="Yes">Has Scholarship</option>
                          </select>
                        </div>
                      </div>

                      <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all mt-4"
                      >
                        {loading ? (
                          <Loader2 className="animate-spin" />
                        ) : (
                          <Activity className="w-4 h-4" />
                        )}
                        Analyze Risk Factor
                      </button>
                    </form>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <div className="bg-white p-8 rounded-xl shadow-sm border-2 border-dashed border-slate-300 hover:border-indigo-500 transition-colors text-center cursor-pointer relative group">
                    <input
                      type="file"
                      onChange={handleUpload}
                      className="absolute inset-0 opacity-0 z-10 cursor-pointer"
                    />
                    <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                      <Upload className="w-8 h-8" />
                    </div>
                    <h3 className="font-bold text-slate-800">
                      Upload {domain.label} CSV
                    </h3>
                    <p className="text-sm text-slate-500 mt-2">
                      Drag & drop or click to browse
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* RIGHT COLUMN: RESULTS TABLE */}
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-3 gap-4">
              <StatCard
                title="Analyzed"
                value={stats.total}
                icon={<Users className="w-4 h-4" />}
                color="blue"
              />
              <StatCard
                title="High Risk"
                value={stats.risk}
                icon={<AlertTriangle className="w-4 h-4" />}
                color="red"
                pulse={stats.risk > 0}
              />
              <StatCard
                title="Needs Aid"
                value={stats.aid}
                icon={<GraduationCap className="w-4 h-4" />}
                color="amber"
              />
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 h-[600px] flex flex-col">
              <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center shrink-0 bg-white rounded-t-xl z-10">
                <h3 className="font-bold text-slate-800">Analysis Results</h3>
                <span className="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded">
                  {students.length} Records
                </span>
              </div>

              {students.length === 0 ? (
                <div className="flex flex-col items-center justify-center flex-1 text-slate-400">
                  <Search className="w-12 h-12 mb-4 opacity-20" />
                  <p>Enter student details or upload a file.</p>
                </div>
              ) : (
                <div className="overflow-y-auto flex-1">
                  <table className="w-full text-left">
                    <thead className="bg-slate-50 text-slate-500 text-xs uppercase sticky top-0 z-10 shadow-sm">
                      <tr>
                        <th
                          onClick={() => handleSort("name")}
                          className="px-6 py-3 cursor-pointer hover:bg-slate-100 transition-colors"
                        >
                          Student{" "}
                          <ArrowUpDown className="inline w-3 h-3 ml-1 text-slate-400" />
                        </th>
                        <th
                          onClick={() => handleSort("risk_score")}
                          className="px-6 py-3 cursor-pointer hover:bg-slate-100 transition-colors"
                        >
                          Risk Score{" "}
                          <ArrowUpDown className="inline w-3 h-3 ml-1 text-slate-400" />
                        </th>
                        <th
                          onClick={() => handleSort("risk_label")}
                          className="px-6 py-3 cursor-pointer hover:bg-slate-100 transition-colors"
                        >
                          Status{" "}
                          <ArrowUpDown className="inline w-3 h-3 ml-1 text-slate-400" />
                        </th>
                        <th className="px-6 py-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {sortedStudents.map((student) => (
                        <tr
                          key={student.student_id}
                          onClick={() => setSelectedStudent(student)}
                          className="hover:bg-slate-50 cursor-pointer transition-colors"
                        >
                          <td className="px-6 py-4">
                            <div className="font-medium text-slate-900">
                              {student.name}
                            </div>
                            <div className="text-xs text-slate-400">
                              {student.student_id}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden max-w-[100px]">
                                <div
                                  className={`h-full transition-all duration-500 ${
                                    student.risk_score > 75
                                      ? "bg-rose-500"
                                      : student.risk_score > 40
                                      ? "bg-amber-500"
                                      : "bg-emerald-500"
                                  }`}
                                  style={{ width: `${student.risk_score}%` }}
                                />
                              </div>
                              <span className="text-xs font-bold text-slate-700">
                                {student.risk_score}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <Badge status={student.risk_label} />
                          </td>
                          <td className="px-6 py-4 text-right">
                            <CallButton
                              id={student.student_id}
                              triggerCall={triggerCall}
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>

        <AnimatePresence>
          {selectedStudent && (
            <StudentModal
              student={selectedStudent}
              onClose={() => setSelectedStudent(null)}
            />
          )}
        </AnimatePresence>
      </main>

    </div>
  );
}

/* --------- SMALL HELPER COMPONENTS (unchanged) ---------- */

function Input({ label, ...props }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">
        {label}
      </label>
      <input
        {...props}
        className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
      />
    </div>
  );
}

function StatCard({ title, value, icon, color, pulse }) {
  const colors = {
    blue: "bg-blue-50 text-blue-600",
    red: "bg-rose-50 text-rose-600",
    amber: "bg-amber-50 text-amber-600",
  };
  return (
    <div className="bg-white p-4 rounded-xl border border-slate-200 flex items-center gap-3 shadow-sm">
      <div
        className={`w-10 h-10 rounded-lg flex items-center justify-center ${
          colors[color]
        } ${pulse ? "animate-pulse" : ""}`}
      >
        {icon}
      </div>
      <div>
        <div className="text-2xl font-bold text-slate-800 leading-none">
          {value}
        </div>
        <div className="text-xs text-slate-500 font-medium mt-1">{title}</div>
      </div>
    </div>
  );
}

function Badge({ status }) {
  const styles = {
    "High Risk": "bg-rose-100 text-rose-700 border-rose-200",
    Moderate: "bg-amber-100 text-amber-800 border-amber-200",
    Safe: "bg-emerald-100 text-emerald-700 border-emerald-200",
  };
  return (
    <span
      className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wide border ${
        styles[status] || styles["Safe"]
      }`}
    >
      {status}
    </span>
  );
}

function CallButton({ id, triggerCall }) {
  const [state, setState] = useState("idle");
  const handleClick = async (e) => {
    e.stopPropagation();
    setState("loading");
    await triggerCall(id);
    setState("active");
  };
  if (state === "loading")
    return (
      <button disabled className="text-slate-400">
        <Loader2 className="w-4 h-4 animate-spin" />
      </button>
    );
  if (state === "active")
    return (
      <button
        disabled
        className="bg-rose-50 text-rose-600 px-3 py-1 rounded text-xs font-bold animate-pulse"
      >
        Calling...
      </button>
    );
  return (
    <button
      onClick={handleClick}
      className="bg-indigo-50 hover:bg-indigo-100 text-indigo-600 px-3 py-1 rounded text-xs font-bold transition-colors"
    >
      Call
    </button>
  );
}

function StudentModal({ student, onClose }) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-white w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto"
      >
        <div className="p-6 border-b border-slate-100 flex justify-between items-start bg-slate-50/50">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              {student.name}
            </h2>
            <p className="text-sm text-slate-500">
              ID: {student.student_id}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-slate-200 rounded-full transition"
          >
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>
        <div className="p-6 space-y-6">
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex justify-between items-center">
            <div>
              <div className="text-sm font-medium text-slate-500">
                Risk Score
              </div>
              <div className="text-3xl font-bold text-indigo-600">
                {student.risk_score}/100
              </div>
            </div>
            <div className="text-right">
              <Badge status={student.risk_label} />
              <div className="text-xs text-slate-400 mt-1">
                Factor: {student.top_risk_factor}
              </div>
            </div>
          </div>
          <StudyPlanner student={student} />
          <div>
            <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Award className="w-4 h-4 text-indigo-500" /> Achievements
            </h3>
            <div className="grid grid-cols-3 gap-3">
              <Achievement
                icon={<CheckCircle2 className="w-5 h-5" />}
                label="Guardian"
                desc="90%+ Att."
                active={student.attendance > 90}
              />
              <Achievement
                icon={<BarChart3 className="w-5 h-5" />}
                label="Scholar"
                desc="9.0+ CGPA"
                active={student.cgpa > 9.0}
              />
              <Achievement
                icon={<Users className="w-5 h-5" />}
                label="Social"
                desc="Active Clubs"
                active={student.top_risk_factor === "None"}
              />
            </div>
          </div>
          {student.financial_flag && (
            <div className="bg-amber-50 border border-amber-100 p-3 rounded-lg flex gap-3 items-start">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <div className="font-bold text-amber-800 text-sm">
                  Financial Aid Recommended
                </div>
                <div className="text-xs text-amber-600 mt-1">
                  Student matches criteria for low-income support. Scholarship
                  application triggered.
                </div>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}

function Achievement({ icon, label, desc, active }) {
  return (
    <div
      className={`p-3 rounded-xl border text-center ${
        active
          ? "bg-indigo-50 border-indigo-100 text-indigo-700"
          : "bg-slate-50 border-slate-100 text-slate-400 grayscale"
      }`}
    >
      <div className="mx-auto w-8 h-8 mb-2 flex items-center justify-center bg-white rounded-full shadow-sm">
        {icon}
      </div>
      <div className="font-bold text-xs mb-0.5">{label}</div>
      <div className="text-[10px] opacity-75">{desc}</div>
    </div>
  );
}
