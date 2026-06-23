/**
 * Kanban board column — renders a list of TicketCards for a given stage.
 * Enhanced with drag and drop handlers.
 */

import TicketCard from './TicketCard';

const STAGE_LABELS = {
  todo: 'To Do',
  in_progress: 'In Progress',
  submitted_for_review: 'For Inspection',
  done: 'Signed Off',
};

export default function BoardColumn({ stage, tasks, userRole, onStart, onSubmit, onDropCard }) {
  const label = STAGE_LABELS[stage] || stage;

  function handleDragOver(e) {
    e.preventDefault();
  }

  function handleDragEnter(e) {
    e.currentTarget.classList.add('drag-over');
  }

  function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
  }

  function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    try {
      const dataStr = e.dataTransfer.getData('text/plain');
      if (dataStr) {
        const { taskId, fromStage } = JSON.parse(dataStr);
        if (fromStage !== stage) {
          onDropCard?.(taskId, fromStage, stage);
        }
      }
    } catch (err) {
      console.error('Drop error:', err);
    }
  }

  return (
    <div 
      className="column"
      onDragOver={handleDragOver}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
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