/**
 * FitWell — Chat Controller
 * Manages conversational interactions with the LangGraph Gemini Agent,
 * message formatting, typing indicators, quick prompt chips, and conversation history.
 */

document.addEventListener('DOMContentLoaded', () => {
  initChat();
});

function initChat() {
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input-field');
  const clearBtn = document.getElementById('btn-clear-chat');
  const chipsContainer = document.getElementById('suggestion-chips');

  // Submit message
  if (chatForm) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = chatInput.value.trim();
      if (!text) return;
      sendMessage(text);
      chatInput.value = '';
    });
  }

  // Quick Prompt Chips
  if (chipsContainer) {
    chipsContainer.addEventListener('click', (e) => {
      const chip = e.target.closest('.prompt-chip');
      if (!chip) return;
      const prompt = chip.getAttribute('data-prompt');
      if (prompt) {
        sendMessage(prompt);
      }
    });
  }

  // Clear Chat History
  if (clearBtn) {
    clearBtn.addEventListener('click', async () => {
      const confirmClear = confirm('Clear all conversation history?');
      if (!confirmClear) return;

      try {
        const res = await fetch('/api/history/clear', { method: 'POST' });
        if (!res.ok) throw new Error('Failed to clear history');
        renderDefaultGreeting();
        if (typeof showToast === 'function') {
          showToast('Conversation history cleared.', 'info');
        }
      } catch (err) {
        console.error(err);
      }
    });
  }

  // Initial load
  loadConversationHistory();
}

async function loadConversationHistory() {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  try {
    const res = await fetch('/api/history');
    if (!res.ok) throw new Error('Failed to fetch history');
    const history = await res.json();

    container.innerHTML = '';
    if (!history || history.length === 0) {
      renderDefaultGreeting();
      return;
    }

    history.forEach(turn => {
      appendMessageBubble(turn.role, turn.content, turn.timestamp, false);
    });
    scrollToBottom();
  } catch (err) {
    console.error('History load error:', err);
    renderDefaultGreeting();
  }
}

function renderDefaultGreeting() {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  container.innerHTML = '';
  const greeting = `
    👋 **Welcome to FitWell!** I'm your personalized fitness and wellness coach.
    
    All your health data, personal records, and meal plans are stored locally in \`data/memory.json\`. 
    
    Here is what I can do for you:
    - 🏋️‍♂️ **Custom Workouts:** Suggest routines tailored to your muscle gain goal and fitness level.
    - 🥗 **Macro-Aligned Nutrition:** Recommend meals with exact protein, carb, and fat breakdowns.
    - 📍 **Local Facilities:** Find top-rated gyms, yoga studios, and running tracks in Kolkata.
    - 📊 **Track Progress:** Log weight, workouts, and PRs directly into local memory through conversation.
    
    Try clicking one of the quick prompts above or type your question below!
  `;
  appendMessageBubble('assistant', greeting, new Date().toISOString(), false);
}

async function sendMessage(text) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  // Append user turn
  appendMessageBubble('user', text, new Date().toISOString(), true);
  scrollToBottom();

  // Show typing indicator
  const typingIndicator = createTypingIndicator();
  container.appendChild(typingIndicator);
  scrollToBottom();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });

    typingIndicator.remove();

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      const errorMsg = errData.error || 'Server returned an error communicating with the agent.';
      appendMessageBubble('assistant', `⚠️ **Error**: ${errorMsg}`, new Date().toISOString(), true);
    } else {
      const data = await res.json();
      appendMessageBubble('assistant', data.response || 'No response returned.', new Date().toISOString(), true);
      
      // Refresh dashboard data in background as the agent may have logged a workout or meal
      if (typeof loadAllDashboardData === 'function') {
        loadAllDashboardData();
      }
      if (typeof loadRawMemory === 'function') {
        loadRawMemory();
      }
    }
  } catch (err) {
    typingIndicator.remove();
    appendMessageBubble('assistant', `⚠️ **Network error**: Could not connect to the agent server. Please make sure the Flask app is running.`, new Date().toISOString(), true);
  } finally {
    scrollToBottom();
  }
}

function appendMessageBubble(role, rawContent, timestamp, animate = true) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const isUser = role === 'user';
  const msgEl = document.createElement('div');
  msgEl.className = `chat-msg ${isUser ? 'user' : 'assistant'}`;
  if (!animate) msgEl.style.animation = 'none';

  const avatar = isUser ? '👤' : '⚡';
  const timeStr = formatChatTime(timestamp);
  const formattedContent = isUser ? escapeHtml(rawContent) : formatMarkdown(rawContent);

  msgEl.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-content-wrapper">
      <div class="msg-bubble">
        ${formattedContent}
      </div>
      <div class="msg-time">${timeStr}</div>
    </div>
  `;

  container.appendChild(msgEl);
}

function createTypingIndicator() {
  const div = document.createElement('div');
  div.className = 'chat-msg assistant typing-msg';
  div.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-bubble typing-bubble">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  return div;
}

function scrollToBottom() {
  const container = document.getElementById('chat-messages');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function formatChatTime(isoString) {
  if (!isoString) return '';
  try {
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    return '';
  }
}

/**
 * Lightweight, safe markdown formatter for assistant responses.
 * Supports bold, bullet points, numbered lists, inline code, and line breaks.
 */
function formatMarkdown(text) {
  if (!text) return '';

  let html = text;

  // Escape basic HTML
  html = html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Code blocks: ```...```
  html = html.replace(/```([\s\S]*?)```/g, (match, p1) => {
    return `<pre><code>${p1.trim()}</code></pre>`;
  });

  // Inline code: `...`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Bold: **...** or __...__
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');

  // Italic: *...* or _..._
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

  // Process lines into paragraphs and lists
  const lines = html.split('\n');
  let inList = false;
  const processedLines = [];

  lines.forEach(line => {
    const trimmed = line.trim();
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || trimmed.startsWith('• ')) {
      if (!inList) {
        processedLines.push('<ul>');
        inList = true;
      }
      processedLines.push(`<li>${trimmed.substring(2)}</li>`);
    } else if (/^\d+\.\s/.test(trimmed)) {
      if (!inList) {
        processedLines.push('<ol>');
        inList = true;
      }
      const itemText = trimmed.replace(/^\d+\.\s/, '');
      processedLines.push(`<li>${itemText}</li>`);
    } else {
      if (inList) {
        processedLines.push('</ul>');
        inList = false;
      }
      if (trimmed) {
        processedLines.push(`<p>${line}</p>`);
      }
    }
  });

  if (inList) {
    processedLines.push('</ul>');
  }

  return processedLines.join('');
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
