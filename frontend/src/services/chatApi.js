/**
 * chatApi.js — Objectives CB-1, CB-4
 *
 * Integrated (default):  POST {API_URL}/api/chat
 *                        GET  {API_URL}/api/chat/history
 * Standalone (Beanie):   POST {REACT_APP_CHAT_URL}/chat
 */

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8002";
const STANDALONE_CHAT_URL = process.env.REACT_APP_CHAT_URL || "";
const REQUEST_TIMEOUT_MS = 45000;

function getChatEndpoint() {
  if (STANDALONE_CHAT_URL) {
    return `${STANDALONE_CHAT_URL.replace(/\/$/, "")}/chat`;
  }
  return `${API_URL}/api/chat`;
}

async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("The tutor is taking too long. Please try again in a moment.");
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * @param {Array<{role: string, content: string}>} messages
 * @param {string} context
 * @param {string|null} token
 * @param {string} pageUrl
 */
export async function sendMessage(messages, context, token = null, pageUrl = "/") {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetchWithTimeout(getChatEndpoint(), {
      method: "POST",
      headers,
      body: JSON.stringify({ messages, context, page_url: pageUrl }),
    });
  } catch (err) {
    if (err.message.includes("taking too long")) throw err;
    throw new Error("Could not reach the chat service. Make sure the backend is running.");
  }

  if (!response.ok) {
    let detail = "Chat request failed.";
    try {
      const err = await response.json();
      detail = err.detail || err.message || detail;
    } catch {}
    throw new Error(typeof detail === "string" ? detail : "Chat request failed.");
  }

  try {
    const data = await response.json();
    return {
      reply: data.reply || data.response || "",
      suggestions: Array.isArray(data.suggestions) ? data.suggestions : [],
    };
  } catch {
    throw new Error("Invalid response from chat service.");
  }
}
/**
 * sendMessageStream — CB-10 (Frontend streaming)
 * Streams tokens from {API_URL}/api/chat/stream (or standalone /chat/stream)
 * via SSE-over-fetch. Falls back gracefully if the endpoint isn't available yet.
 *
 * @param {Array<{role: string, content: string}>} messages
 * @param {string} context
 * @param {string|null} token
 * @param {string} pageUrl
 * @param {(chunk: string) => void} onToken - called with each new text chunk
 * @param {(final: {suggestions: string[]}) => void} onDone - called once stream ends
 * @param {(err: Error) => void} onError
 */
export async function sendMessageStream(
  messages,
  context,
  token = null,
  pageUrl = "/",
  onToken = () => {},
  onDone = () => {},
  onError = () => {}
) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const streamUrl = getChatEndpoint().replace(/\/chat$/, "/chat/stream");

  let response;
  try {
    response = await fetch(streamUrl, {
      method: "POST",
      headers,
      body: JSON.stringify({ messages, context, page_url: pageUrl }),
    });
  } catch (err) {
    onError(new Error("Could not reach the chat service. Make sure the backend is running."));
    return;
  }

  if (!response.ok || !response.body) {
    onError(new Error("Streaming not available. Falling back."));
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let suggestions = [];

  try {
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop(); // keep incomplete chunk for next read

      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        const payload = line.replace(/^data:\s*/, "");

        if (payload === "[DONE]") {
          onDone({ suggestions });
          return;
        }

        try {
          const parsed = JSON.parse(payload);
          if (parsed.token) onToken(parsed.token);
          if (Array.isArray(parsed.suggestions)) suggestions = parsed.suggestions;
        } catch {
          // plain-text token fallback (not JSON-wrapped)
          if (payload) onToken(payload);
        }
      }
    }
    onDone({ suggestions });
  } catch (err) {
    onError(new Error("Stream interrupted. Please try again."));
  }
}

/**
 * createChatSession — CB-13
 * Creates a new backend session for logged-in users. Guests skip this
 * (handled by caller) since guest sessions aren't persisted.
 * NOTE: relies on POST {API_URL}/api/chat/sessions — confirm with backend
 * owner whether this route exists yet.
 */
export async function createChatSession(token, title = "New Chat") {
  if (!token) return null;
  try {
    const response = await fetchWithTimeout(`${API_URL}/api/chat/sessions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title }),
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data.session_id || data.id || null;
  } catch {
    return null; // fail silently — local reset still works
  }
}
export async function fetchChatHistory(token) {
  if (!token) return [];

  let response;
  try {
    response = await fetchWithTimeout(`${API_URL}/api/chat/history`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (err) {
    if (err.message.includes("taking too long")) throw err;
    throw new Error("Could not reach the backend server.");
  }

  if (!response.ok) {
    if (response.status === 401) throw new Error("Session expired. Please log in again.");
    throw new Error("Failed to load chat history.");
  }

  try {
    const data = await response.json();
    return data.history || data.sessions || [];
  } catch {
    return [];
  }
}
