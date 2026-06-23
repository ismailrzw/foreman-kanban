/**
 * Ticket Card — paper-style task card with pin, complexity dots,
 * assignee avatar, and role-appropriate action buttons.
 * Includes stamp animation for approve/reject.
 */

import React, { useState, useRef } from 'react';

function ComplexityDots({ level }) {
  return (
    <div className="complexity-dots">
      {[1, 2, 3].map((i) => (
        <span key={i} className={i <= level ? 'filled' : 'empty'}>●</span>
      ))}
    </div>
  );
}

export default function TicketCard({ task, userRole, onStart, onSubmit }) {
  const [stamped, setStamped] = useState(null); // 'approved' or 'rejected' or null
  const cardRef = useRef(null);

  const isRework = task.is_rejected && task.stage !== 'submitted_for_review' && task.stage !== 'done';

  const assigneeName = task.assigned_to_name || 'Unknown';
  const initials = assigneeName
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  function renderAction() {
    if (userRole !== 'employee') return null;

    switch (task.stage) {
      case 'todo':
        return (
          <button className="ticket-action" onClick={() => onStart?.(task.id)}>
            Start Job
          </button>
        );
      case 'in_progress':
        return (
          <button className="ticket-action" onClick={() => onSubmit?.(task.id)}>
            {isRework ? 'Resubmit for Inspection' : 'Submit for Inspection'}
          </button>
        );
      case 'submitted_for_review':
        return (
          <button className="ticket-action is-disabled">
            Awaiting Inspection…
          </button>
        );
      case 'done':
        return (
          <button className="ticket-action is-done">
            Signed Off ✓
          </button>
        );
      default:
        return null;
    }
  }

  return (
    <div className={`ticket ${isRework ? 'is-rework' : ''}`} ref={cardRef}>
      <div className="pin"></div>
      <div className="ticket-id">{task.id?.slice(-8) || 'N/A'}</div>
      <div className="ticket-title">{task.title}</div>
      <div className="ticket-desc">{task.description}</div>

      {isRework && task.rejection_feedback && (
        <div className="rework-note">
          <b>Sent back by Manager</b>
          {task.rejection_feedback}
        </div>
      )}

      <div className="ticket-meta">
        <ComplexityDots level={task.complexity} />
        <div className="ticket-assignee">
          <div className="mini-avatar">{initials}</div>
          <span>{assigneeName.split(' ')[0]}</span>
        </div>
      </div>

      {renderAction()}

      {stamped && (
        <div className="stamp-overlay">
          <div className={`stamp-mark ${stamped === 'rejected' ? 'reject' : ''}`}>
            {stamped === 'rejected' ? 'SENT BACK' : 'APPROVED'}
          </div>
        </div>
      )}
    </div>
  );
}