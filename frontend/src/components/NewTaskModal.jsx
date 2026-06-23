/**
 * New Work Order modal — Manager creates and assigns tasks.
 */

import React, { useState, useEffect } from 'react';
import api from '../utils/api';

export default function NewTaskModal({ isOpen, onClose, onCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [assignee, setAssignee] = useState('');
  const [complexity, setComplexity] = useState(2);
  const [employees, setEmployees] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      api.get('/api/users/employees').then((res) => {
        setEmployees(res.data);
        if (res.data.length > 0) setAssignee(res.data[0].firebase_uid);
      });
    }
  }, [isOpen]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim()) return;
    setSubmitting(true);

    try {
      await api.post('/api/tasks', {
        title: title.trim(),
        description: description.trim() || 'No description provided.',
        assigned_to: assignee,
        complexity: parseInt(complexity, 10),
      });
      setTitle('');
      setDescription('');
      setComplexity(2);
      onCreated?.();
      onClose();
    } catch (err) {
      console.error('Failed to create task:', err);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className={`modal-overlay ${isOpen ? 'open' : ''}`} onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>New work order</h3>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="nt-title">Title</label>
            <input
              id="nt-title"
              type="text"
              placeholder="e.g. Fix Nginx upstream config"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="nt-desc">Description</label>
            <input
              id="nt-desc"
              type="text"
              placeholder="What needs to happen"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="nt-assignee">Assign to</label>
            <select
              id="nt-assignee"
              value={assignee}
              onChange={(e) => setAssignee(e.target.value)}
            >
              {employees.map((emp) => (
                <option key={emp.firebase_uid} value={emp.firebase_uid}>
                  {emp.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="nt-complexity">Complexity</label>
            <select
              id="nt-complexity"
              value={complexity}
              onChange={(e) => setComplexity(e.target.value)}
            >
              <option value={1}>Low</option>
              <option value={2}>Medium</option>
              <option value={3}>High</option>
            </select>
          </div>
          <div className="modal-actions">
            <button
              type="submit"
              className="btn btn-primary"
              style={{ flex: 1 }}
              disabled={submitting}
            >
              {submitting ? 'Creating...' : 'Open work order'}
            </button>
            <button type="button" className="btn btn-ghost" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}