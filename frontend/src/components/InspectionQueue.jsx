/**
 * Inspection Queue — Manager's "PR inbox" for tasks awaiting review.
 * Shows confirm/reject buttons with inline reject-feedback panel.
 * Enhanced with employee/complexity filters, details panel expansion,
 * revision history integration, and batch sign-off ("Confirm All").
 */

import React, { useState } from 'react';
import RejectPanel from './RejectPanel';

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
          tasks.map((task) => (
            <div className="queue-item" key={task.id}>
              <div className="qi-main">
                <div className="qi-title">{task.title}</div>
                <div className="qi-sub">
                  {task.id?.slice(-8)} · Submitted by {task.assigned_to_name || 'Unknown'} ·{' '}
                  Complexity <ComplexityDots level={task.complexity} />
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
              {openRejectId === task.id && (
                <RejectPanel
                  taskId={task.id}
                  onReject={(taskId, feedback) => {
                    onReject(taskId, feedback);
                    setOpenRejectId(null);
                  }}
                  onCancel={() => setOpenRejectId(null)}
                />
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}