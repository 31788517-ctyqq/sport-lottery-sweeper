const BENIGN_ERROR_PATTERNS = [
  /ResizeObserver loop completed with undelivered notifications/i,
  /ResizeObserver loop limit exceeded/i
]

export const getErrorMessage = (payload) => {
  if (!payload) return ''
  if (typeof payload === 'string') return payload
  if (payload instanceof Error) return payload.message || payload.toString()
  if (typeof payload?.message === 'string') return payload.message

  try {
    return String(payload)
  } catch {
    return ''
  }
}

export const isBenignBrowserError = (payload) => {
  const message = getErrorMessage(payload)
  if (!message) return false
  return BENIGN_ERROR_PATTERNS.some((pattern) => pattern.test(message))
}

