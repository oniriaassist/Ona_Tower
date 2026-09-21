function record(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === 'object' ? value as Record<string, unknown> : {};
}

export function errorMessage(body: unknown, status: number): string {
  const data = record(body);
  const error = record(data.error);
  const detail = record(data.detail);
  for (const value of [error.message, data.detail, detail.message, data.message]) {
    if (typeof value === 'string' && value.trim()) return value;
  }
  if (Array.isArray(detail.errors)) {
    const messages = detail.errors.filter((value): value is string => typeof value === 'string' && !!value.trim());
    if (messages.length) return messages.join('; ');
  }
  const details = Array.isArray(error.details) ? error.details : data.detail;
  if (Array.isArray(details)) {
    const message = record(details[0]).msg;
    if (typeof message === 'string' && message.trim()) return message;
  }
  return `Request failed with status ${status}.`;
}

export async function getErrorMessage(response: Response): Promise<string> {
  return errorMessage(await response.json().catch(() => null), response.status);
}
