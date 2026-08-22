/* eslint-disable react-refresh/only-export-components */
/**
 * Auth Context — provides Firebase auth state + user role to all components.
 *
 * On auth state change:
 * 1. If user is logged in → fetch their profile from /api/me → get role
 * 2. Provides: currentUser (Firebase user), userProfile (MongoDB doc with role),
 *    loading, login, signup, logout functions
 */

import { createContext, useContext, useState, useEffect } from 'react';
import {
  auth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  sendEmailVerification,
  onAuthStateChanged,
} from '../firebase';
import api from '../utils/api';

const AuthContext = createContext(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);   // Firebase user object
  const [userProfile, setUserProfile] = useState(null);    // { firebase_uid, email, name, role }
  const [loading, setLoading] = useState(true);

  // Listen for Firebase auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setCurrentUser(user);
      if (user) {
        try {
          const res = await api.get('/api/me');
          setUserProfile(res.data);
        } catch (err) {
          console.warn('User exists in Firebase but not registered in our DB yet:', err);
          setUserProfile(null);
        }
      } else {
        setUserProfile(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  // Sign up: create Firebase account → send verification email → register in backend
  async function signup(email, password, name, role) {
    let user;
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      user = userCredential.user;
      try {
        await sendEmailVerification(user);
      } catch (e) {
        console.warn('Verification email not sent:', e);
      }
    } catch (err) {
      if (err.code === 'auth/email-already-in-use') {
        // Account exists in Firebase — sign in to sync missing MongoDB profile
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        user = userCredential.user;
      } else {
        throw err;
      }
    }

    // Register in our backend (creates MongoDB user doc with role)
    await user.getIdToken();
    try {
      const res = await api.post('/api/register', {
        firebase_uid: user.uid,
        email: email,
        name: name,
        role: role,
      });
      setUserProfile(res.data);
    } catch (err) {
      if (err?.response?.status === 409) {
        // Already registered in MongoDB — fetch current profile
        const res = await api.get('/api/me');
        setUserProfile(res.data);
      } else {
        throw err;
      }
    }

    return user;
  }

  // Login: sign in with Firebase → fetch profile from backend
  async function login(email, password) {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    try {
      const res = await api.get('/api/me');
      setUserProfile(res.data);
      return user;
    } catch (err) {
      if (err?.response?.status === 404) {
        throw new Error("Account exists in Firebase, but your profile was missing in the database. Switch to 'New Hire', enter your name & role, and click 'Create Account' to sync your profile.");
      }
      throw err;
    }
  }

  // Complete registration for users logged into Firebase but missing MongoDB profile
  async function completeRegistration(name, role) {
    if (!currentUser) throw new Error('Not logged into Firebase.');
    const res = await api.post('/api/register', {
      firebase_uid: currentUser.uid,
      email: currentUser.email,
      name: name,
      role: role,
    });
    setUserProfile(res.data);
    return res.data;
  }

  // Logout
  async function logout() {
    await signOut(auth);
    setUserProfile(null);
  }

  const value = {
    currentUser,
    userProfile,
    loading,
    signup,
    login,
    completeRegistration,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}