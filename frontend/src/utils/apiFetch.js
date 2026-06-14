export async function apiFetch(url, options = {}) {
  const response = await fetch(url, { credentials: 'include', ...options });
  if (response.status === 401 || response.status === 422) {
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    window.location.href = '/login';
    return null;
  }
  return response;
}
