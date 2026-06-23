/**
 * Auth Screen — Login ("Clock In") and Signup ("New Hire") tabs.
 * Matches the Foreman industrial aesthetic from the prototype.
 */

import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from './Toast';

export default function AuthScreen() {
  const [mode, setMode] = useState('login'); // 'login' or 'signup'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('manager');
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const { signup, login } = useAuth();
  const showToast = useToast();

  function validate() {
    const errs = {};
    if (!/^\S+@\S+\.\S+$/.test(email)) errs.email = 'Enter a valid email address.';
    if (password.length < 6) errs.password = 'Password needs at least 6 characters.';
    if (mode === 'signup' && name.length < 2) errs.name = "Tell us who's clocking in.";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);

    try {
      if (mode === 'signup') {
        await signup(email, password, name, role);
        showToast('Account created — verification email sent.');
      } else {
        await login(email, password);
        showToast('Welcome back!');
      }
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || 'Something went wrong.';
      setErrors({ form: msg });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-wrap">
        {/* Left side — branding */}
        <div className="auth-side">
          <div>
            <div className="brand-mark">
              <span className="rivet"></span>
              <span>Foreman</span>
            </div>
            <h1>Assign the work.<br />Inspect what's done.</h1>
            <p>
              A job board for teams who need real sign-off before work counts
              as finished — not just a checkbox.
            </p>
          </div>
          <div className="ledger">
            <div><b>01</b>&nbsp; Manager opens a work order, sets the complexity, assigns the crew.</div>
            <div><b>02</b>&nbsp; Employee does the job, then submits it for inspection.</div>
            <div><b>03</b>&nbsp; Manager confirms or sends it back — nothing is "done" until it's stamped.</div>
          </div>
        </div>

        {/* Right side — form */}
        <div className="auth-form-area">
          <div className="auth-tabs">
            <button
              className={`auth-tab ${mode === 'login' ? 'is-active' : ''}`}
              onClick={() => { setMode('login'); setErrors({}); }}
              type="button"
              id="tab-login"
            >
              Clock In
            </button>
            <button
              className={`auth-tab ${mode === 'signup' ? 'is-active' : ''}`}
              onClick={() => { setMode('signup'); setErrors({}); }}
              type="button"
              id="tab-signup"
            >
              New Hire
            </button>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {mode === 'signup' && (
              <div className={`field ${errors.name ? 'has-error' : ''}`}>
                <label htmlFor="inp-name">Full name</label>
                <input
                  id="inp-name"
                  type="text"
                  placeholder="e.g. Saad Khan"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
                {errors.name && <div className="field-error">{errors.name}</div>}
              </div>
            )}

            <div className={`field ${errors.email ? 'has-error' : ''}`}>
              <label htmlFor="inp-email">Work email</label>
              <input
                id="inp-email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              {errors.email && <div className="field-error">{errors.email}</div>}
            </div>

            <div className={`field ${errors.password ? 'has-error' : ''}`}>
              <label htmlFor="inp-password">Password</label>
              <input
                id="inp-password"
                type="password"
                placeholder="At least 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              {errors.password && <div className="field-error">{errors.password}</div>}
            </div>

            {mode === 'signup' && (
              <div className="field">
                <label>You are a...</label>
                <div className="role-pick">
                  <button
                    type="button"
                    className={`role-opt ${role === 'manager' ? 'is-selected' : ''}`}
                    onClick={() => setRole('manager')}
                  >
                    <b>Manager</b>
                    <small>Assigns work orders, sets complexity, signs off finished jobs.</small>
                  </button>
                  <button
                    type="button"
                    className={`role-opt ${role === 'employee' ? 'is-selected' : ''}`}
                    onClick={() => setRole('employee')}
                  >
                    <b>Employee</b>
                    <small>Views assigned jobs and submits them for inspection.</small>
                  </button>
                </div>
              </div>
            )}

            {errors.form && (
              <div className="field-error" style={{ marginBottom: 12, display: 'block' }}>
                {errors.form}
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={submitting}
              id="btn-auth-submit"
            >
              {submitting
                ? 'Processing...'
                : mode === 'signup'
                  ? 'Create Account'
                  : 'Clock In'}
            </button>
          </form>

          <div className="auth-foot">
            {mode === 'signup'
              ? 'A verification email will be sent to confirm your address.'
              : "Don't have an account? Click 'New Hire' above to register."}
          </div>
        </div>
      </div>
    </div>
  );
}