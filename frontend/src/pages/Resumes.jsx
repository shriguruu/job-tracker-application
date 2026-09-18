import React, { useState, useEffect } from 'react';
import {
  FileText,
  Upload,
  Download,
  Trash2,
  Calendar,
  AlertCircle,
  Loader2,
  ExternalLink,
} from 'lucide-react';
import { resumesApi } from '../services/api';
import ResumeModal from '../components/ResumeModal';
import ConfirmationModal from '../components/ConfirmationModal';

export default function Resumes() {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [downloadingId, setDownloadingId] = useState(null);

  const fetchResumes = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await resumesApi.list();
      setResumes(data);
    } catch (err) {
      setError(err.message || 'Failed to load resumes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleDownload = async (resume) => {
    try {
      setDownloadingId(resume.resume_id);
      const res = await resumesApi.getDownloadUrl(resume.resume_id);
      if (res.url) {
        window.open(res.url, '_blank', 'noopener,noreferrer');
      }
    } catch (err) {
      alert(err.message || 'Failed to generate download URL');
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    try {
      setDeleteLoading(true);
      await resumesApi.delete(deleteTarget.resume_id);
      setResumes((prev) => prev.filter((r) => r.resume_id !== deleteTarget.resume_id));
      setDeleteTarget(null);
    } catch (err) {
      alert(err.message || 'Failed to delete resume');
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Resume Manager</h1>
          <p className="text-sm text-slate-500 mt-1">
            Upload PDF resumes once and attach them across multiple applications
          </p>
        </div>
        <button
          onClick={() => setIsUploadModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-sm shadow-blue-500/20 transition-colors"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Resume</span>
        </button>
      </div>

      {/* Info Notice */}
      <div className="bg-blue-50/70 border border-blue-200/80 rounded-xl p-4 mb-6 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 shrink-0" />
        <div className="text-xs text-blue-800 leading-relaxed">
          <p className="font-semibold text-blue-900">Secure Pre-Signed Download Links</p>
          <p className="mt-0.5">
            Resumes are stored privately in cloud storage. When you click download, a temporary signed link valid for 5 minutes is generated on demand. Deleting a resume preserves your application history and unlinks gracefully.
          </p>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-slate-500">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-3" />
          <p className="text-sm">Loading your resumes...</p>
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-center text-rose-700 text-sm">
          {error}
        </div>
      ) : resumes.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center shadow-sm">
          <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-3">
            <FileText className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-slate-800">No resumes uploaded yet</h3>
          <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
            Upload your resumes in PDF format (up to 5MB) to easily attach them when tracking job applications.
          </p>
          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm"
          >
            <Upload className="w-3.5 h-3.5" />
            Upload your first resume
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resumes.map((resume) => (
            <div
              key={resume.resume_id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3">
                  <div className="w-10 h-10 rounded-lg bg-red-50 text-red-600 flex items-center justify-center shrink-0 border border-red-100">
                    <FileText className="w-5 h-5" />
                  </div>
                  <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600 uppercase tracking-wide">
                    PDF
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-slate-900 mt-3 truncate" title={resume.resume_name}>
                  {resume.resume_name}
                </h3>
                <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  Uploaded on {new Date(resume.created_at).toLocaleDateString()}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between gap-2">
                <button
                  onClick={() => handleDownload(resume)}
                  disabled={downloadingId === resume.resume_id}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors disabled:opacity-50"
                >
                  {downloadingId === resume.resume_id ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Download className="w-3.5 h-3.5" />
                  )}
                  <span>Download</span>
                </button>

                <button
                  onClick={() => setDeleteTarget(resume)}
                  className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                  title="Delete Resume"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      <ResumeModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onSuccess={fetchResumes}
      />

      {/* Delete Modal */}
      <ConfirmationModal
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        title="Delete Resume"
        message={`Are you sure you want to delete "${deleteTarget?.resume_name}"? Applications referencing this resume will keep their history but will have the resume unlinked.`}
        loading={deleteLoading}
      />
    </div>
  );
}
