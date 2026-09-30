(function () {
  try {
    var saved = localStorage.getItem('theme');
    var dark = saved
      ? saved === 'dark'
      : window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (dark) {
      document.documentElement.classList.add('dark');
    }
    document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
  } catch (error) {
    // sin acceso a localStorage: se queda el tema claro
  }
})();
