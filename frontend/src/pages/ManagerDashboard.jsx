/**
 * Manager Dashboard — full board + inspection queue + "New Work Order" button.
 * Manager sees ALL tasks across all employees.
 */

import React, { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
import BoardColumn from '../components/BoardColumn';
import InspectionQueue from '../components/InspectionQueue';
import NewTaskModal from '../components/NewTaskModal';
import { useToast } from '../components/Toast';

const STAGES = ['todo', 'in_progress', 'submitted_for_review', 'done'];

export default function ManagerDashboard() {
  const [tasks, setTasks] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
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

  const pendingInspection = tasks.filter((t) => t.stage === 'submitted_for_review');

  async function handleConfirm(taskId) {
    try {
      await api.post(`/api/tasks/${taskId}/review`, {
        action: 'confirm',
      });
      showToast('Task signed off and marked Done.');
      fetchTasks();
    } catch (err) {
      showToast('Failed to confirm task.');
    }
  }

  async function handleReject(taskId, feedback) {
    try {
      await api.post(`/api/tasks/${taskId}/review`, {
        action: 'reject',
        feedback,
      });
      showToast('Task sent back for revision.');
      fetchTasks();
    } catch (err) {
      showToast('Failed to reject task.');
    }
  }

  if (loading) {
    return (
      <div className="content">
        <div className="loading-screen" style={{ minHeight: '50vh' }}>
          <div className="spinner"></div>
          <div className="loading-text">Loading work orders…</div>
        </div>
      </div>
    );
  }

  return (
    <div className="content">
      <div className="page-head">
        <div>
          <h2>Job Board</h2>
          <p>Open new work orders, assign the crew, and inspect what comes back.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setModalOpen(true)}>
          + New Work Order
        </button>
      </div>

      <InspectionQueue
        tasks={pendingInspection}
        onConfirm={handleConfirm}
        onReject={handleReject}
      />

      <div className="board">
        {STAGES.map((stage) => (
          <BoardColumn
            key={stage}
            stage={stage}
            tasks={tasks.filter((t) => t.stage === stage)}
            userRole="manager"
          />
        ))}
      </div>

      <NewTaskModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreated={fetchTasks}
      />
    </div>
  );
}