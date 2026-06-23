/**
 * Employee Dashboard — filtered board (own tasks only) + submit actions.
 * Employee can: start jobs, submit for inspection.
 * Employee CANNOT: create tasks, confirm/reject, see other employees' tasks.
 */

import React, { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
import BoardColumn from '../components/BoardColumn';
import { useToast } from '../components/Toast';

const STAGES = ['todo', 'in_progress', 'submitted_for_review', 'done'];

export default function EmployeeDashboard() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
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

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  async function handleStart(taskId) {
    try {
      await api.post(`/api/tasks/${taskId}/start`);
      showToast('Job started — moved to In Progress.');
      fetchTasks();
    } catch (err) {
      showToast('Failed to start task.');
    }
  }

  async function handleSubmit(taskId) {
    try {
      await api.post(`/api/tasks/${taskId}/submit`);
      showToast('Submitted for inspection — awaiting manager review.');
      fetchTasks();
    } catch (err) {
      showToast('Failed to submit task.');
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
      </div>

      <div className="board">
        {STAGES.map((stage) => (
          <BoardColumn
            key={stage}
            stage={stage}
            tasks={tasks.filter((t) => t.stage === stage)}
            userRole="employee"
            onStart={handleStart}
            onSubmit={handleSubmit}
          />
        ))}
      </div>
    </div>
  );
}