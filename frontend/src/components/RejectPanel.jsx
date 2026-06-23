/**
 * Reject Panel — inline feedback form for rejecting a task submission.
 * Extracted as a reusable component.
 */

import { useState } from 'react';

export default function RejectPanel({ taskId, onReject, onCancel }) {
  const [reason, setReason] = useState('');

  function handleSubmit() {
    const feedback = reason.trim() || 'Needs another pass before it can be signed off.';
    onReject(taskId, feedback);
    setReason('');
  }

  return (
    <div className="reject-panel">
      <textarea
        placeholder="What needs to be fixed before this can be signed off?"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
      />
      <div className="reject-actions">
        <button className="btn btn-sm btn-stamp-reject" onClick={handleSubmit}>
          Confirm rejection
        </button>
        <button className="btn btn-sm btn-ghost" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
}