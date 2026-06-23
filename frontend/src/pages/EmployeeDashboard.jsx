/**
 * Employee Dashboard — filtered board (own tasks only) + submit actions.
 * Employee can: start jobs, submit for inspection.
 * Employee CANNOT: create tasks, confirm/reject, see other employees' tasks.
 */

import { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
import BoardColumn from '../components/BoardColumn';
import WorkloadView from '../components/WorkloadView';
import { useToast } from '../components/Toast';

const STAGES = ['todo', 'in_progress', 'submitted_for_review', 'done'];

export default function EmployeeDashboard() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('board'); // 'board' or 'workload'
  const showToast = useToast();

  const fetchTasks = useCallback(async () => {
    try {
      const res = await api.get('/api/tasks');
      setTasks(res.data);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  async function handleStart(taskId) {
    try {
      await api.post(`/api/tasks/${taskId}/start`);
      showToast('Job started — moved to In Progress.');
      fetchTasks();
    } catch (err) {
      console.error('Failed to start task:', err);
      showToast('Failed to start task.');
    }
  }

  async function handleSubmit(taskId) {
    try {
      await api.post(`/api/tasks/${taskId}/submit`);
      showToast('Submitted for inspection — awaiting manager review.');
      fetchTasks();
    } catch (err) {
      console.error('Failed to submit task:', err);
      showToast('Failed to submit task.');
    }
  }

  async function handleDropCard(taskId, fromStage, toStage) {
    if (fromStage === 'todo' && toStage === 'in_progress') {
      await handleStart(taskId);
    } else if (fromStage === 'in_progress' && toStage === 'submitted_for_review') {
      await handleSubmit(taskId);
    } else {
      showToast(`Cannot move task from '${fromStage}' to '${toStage}' directly.`);
    }
  }

  if (loading) {
    return (
      <div className="content">
        <div className="loading-screen" style={{ minHeight: '50vh' }}>
          <div className="spinner"></div>
          <div className="loading-text">Loading your work orders…</div>
        </div>
      </div>
    );
  }

  return (
    <div className="content">
      <div className="page-head">
        <div>
          <h2>My Work Orders</h2>
          <p>
            Jobs assigned to you. Submit finished work for inspection — your Manager
            signs off before it counts as done.
          </p>
        </div>
        <div className="view-toggle">
          <button
            className={`btn btn-sm ${viewMode === 'board' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setViewMode('board')}
          >
            Board View
          </button>
          <button
            className={`btn btn-sm ${viewMode === 'workload' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setViewMode('workload')}
            style={{ marginLeft: '8px' }}
          >
            Workload View
          </button>
        </div>
      </div>

      {viewMode === 'board' ? (
        <div className="board">
          {STAGES.map((stage) => (
            <BoardColumn
              key={stage}
              stage={stage}
              tasks={tasks.filter((t) => t.stage === stage)}
              userRole="employee"
              onStart={handleStart}
              onSubmit={handleSubmit}
              onDropCard={handleDropCard}
            />
          ))}
        </div>
      ) : (
        <WorkloadView
          tasks={tasks}
          userRole="employee"
          onStart={handleStart}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  );
}