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