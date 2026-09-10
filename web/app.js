const modelSelect = document.getElementById('modelSelect');
const newChatBtn = document.getElementById('newChatBtn');
const refreshSessionsBtn = document.getElementById('refreshSessionsBtn');
const sessionList = document.getElementById('sessionList');
const messagesContainer = document.getElementById('messages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const statusBadge = document.getElementById('statusBadge');
const chatTitle = document.getElementById('chatTitle');
const chatTokenCount = document.getElementById('chatTokenCount');
const sessionTokenCount = document.getElementById('sessionTokenCount');
const messageCount = document.getElementById('messageCount');

const state = {
  model: null,
  sessionId: null,
  sessions: [],
  sessionDetail: null,
  currentMessages: [],
};

function formatTokenValue(value) {
  return Number(value).toLocaleString();
}

function estimateTokens(text) {
  const normalized = (text || '').trim();
  if (!normalized) {
    return 0;
  }
  return Math.max(1, Math.ceil(normalized.length / 4));
}

function calculateConversationTokens(messages) {
  return messages.reduce((sum, item) => sum + estimateTokens(item.content), 0);
}

function updateTokenStats() {
  const chatTokens = calculateConversationTokens(state.currentMessages);
  const sessionTokens = state.sessionDetail ? calculateConversationTokens(state.sessionDetail.messages) : 0;

  chatTokenCount.textContent = formatTokenValue(chatTokens);
  sessionTokenCount.textContent = formatTokenValue(sessionTokens);
  messageCount.textContent = formatTokenValue(state.currentMessages.length);
}

function setStatus(text, isError = false) {
  statusBadge.textContent = text;
  statusBadge.style.background = isError ? 'rgba(248, 113, 113, 0.12)' : 'rgba(34, 197, 94, 0.14)';
  statusBadge.style.color = isError ? '#fecaca' : '#a7f3d0';
  statusBadge.style.borderColor = isError ? 'rgba(248, 113, 113, 0.3)' : 'rgba(34, 197, 94, 0.3)';
}

function formatMessageTime(date = new Date()) {
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    month: 'short',
    day: 'numeric',
  }).format(date);
}

function renderMessage(role, content, timestamp = new Date()) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;

  const roleLabel = document.createElement('span');
  roleLabel.className = 'role';
  roleLabel.textContent = `${role === 'user' ? 'You' : 'Assistant'} • ${formatMessageTime(new Date(timestamp))}`;

  const node = document.createElement('div');
  node.textContent = content;

  wrapper.appendChild(roleLabel);
  wrapper.appendChild(node);
  messagesContainer.appendChild(wrapper);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function resetConversation() {
  state.sessionId = null;
  state.sessionDetail = null;
  state.currentMessages = [];
  chatTitle.textContent = 'New chat';
  messagesContainer.innerHTML = '';
  updateTokenStats();
}

function renderSessionList() {
  sessionList.innerHTML = '';

  if (!state.sessions.length) {
    const empty = document.createElement('li');
    empty.className = 'session-meta';
    empty.textContent = 'No saved sessions';
    sessionList.appendChild(empty);
    return;
  }

  state.sessions.forEach((session) => {
    const item = document.createElement('li');
    const button = document.createElement('button');
    if (state.sessionId === session.id) {
      button.classList.add('active');
    }

    const left = document.createElement('div');
    left.textContent = session.model;

    const meta = document.createElement('div');
    meta.className = 'session-meta';
    meta.textContent = `${session.message_count} messages`;

    button.appendChild(left);
    button.appendChild(meta);
    button.addEventListener('click', async () => {
      state.sessionId = session.id;
      await loadSessionDetail(session.id);
      renderSessionList();
    });
    item.appendChild(button);
    sessionList.appendChild(item);
  });
}

async function loadModels() {
  const response = await fetch('/models');
  const models = await response.json();

  const availableModels = models.filter((model) => model.available);
  if (!availableModels.length) {
    throw new Error('No available models were returned by the backend.');
  }

  modelSelect.innerHTML = availableModels
    .map((model) => `<option value="${model.id}">${model.provider} / ${model.id}</option>`)
    .join('');

  state.model = availableModels[0].id;
  modelSelect.value = state.model;
}

async function loadSessions() {
  const response = await fetch('/sessions');
  state.sessions = await response.json();
  renderSessionList();
}

async function loadSessionDetail(sessionId) {
  const response = await fetch(`/sessions/${sessionId}`);
  const session = await response.json();
  state.sessionDetail = session;
  state.currentMessages = session.messages;
  messagesContainer.innerHTML = '';
  session.messages.forEach((message) => renderMessage(message.role, message.content, message.timestamp || new Date()));
  chatTitle.textContent = `Session ${session.id.slice(0, 8)}`;
  updateTokenStats();
}

async function submitPrompt(event) {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    return;
  }

  const timestamp = new Date().toISOString();
  const newUserMessage = { role: 'user', content: message, timestamp };
  state.currentMessages.push(newUserMessage);
  renderMessage('user', message, timestamp);
  messageInput.value = '';
  messageInput.focus();
  updateTokenStats();

  setStatus('Sending...');

  try {
    const payload = {
      message,
      model: state.model,
      session_id: state.sessionId,
    };

    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed.' }));
      throw new Error(error.detail || 'Request failed.');
    }

    const result = await response.json();
    state.sessionId = result.session_id;
    const assistantTimestamp = new Date().toISOString();
    const assistantMessage = { role: 'assistant', content: result.message.content, timestamp: assistantTimestamp };
    state.sessionDetail = { ...state.sessionDetail, id: result.session_id, messages: [...(state.sessionDetail?.messages || []), newUserMessage, assistantMessage] };
    state.currentMessages.push(assistantMessage);
    renderMessage('assistant', result.message.content, assistantTimestamp);
    chatTitle.textContent = `Session ${result.session_id.slice(0, 8)}`;
    await loadSessions();
    updateTokenStats();
    setStatus('Ready');
  } catch (error) {
    console.error(error);
    renderMessage('assistant', `Error: ${error.message}`);
    setStatus(error.message, true);
  }
}

messageInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

modelSelect.addEventListener('change', (event) => {
  state.model = event.target.value;
});

newChatBtn.addEventListener('click', () => {
  resetConversation();
  setStatus('Ready');
});

refreshSessionsBtn.addEventListener('click', async () => {
  await loadSessions();
});

chatForm.addEventListener('submit', submitPrompt);

async function init() {
  try {
    await loadModels();
    await loadSessions();
    resetConversation();
    setStatus('Ready');
  } catch (error) {
    console.error(error);
    setStatus('Unavailable', true);
  }
}

init();
