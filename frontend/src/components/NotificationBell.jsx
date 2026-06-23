/**
 * Notification Bell — Header notification drawer widget.
 * Periodically polls /api/tasks to detect changes and alerts users.
 * Persists notifications per-user in localStorage.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import api from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

export default function NotificationBell() {
  const { userProfile } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const prevTasksRef = useRef([]);
  const dropdownRef = useRef(null);

  // Load notifications from local storage on mount
  useEffect(() => {
    if (userProfile) {
      const stored = localStorage.getItem(`notifications_${userProfile.firebase_uid}`);
      if (stored) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setNotifications(JSON.parse(stored));
      }
    }
  }, [userProfile]);

  // Save to local storage whenever notifications change
  const saveNotifications = useCallback((updated) => {
    if (typeof updated === 'function') {
      setNotifications((prev) => {
        const next = updated(prev);
        if (userProfile) {
          localStorage.setItem(`notifications_${userProfile.firebase_uid}`, JSON.stringify(next));
        }
        return next;
      });
    } else {
      setNotifications(updated);
      if (userProfile) {
        localStorage.setItem(`notifications_${userProfile.firebase_uid}`, JSON.stringify(updated));
      }
    }
  }, [userProfile]);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (!userProfile) return;

    // Fetch initial task list once to establish baseline
    api.get('/api/tasks')
      .then((res) => {
        prevTasksRef.current = res.data;
      })
      .catch((err) => console.error('Failed to get baseline tasks for notifications:', err));

    const pollInterval = setInterval(async () => {
      try {
        const res = await api.get('/api/tasks');
        const currentTasks = res.data;
        const previousTasks = prevTasksRef.current;

        if (previousTasks.length > 0) {
          const newAlerts = [];
          currentTasks.forEach((task) => {
            const oldTask = previousTasks.find((t) => t.id === task.id);
            if (!oldTask) {
              // Newly created/assigned task
              if (userProfile.role === 'employee' && task.assigned_to === userProfile.firebase_uid) {
                newAlerts.push({
                  id: `${task.id}-new-${Date.now()}`,
                  message: `New Job assigned: "${task.title}"`,
                  read: false,
                  timestamp: new Date().toISOString(),
                });
              }
            } else {
              // Task status changed
              const stageChanged = oldTask.stage !== task.stage;
              const rejectionChanged = !oldTask.is_rejected && task.is_rejected;

              if (userProfile.role === 'employee' && task.assigned_to === userProfile.firebase_uid) {
                if (stageChanged && task.stage === 'done') {
                  newAlerts.push({
                    id: `${task.id}-done-${Date.now()}`,
                    message: `Job signed off: "${task.title}" ✓`,
                    read: false,
                    timestamp: new Date().toISOString(),
                  });
                } else if ((stageChanged || rejectionChanged) && task.stage === 'in_progress' && task.is_rejected) {
                  newAlerts.push({
                    id: `${task.id}-rejected-${Date.now()}`,
                    message: `Job sent back: "${task.title}" (Revisions requested)`,
                    read: false,
                    timestamp: new Date().toISOString(),
                  });
                }
              } else if (userProfile.role === 'manager') {
                if (stageChanged && task.stage === 'submitted_for_review') {
                  newAlerts.push({
                    id: `${task.id}-submitted-${Date.now()}`,
                    message: `Job submitted for inspection: "${task.title}" by ${task.assigned_to_name || 'Crew'}`,
                    read: false,
                    timestamp: new Date().toISOString(),
                  });
                }
              }
            }
          });

          if (newAlerts.length > 0) {
            // Prepend new alerts to notifications list using functional state update
            saveNotifications((prev) => [...newAlerts, ...prev]);
          }
        }
        prevTasksRef.current = currentTasks;
      } catch (err) {
        console.error('Failed to poll tasks for notifications:', err);
      }
    }, 10000); // 10s poll

    return () => clearInterval(pollInterval);
  }, [userProfile, saveNotifications]);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleMarkAllRead = () => {
    const updated = notifications.map((n) => ({ ...n, read: true }));
    saveNotifications(updated);
  };

  const handleClearAll = () => {
    saveNotifications([]);
  };

  return (
    <div className="bell-container" ref={dropdownRef}>
      <button 
        className={`icon-btn bell-icon-btn ${unreadCount > 0 ? 'has-unread' : ''}`}
        title="Notifications"
        onClick={() => setIsOpen(!isOpen)}
      >
        🔔
        {unreadCount > 0 && <span className="bell-badge">{unreadCount}</span>}
      </button>

      {isOpen && (
        <div className="bell-dropdown">
          <div className="bell-dropdown-head">
            <h5>Notifications</h5>
            <div className="bell-dropdown-actions">
              {unreadCount > 0 && (
                <button className="btn-link" onClick={handleMarkAllRead}>
                  Mark all read
                </button>
              )}
              {notifications.length > 0 && (
                <button className="btn-link clear-all" onClick={handleClearAll} style={{ marginLeft: '8px' }}>
                  Clear
                </button>
              )}
            </div>
          </div>
          <div className="bell-dropdown-body">
            {notifications.length === 0 ? (
              <div className="bell-empty">No alerts right now.</div>
            ) : (
              notifications.map((n) => (
                <div className={`bell-item ${n.read ? 'is-read' : 'is-unread'}`} key={n.id}>
                  <div className="bell-item-dot"></div>
                  <div className="bell-item-content">
                    <p className="bell-item-text">{n.message}</p>
                    <span className="bell-item-time">
                      {new Date(n.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
