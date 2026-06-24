/**
 * Top navigation bar — brand mark, page title, user badge, logout.
 */

import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getStoredTheme, setStoredTheme } from '../utils/theme';
import NotificationBell from './NotificationBell';

export default function Topbar() {
  const { userProfile, logout } = useAuth();
  const [theme, setTheme] = useState(getStoredTheme());

  if (!userProfile) return null;

  const initials = userProfile.name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  const isManager = userProfile.role === 'manager';
  const pageTitle = isManager ? 'Job Board — Manager View' : 'My Work Orders';

  const handleToggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    setStoredTheme(nextTheme);
  };

  return (
    <div className="topbar">
      <div className="brand-mark">
        <span className="rivet"></span>
        <span>Foreman</span>
      </div>
      <div className="topbar-divider"></div>
      <div className="topbar-title">{pageTitle}</div>
      <div className="topbar-spacer"></div>

      <div className={`id-badge ${isManager ? '' : 'role-employee'}`}>
        <div className="avatar">{initials}</div>
        <div className="meta">
          <b>{userProfile.name}</b>
          <small>{isManager ? 'Manager' : 'Employee'}</small>
        </div>
      </div>

      <div style={{ marginRight: '16px', display: 'flex', alignItems: 'center' }}>
        <NotificationBell />
      </div>

      <button className="icon-btn" title="Toggle Theme" onClick={handleToggleTheme} style={{ marginRight: '16px', fontSize: '16px' }}>
        {theme === 'dark' ? '☀' : '🌙'}
      </button>

      <button className="icon-btn" title="Sign out" onClick={logout}>
        ⏏
      </button>
    </div>
  );
}