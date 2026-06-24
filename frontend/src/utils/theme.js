/**
 * Theme Management Utilities.
 * Handles reading, writing, and initializing the visual theme (dark/light)
 * via localStorage and the data-theme attribute on the root document element.
 */

export const getStoredTheme = () => {
  return localStorage.getItem('theme') || 'dark';
};

export const setStoredTheme = (theme) => {
  localStorage.setItem('theme', theme);
  document.documentElement.setAttribute('data-theme', theme);
};

export const initTheme = () => {
  const theme = getStoredTheme();
  document.documentElement.setAttribute('data-theme', theme);
};
