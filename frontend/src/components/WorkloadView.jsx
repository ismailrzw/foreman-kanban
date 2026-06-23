/**
 * Workload View — renders employee's tasks grouped by complexity (Low, Medium, High).
 * Displays a completion progress bar per complexity bucket.
 */

import TicketCard from './TicketCard';

const COMPLEXITY_LEVELS = [
  { level: 1, label: 'Low Complexity' },
  { level: 2, label: 'Medium Complexity' },
  { level: 3, label: 'High Complexity' },
];

export default function WorkloadView({ tasks, userRole, onStart, onSubmit }) {
  return (
    <div className="workload-grid">
      {COMPLEXITY_LEVELS.map(({ level, label }) => {
        const bucketTasks = tasks.filter((t) => t.complexity === level);
        const total = bucketTasks.length;
        const done = bucketTasks.filter((t) => t.stage === 'done').length;
        const progressPercent = total > 0 ? Math.round((done / total) * 100) : 0;

        return (
          <div className="workload-column" key={level}>
            <div className="workload-column-head">
              <div className="wch-info">
                <h4>{label}</h4>
                <span className="n">{total}</span>
              </div>
              <div className="workload-progress-bar-container">
                <div className="progress-bar-bg">
                  <div 
                    className="progress-bar-fill" 
                    style={{ width: `${progressPercent}%` }}
                  ></div>
                </div>
                <span className="progress-text">{progressPercent}% Done ({done}/{total})</span>
              </div>
            </div>
            <div className="workload-column-body">
              {total === 0 ? (
                <div className="column-empty">No work orders in this category</div>
              ) : (
                bucketTasks.map((task) => (
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
      })}
    </div>
  );
}
