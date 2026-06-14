function getCsrfToken() {
  const match = document.cookie.match(/csrf_access_token=([^;]+)/);
  return match ? match[1] : null;
}

export async function apiFetch(url, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const csrfHeaders = ['GET', 'HEAD', 'OPTIONS'].includes(method)
    ? {}
    : { 'X-CSRF-TOKEN': getCsrfToken() };

  const response = await fetch(url, {
    credentials: 'include',
    ...options,
    headers: { ...csrfHeaders, ...options.headers },
  });

  if (response.status === 401 || response.status === 422) {
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    window.location.href = '/login';
    return null;
  }
  return response;
}
