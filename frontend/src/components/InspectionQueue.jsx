/**
 * Inspection Queue — Manager's "PR inbox" for tasks awaiting review.
 * Shows confirm/reject buttons with inline reject-feedback panel.
 * Enhanced with employee/complexity filters, details panel expansion,
 * revision history integration, and batch sign-off ("Confirm All").
 */

import { useState, useEffect } from 'react';
import api from '../utils/api';

function ComplexityDots({ level }) {
  return (
    <span className="complexity-dots" style={{ display: 'inline' }}>
      {[1, 2, 3].map((i) => (
        <span key={i} className={i <= level ? 'filled' : 'empty'}>●</span>
      ))}
    </span>
  );
}

export default function InspectionQueue({ tasks, onConfirm, onReject }) {
  const [openRejectId, setOpenRejectId] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [employees, setEmployees] = useState([]);
  
  // Filter states
  const [filterEmployee, setFilterEmployee] = useState('all');
  const [filterComplexity, setFilterComplexity] = useState('all');
  
  // Expansion states
  const [expandedTaskId, setExpandedTaskId] = useState(null);
  const [revisions, setRevisions] = useState({}); // { taskId: Array of revisions }
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [confirmingAll, setConfirmingAll] = useState(false);

  // Fetch employees list for filtering
  useEffect(() => {
    api.get('/api/users/employees')
      .then((res) => {
        setEmployees(res.data);
      })
      .catch((err) => {
        console.error('Failed to fetch employees for review queue filters:', err);
      });
  }, []);

  function handleReject(taskId) {
    const feedback = rejectReason.trim() || 'Needs another pass before it can be signed off.';
    onReject(taskId, feedback);
    setOpenRejectId(null);
    setRejectReason('');
  }

  // Toggle detail expansion and fetch revision history
  const handleToggleExpand = async (taskId) => {
    if (expandedTaskId === taskId) {
      setExpandedTaskId(null);
    } else {
      setExpandedTaskId(taskId);
      if (!revisions[taskId]) {
        setLoadingHistory(true);
        try {
          const res = await api.get(`/api/tasks/${taskId}/history`);
          // Support both possible shapes of the API response
          const historyList = Array.isArray(res.data) 
            ? res.data 
            : (res.data.revisions || res.data.revision_history || []);
          setRevisions(prev => ({ ...prev, [taskId]: historyList }));
        } catch (err) {
          console.error(`Failed to fetch history for task ${taskId}:`, err);
          // Set to empty to avoid repeated failing calls
          setRevisions(prev => ({ ...prev, [taskId]: [] }));
        } finally {
          setLoadingHistory(false);
        }
      }
    }
  };

  // Confirm all filtered tasks
  const handleConfirmAll = async () => {
    const visibleTasks = filteredTasks;
    if (visibleTasks.length === 0) return;
    
    setConfirmingAll(true);
    try {
      await Promise.all(visibleTasks.map(task => onConfirm(task.id)));
    } catch (err) {
      console.error('Failed to confirm all filtered tasks:', err);
    } finally {
      setConfirmingAll(false);
    }
  };

  // Filter tasks client-side
  const filteredTasks = tasks.filter((task) => {
    const matchEmp = filterEmployee === 'all' || task.assigned_to === filterEmployee;
    const matchComp = filterComplexity === 'all' || task.complexity.toString() === filterComplexity;
    return matchEmp && matchComp;
  });

  return (
    <div className="queue-section">
      <div className="queue-section-head">
        <h3>Inspection Queue</h3>
        <span className="count-pill">{filteredTasks.length}</span>
      </div>

      {/* Filter Toolbar */}
      <div className="queue-filters">
        <div className="filter-group">
          <label htmlFor="qf-employee">Crew member:</label>
          <select
            id="qf-employee"
            value={filterEmployee}
            onChange={(e) => setFilterEmployee(e.target.value)}
          >
            <option value="all">All Crew</option>
            {employees.map((emp) => (
              <option key={emp.firebase_uid} value={emp.firebase_uid}>
                {emp.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="qf-complexity">Complexity:</label>
          <select
            id="qf-complexity"
            value={filterComplexity}
            onChange={(e) => setFilterComplexity(e.target.value)}
          >
            <option value="all">All Levels</option>
            <option value="1">Low</option>
            <option value="2">Medium</option>
            <option value="3">High</option>
          </select>
        </div>

        {filteredTasks.length > 1 && (
          <button
            className="btn btn-sm btn-stamp-approve confirm-all-btn"
            onClick={handleConfirmAll}
            disabled={confirmingAll}
          >
            {confirmingAll ? 'Signing Off...' : `Confirm All (${filteredTasks.length})`}
          </button>
        )}
      </div>

      <div className="queue-list">
        {filteredTasks.length === 0 ? (
          <div className="empty-queue">
            {tasks.length === 0 
              ? 'Nothing waiting on inspection right now.'
              : 'No tasks match the active filters.'}
          </div>
        ) : (
          filteredTasks.map((task) => {
            const isExpanded = expandedTaskId === task.id;
            return (
              <div className={`queue-item ${isExpanded ? 'is-expanded' : ''}`} key={task.id}>
                <div className="qi-main" onClick={() => handleToggleExpand(task.id)}>
                  <div className="qi-expansion-indicator">{isExpanded ? '▼' : '▶'}</div>
                  <div className="qi-info">
                    <div className="qi-title">{task.title}</div>
                    <div className="qi-sub">
                      {task.id?.slice(-8)} · Submitted by {task.assigned_to_name || 'Unknown'} ·{' '}
                      Complexity <ComplexityDots level={task.complexity} />
                    </div>
                  </div>
                </div>
                
                <div className="queue-actions">
                  <button
                    className="btn btn-sm btn-stamp-approve"
                    onClick={() => onConfirm(task.id)}
                  >
                    Confirm
                  </button>
                  <button
                    className="btn btn-sm btn-stamp-reject"
                    onClick={() =>
                      setOpenRejectId(openRejectId === task.id ? null : task.id)
                    }
                  >
                    Send Back
                  </button>
                </div>

                {/* Collapsible details panel */}
                {isExpanded && (
                  <div className="queue-detail-panel">
                    <div className="qd-section">
                      <h5>Work Order Description</h5>
                      <p className="qd-desc">{task.description || 'No description provided.'}</p>
                    </div>

                    <div className="qd-section">
                      <h5>Revision Log & Inspection Notes</h5>
                      {loadingHistory && !revisions[task.id] ? (
                        <div className="qd-loading">Loading history...</div>
                      ) : (!revisions[task.id] || revisions[task.id].length === 0) ? (
                        <div className="qd-empty-history">No past rejections on this work order.</div>
                      ) : (
                        <div className="revisions-timeline">
                          {revisions[task.id].map((rev, index) => (
                            <div key={index} className="revision-log-item">
                              <div className="rev-meta">
                                <span className="rev-num">Revision #{rev.revision_number || index + 1}</span>
                                <span className="rev-date">
                                  {rev.rejected_at ? new Date(rev.rejected_at).toLocaleString() : 'N/A'}
                                </span>
                              </div>
                              <p className="rev-feedback">"{rev.feedback}"</p>
                              <div className="rev-author">
                                <small>Rejected by: {rev.rejected_by || 'Manager'}</small>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {openRejectId === task.id && (
                  <div className="reject-panel">
                    <textarea
                      placeholder="What needs to be fixed before this can be signed off?"
                      value={rejectReason}
                      onChange={(e) => setRejectReason(e.target.value)}
                    />
                    <div className="reject-actions">
                      <button
                        className="btn btn-sm btn-stamp-reject"
                        onClick={() => handleReject(task.id)}
                      >
                        Confirm rejection
                      </button>
                      <button
                        className="btn btn-sm btn-ghost"
                        onClick={() => {
                          setOpenRejectId(null);
                          setRejectReason('');
                        }}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}