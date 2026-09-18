import React, { useState, useEffect } from 'react';
import { X, Loader2 } from 'lucide-react';
import { applicationsApi, resumesApi } from '../services/api';

export default function ApplicationModal({ isOpen, onClose, onSuccess, application = null }) {
  const [formData, setFormData] = useState({
    company_name: '',
    role_name: '',
    status: 'applied',
    ctc_amount: '',
    ctc_currency: 'INR',
    job_description_url: '',
    notes: '',
    resume_id: '',
  });

  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      setError(null);
      fetchResumes();

      if (application) {
        setFormData({
          company_name: application.company_name || '',
          role_name: application.role_name || '',
          status: application.status || 'applied',
          ctc_amount: application.ctc_amount !== null && application.ctc_amount !== undefined ? application.ctc_amount : '',
          ctc_currency: application.ctc_currency || 'INR',
          job_description_url: application.job_description_url || '',
          notes: application.notes || '',
          resume_id: application.resume_id || '',
        });
      } else {
        setFormData({
          company_name: '',
          role_name: '',
          status: 'applied',
          ctc_amount: '',
          ctc_currency: 'INR',
          job_description_url: '',
          notes: '',
          resume_id: '',
        });
      }
    }
  }, [isOpen, application]);

  const fetchResumes = async () => {
    try {
      const data = await resumesApi.list();
      setResumes(data);
    } catch (err) {
      console.error('Failed to load resumes for dropdown', err);
    }
  };

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const payload = {
      company_name: formData.company_name.trim(),
      role_name: formData.role_name.trim(),
      status: formData.status,
      ctc_amount: formData.ctc_amount !== '' ? parseFloat(formData.ctc_amount) : null,
      ctc_currency: formData.ctc_currency.trim() || 'INR',
      job_description_url: formData.job_description_url.trim() || null,
      notes: formData.notes.trim() || null,
      resume_id: formData.resume_id || null,
    };

    try {
      if (application) {
        await applicationsApi.update(application.application_id, payload);
      } else {
        await applicationsApi.create(payload);
      }
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to save application');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-800">
            {application ? 'Edit Application' : 'Log New Application'}
          </h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 rounded-lg p-1 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded-lg">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Company Name *
              </label>
              <input
                type="text"
                name="company_name"
                required
                value={formData.company_name}
                onChange={handleChange}
                placeholder="e.g. Google, Stripe"
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Role Name *
              </label>
              <input
                type="text"
                name="role_name"
                required
                value={formData.role_name}
                onChange={handleChange}
                placeholder="e.g. Senior Backend Engineer"
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Status
              </label>
              <select
                name="status"
                value={formData.status}
                onChange={handleChange}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white"
              >
                <option value="applied">Applied</option>
                <option value="oa">Online Assessment (OA)</option>
                <option value="interview">Interview</option>
                <option value="offer">Offer</option>
                <option value="rejected">Rejected</option>
                <option value="withdrawn">Withdrawn</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Attached Resume
              </label>
              <select
                name="resume_id"
                value={formData.resume_id}
                onChange={handleChange}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white"
              >
                <option value="">-- No resume attached --</option>
                {resumes.map((r) => (
                  <option key={r.resume_id} value={r.resume_id}>
                    {r.resume_name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="col-span-2">
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                CTC Amount
              </label>
              <input
                type="number"
                name="ctc_amount"
                step="0.01"
                min="0"
                value={formData.ctc_amount}
                onChange={handleChange}
                placeholder="e.g. 2400000"
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Currency
              </label>
              <input
                type="text"
                name="ctc_currency"
                maxLength="3"
                value={formData.ctc_currency}
                onChange={handleChange}
                placeholder="INR"
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none uppercase"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Job Description URL
            </label>
            <input
              type="url"
              name="job_description_url"
              value={formData.job_description_url}
              onChange={handleChange}
              placeholder="https://..."
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Notes
            </label>
            <textarea
              name="notes"
              rows="3"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Interview stages, contacts, referral notes, etc."
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          {/* Footer actions */}
          <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-colors disabled:opacity-50"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {application ? 'Save Changes' : 'Create Application'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
