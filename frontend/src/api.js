// Keep network details outside the interface; Vite proxies /api locally.
export async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`/api${path}`, options)
  } catch {
    throw new Error('Could not reach your local study service. Check that it is running, then try again.')
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Could not save or load this session. Please try again.')
  }
  return response.json()
}
