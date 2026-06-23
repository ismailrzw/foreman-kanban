/**
 * Kanban board column — renders a list of TicketCards for a given stage.
 */

import React from 'react';
import TicketCard from './TicketCard';

const STAGE_LABELS = {
  todo: 'To Do',
  in_progress: 'In Progress',
  submitted_for_review: 'For Inspection',
  done: 'Signed Off',
};

export default function BoardColumn({ stage, tasks, userRole, onStart, onSubmit }) {
  const label = STAGE_LABELS[stage] || stage;

  return (
    <div className="column">
      <div className="column-head">
        <h4>{label}</h4>
        <span className="n">{tasks.length}</span>
      </div>
      <div className="column-body">
        {tasks.length === 0 ? (
          <div className="column-empty">No work orders here</div>
        ) : (
          tasks.map((task) => (
            <TicketCard
              key={task.id}
              task={task}
              userRole={userRole}
              onStart={onStart}
              onSubmit={onSubmit}
            />
          ))
        )}
      </div>
    </div>
  );
}