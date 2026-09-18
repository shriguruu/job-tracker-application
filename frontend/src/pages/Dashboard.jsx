import React, { useState, useEffect, useMemo } from 'react';
import {
  Plus,
  Search,
  Filter,
  LayoutGrid,
  List,
  Building2,
  ExternalLink,
  Calendar,
  FileText,
  Edit2,
  Trash2,
  DollarSign,
  Briefcase,
  Award,
  CheckCircle2,
  Clock,
  ChevronRight,
  Loader2,
} from 'lucide-react';
import { applicationsApi, resumesApi } from '../services/api';
import StatusBadge, { STATUS_CONFIG } from '../components/StatusBadge';
import ApplicationModal from '../components/ApplicationModal';
import ConfirmationModal from '../components/ConfirmationModal';

export default function Dashboard() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters and view
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [viewMode, setViewMode] = useState('board'); // 'board' | 'table'

  // Modals state
  const [isAppModalOpen, setIsAppModalOpen] = useState(false);
  const [editingApp, setEditingApp] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [downloadingResumeId, setDownloadingResumeId] = useState(null);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = selectedStatus !== 'all' ? { status: selectedStatus } : {};
      const data = await applicationsApi.list(params);
      setApplications(data);
    } catch (err) {
      setError(err.message || 'Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [selectedStatus]);

  // Client-side search filter
  const filteredApps = useMemo(() => {
    if (!searchQuery.trim()) return applications;
    const q = searchQuery.toLowerCase();
    return applications.filter(
      (app) =>
        app.company_name.toLowerCase().includes(q) ||
        app.role_name.toLowerCase().includes(q) ||
        (app.notes && app.notes.toLowerCase().includes(q))
    );
  }, [applications, searchQuery]);

  // Statistics calculation
  const stats = useMemo(() => {
    const counts = {
      total: applications.length,
      applied: 0,
      oa: 0,
      interview: 0,
      offer: 0,
      rejected: 0,
      withdrawn: 0,
    };
    applications.forEach((app) => {
      if (counts[app.status] !== undefined) {
        counts[app.status] += 1;
      }
    });
    return counts;
  }, [applications]);

  const handleEdit = (app) => {
    setEditingApp(app);
    setIsAppModalOpen(true);
  };

  const handleOpenCreate = () => {
    setEditingApp(null);
    setIsAppModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    try {
      setDeleteLoading(true);
      await applicationsApi.delete(deleteTarget.application_id);
      setApplications((prev) => prev.filter((a) => a.application_id !== deleteTarget.application_id));
      setDeleteTarget(null);
    } catch (err) {
      alert(err.message || 'Failed to delete application');
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleDownloadResume = async (resumeId) => {
    if (!resumeId) return;
    try {
      setDownloadingResumeId(resumeId);
      const res = await resumesApi.getDownloadUrl(resumeId);
      if (res.url) {
        window.open(res.url, '_blank', 'noopener,noreferrer');
      }
    } catch (err) {
      alert(err.message || 'Failed to fetch download link for resume');
    } finally {
      setDownloadingResumeId(null);
    }
  };

  const handleQuickStatusChange = async (app, newStatus) => {
    try {
      const updated = await applicationsApi.update(app.application_id, { status: newStatus });
      setApplications((prev) =>
        prev.map((a) => (a.application_id === app.application_id ? updated : a))
      );
    } catch (err) {
      alert(err.message || 'Failed to update status');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Applications Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1">
            Track, filter, and advance your active job applications
          </p>
        </div>
        <button
          onClick={handleOpenCreate}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-sm shadow-blue-500/20 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Log Application</span>
        </button>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total</span>
          <p className="text-2xl font-bold text-slate-900 mt-1">{stats.total}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-blue-100 bg-blue-50/20 shadow-sm">
          <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">Applied</span>
          <p className="text-2xl font-bold text-blue-700 mt-1">{stats.applied}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-purple-100 bg-purple-50/20 shadow-sm">
          <span className="text-xs font-semibold text-purple-600 uppercase tracking-wider">OA</span>
          <p className="text-2xl font-bold text-purple-700 mt-1">{stats.oa}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-amber-100 bg-amber-50/20 shadow-sm">
          <span className="text-xs font-semibold text-amber-600 uppercase tracking-wider">Interview</span>
          <p className="text-2xl font-bold text-amber-700 mt-1">{stats.interview}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-emerald-100 bg-emerald-50/20 shadow-sm">
          <span className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Offers</span>
          <p className="text-2xl font-bold text-emerald-700 mt-1">{stats.offer}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-rose-100 bg-rose-50/20 shadow-sm">
          <span className="text-xs font-semibold text-rose-600 uppercase tracking-wider">Rejected</span>
          <p className="text-2xl font-bold text-rose-700 mt-1">{stats.rejected}</p>
        </div>
      </div>

      {/* Filter and View Controls Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by company or role..."
            className="w-full pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        {/* Status Filter and View Mode switch */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="text-xs font-medium text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="all">All Statuses</option>
              <option value="applied">Applied</option>
              <option value="oa">Online Assessment</option>
              <option value="interview">Interview</option>
              <option value="offer">Offer</option>
              <option value="rejected">Rejected</option>
              <option value="withdrawn">Withdrawn</option>
            </select>
          </div>

          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200">
            <button
              onClick={() => setViewMode('board')}
              title="Board View"
              className={`p-1.5 rounded-md text-xs font-medium transition-colors ${
                viewMode === 'board' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('table')}
              title="Table View"
              className={`p-1.5 rounded-md text-xs font-medium transition-colors ${
                viewMode === 'table' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-slate-500">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-3" />
          <p className="text-sm">Loading applications...</p>
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-center text-rose-700 text-sm">
          {error}
        </div>
      ) : filteredApps.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-3">
            <Briefcase className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-slate-800">No applications found</h3>
          <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
            {searchQuery
              ? 'No applications match your search query. Try clearing filters.'
              : 'You have not logged any applications yet. Click below to add your first one!'}
          </p>
          {!searchQuery && (
            <button
              onClick={handleOpenCreate}
              className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm"
            >
              <Plus className="w-3.5 h-3.5" />
              Log your first application
            </button>
          )}
        </div>
      ) : viewMode === 'board' ? (
        /* Board / Kanban View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {['applied', 'oa', 'interview', 'offer'].map((colStatus) => {
            const colApps = filteredApps.filter((a) => a.status === colStatus);
            const config = STATUS_CONFIG[colStatus];
            return (
              <div key={colStatus} className="flex flex-col bg-slate-100/70 rounded-xl p-3 border border-slate-200/80 min-h-[500px]">
                {/* Column header */}
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200 px-1">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${config.dot}`} />
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                      {config.label}
                    </h3>
                  </div>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-200 text-slate-600">
                    {colApps.length}
                  </span>
                </div>

                {/* Cards */}
                <div className="space-y-3 flex-1 overflow-y-auto">
                  {colApps.map((app) => (
                    <div
                      key={app.application_id}
                      className="bg-white rounded-lg p-4 border border-slate-200 shadow-xs hover:shadow-md transition-shadow group relative"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h4 className="font-semibold text-slate-900 text-sm">{app.company_name}</h4>
                          <p className="text-xs text-slate-600 font-medium mt-0.5">{app.role_name}</p>
                        </div>
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => handleEdit(app)}
                            className="p-1 text-slate-400 hover:text-blue-600 rounded hover:bg-slate-50"
                            title="Edit"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => setDeleteTarget(app)}
                            className="p-1 text-slate-400 hover:text-rose-600 rounded hover:bg-slate-50"
                            title="Delete"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>

                      {/* CTC Info */}
                      {app.ctc_amount && (
                        <div className="mt-2.5 flex items-center gap-1 text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-1 rounded w-fit">
                          <DollarSign className="w-3 h-3" />
                          <span>
                            {app.ctc_currency} {Number(app.ctc_amount).toLocaleString()}
                          </span>
                        </div>
                      )}

                      {/* Attached Resume */}
                      {app.resume_id && (
                        <div className="mt-2.5 flex items-center gap-1.5 text-xs text-slate-600">
                          <FileText className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                          <button
                            onClick={() => handleDownloadResume(app.resume_id)}
                            disabled={downloadingResumeId === app.resume_id}
                            className="truncate text-blue-600 hover:underline hover:text-blue-700 text-left"
                            title="Click to download resume"
                          >
                            {app.resume_name || 'Attached Resume'}
                          </button>
                        </div>
                      )}

                      {/* Job Link */}
                      {app.job_description_url && (
                        <div className="mt-2 flex items-center gap-1 text-xs text-slate-500">
                          <ExternalLink className="w-3 h-3 shrink-0" />
                          <a
                            href={app.job_description_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="truncate hover:text-blue-600 hover:underline"
                          >
                            View Job Description
                          </a>
                        </div>
                      )}

                      {/* Footer: Date & Quick Actions */}
                      <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(app.created_at).toLocaleDateString()}
                        </span>

                        {/* Quick next stage advance */}
                        {colStatus === 'applied' && (
                          <button
                            onClick={() => handleQuickStatusChange(app, 'oa')}
                            className="text-purple-600 hover:text-purple-800 font-medium flex items-center gap-0.5"
                          >
                            Advance to OA <ChevronRight className="w-3 h-3" />
                          </button>
                        )}
                        {colStatus === 'oa' && (
                          <button
                            onClick={() => handleQuickStatusChange(app, 'interview')}
                            className="text-amber-600 hover:text-amber-800 font-medium flex items-center gap-0.5"
                          >
                            Interview <ChevronRight className="w-3 h-3" />
                          </button>
                        )}
                        {colStatus === 'interview' && (
                          <button
                            onClick={() => handleQuickStatusChange(app, 'offer')}
                            className="text-emerald-600 hover:text-emerald-800 font-medium flex items-center gap-0.5"
                          >
                            Offer <ChevronRight className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                  {colApps.length === 0 && (
                    <div className="h-32 border-2 border-dashed border-slate-200 rounded-lg flex items-center justify-center text-xs text-slate-400">
                      Empty
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Table View */
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3.5">Company & Role</th>
                  <th className="px-6 py-3.5">Status</th>
                  <th className="px-6 py-3.5">Compensation</th>
                  <th className="px-6 py-3.5">Resume</th>
                  <th className="px-6 py-3.5">Date Added</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredApps.map((app) => (
                  <tr key={app.application_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-900">{app.company_name}</div>
                      <div className="text-xs text-slate-500 mt-0.5">{app.role_name}</div>
                      {app.job_description_url && (
                        <a
                          href={app.job_description_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-[11px] text-blue-600 hover:underline mt-1"
                        >
                          <ExternalLink className="w-3 h-3" /> Job Post
                        </a>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={app.status} />
                    </td>
                    <td className="px-6 py-4 text-xs font-medium text-slate-700">
                      {app.ctc_amount ? (
                        <span>
                          {app.ctc_currency} {Number(app.ctc_amount).toLocaleString()}
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {app.resume_id ? (
                        <button
                          onClick={() => handleDownloadResume(app.resume_id)}
                          disabled={downloadingResumeId === app.resume_id}
                          className="inline-flex items-center gap-1.5 text-blue-600 hover:underline hover:text-blue-700"
                        >
                          <FileText className="w-3.5 h-3.5 text-blue-500" />
                          <span className="truncate max-w-[150px]">{app.resume_name || 'Resume'}</span>
                        </button>
                      ) : (
                        <span className="text-slate-400">None attached</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">
                      {new Date(app.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button
                        onClick={() => handleEdit(app)}
                        className="p-1 text-slate-400 hover:text-blue-600 rounded transition-colors"
                        title="Edit"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteTarget(app)}
                        className="p-1 text-slate-400 hover:text-rose-600 rounded transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create / Edit Modal */}
      <ApplicationModal
        isOpen={isAppModalOpen}
        onClose={() => setIsAppModalOpen(false)}
        onSuccess={fetchApplications}
        application={editingApp}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        title="Delete Application"
        message={`Are you sure you want to delete the application for "${deleteTarget?.role_name}" at "${deleteTarget?.company_name}"? This action cannot be undone.`}
        loading={deleteLoading}
      />
    </div>
  );
}
