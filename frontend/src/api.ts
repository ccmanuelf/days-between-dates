// Every call to the JSON API: the status, and the decoded body (null when empty). A request that gets no answer
// comes back with status 0.
export interface Answer<T = any> {
  status: number
  body: T | null
}

export interface ApiError {
  code: string
  field: string | null
  message: string
}

export async function api<T = any>(method: string, path: string, body?: unknown): Promise<Answer<T>> {
  const options: RequestInit = { method, headers: {} }
  if (body !== undefined) {
    options.headers = { 'Content-Type': 'application/json' }
    options.body = JSON.stringify(body)
  }
  try {
    const response = await fetch(path, options)
    const text = await response.text()
    return { status: response.status, body: text ? JSON.parse(text) : null }
  }
  catch {
    return { status: 0, body: null }
  }
}

export function errorOf(answer: Answer): ApiError | null {
  return (answer.body as { error?: ApiError } | null)?.error ?? null
}
