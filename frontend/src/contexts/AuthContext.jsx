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
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Send verification email
    await sendEmailVerification(user);

    // Register in our backend (creates MongoDB user doc with role)
    await user.getIdToken();
    const res = await api.post('/api/register', {
      firebase_uid: user.uid,
      email: email,
      name: name,
      role: role,
    });

    setUserProfile(res.data);
    return user;
  }

  // Login: sign in with Firebase → fetch profile from backend
  async function login(email, password) {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    const res = await api.get('/api/me');
    setUserProfile(res.data);
    return user;
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
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}