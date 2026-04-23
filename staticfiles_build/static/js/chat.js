/* global IXOVA_CHAT_API, IXOVA_CSRF, IXOVA_USER_INITIAL */
(function () {
  'use strict';

  if (window.location.pathname === '/chat/') return;

  const SUGGESTIONS = [
    '🔥 Show trending',
    '💼 Find internships',
    '📚 Browse courses',
    '📋 My applications',
    '🎯 My AI score',
  ];

  function renderMarkdown(text) {
    return text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" style="color:var(--blue)">$1</a>')
      .replace(/\n/g, '<br>');
  }

  // ── Build Widget HTML ──────────────────────────────────────
  const widget = document.createElement('div');
  widget.id = 'ixova-chat-widget';
  widget.innerHTML = `
    <button class="chat-fab" id="chatFab" aria-label="Open chat">
      <span class="chat-fab-icon open-icon">🤖</span>
      <span class="chat-fab-icon close-icon" style="display:none">✕</span>
      <span class="chat-fab-badge" id="chatBadge" style="display:none">1</span>
    </button>

    <div class="chat-widget" id="chatWidget" style="display:none">
      <div class="chat-widget-header">
        <div style="display:flex;align-items:center;gap:10px">
          <div class="chat-widget-avatar">🤖</div>
          <div>
            <div style="font-weight:700;font-size:14px">IXOVA Assistant</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.75)">● Online</div>
          </div>
        </div>
        <div style="display:flex;gap:8px;align-items:center" id="chatHeaderActions">
          <button id="voiceToggleBtn" title="Mute voice" style="background:none;border:none;cursor:pointer;font-size:17px;color:rgba(255,255,255,0.9);line-height:1;padding:0 2px;">🔊</button>
          <a href="/chat/" class="chat-widget-expand" title="Open full chat">⤢</a>
          <button class="chat-widget-close" id="chatClose">✕</button>
        </div>
      </div>

      <div class="chat-widget-messages" id="widgetMessages">
        <div class="chat-msg bot">
          <div class="chat-avatar bot-avatar">🤖</div>
          <div class="chat-bubble bot-bubble">
            Hey! 👋 I'm your IXOVA Assistant.<br>
            How can I help you today?
          </div>
        </div>
      </div>

      <div class="chat-widget-suggestions" id="widgetSuggestions">
        ${SUGGESTIONS.map(s => `<button class="chat-suggestion-btn widget-suggestion">${s}</button>`).join('')}
      </div>

      <div class="chat-widget-input-bar">
        <input type="text" id="widgetInput" class="chat-input" placeholder="Ask me anything…" maxlength="500" autocomplete="off">
        <button class="chat-send-btn" id="widgetSendBtn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(widget);

  // ── Refs ───────────────────────────────────────────────────
  const fab        = document.getElementById('chatFab');
  const chatWidget = document.getElementById('chatWidget');
  const closeBtn   = document.getElementById('chatClose');
  const input      = document.getElementById('widgetInput');
  const sendBtn    = document.getElementById('widgetSendBtn');
  const msgBox     = document.getElementById('widgetMessages');
  const badge      = document.getElementById('chatBadge');
  const voiceBtn   = document.getElementById('voiceToggleBtn');
  let isOpen       = false;
  let unread       = 0;

  // ── Voice / TTS ────────────────────────────────────────────
  const synth      = window.speechSynthesis;
  let voiceEnabled = true;

  function pickVoice() {
    var all = synth ? synth.getVoices() : [];
    return (
      all.find(v => v.lang.startsWith('en') && /google us english/i.test(v.name)) ||
      all.find(v => v.lang.startsWith('en') && /google/i.test(v.name)) ||
      all.find(v => v.lang === 'en-US') ||
      all.find(v => v.lang.startsWith('en')) ||
      all[0] ||
      null
    );
  }

  function speak(text) {
    if (!synth || !voiceEnabled) return;

    // Clean text for speech
    var clean = text
      .replace(/\*\*(.+?)\*\*/g, '$1')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/<[^>]+>/g, ' ')
      .replace(/[#*_`>•]/g, '')
      .replace(/\s+/g, ' ')
      .trim();
    if (!clean) return;

    synth.cancel();

    function fire() {
      var utter   = new SpeechSynthesisUtterance(clean);
      utter.lang  = 'en-US';
      utter.rate  = 1.0;
      utter.pitch = 1.1;
      utter.volume = 1.0;
      var v = pickVoice();
      if (v) utter.voice = v;
      synth.speak(utter);
    }

    // If voices already loaded, speak immediately
    if (synth.getVoices().length > 0) {
      fire();
    } else {
      // Wait for voices to load then speak
      synth.addEventListener('voiceschanged', function handler() {
        synth.removeEventListener('voiceschanged', handler);
        fire();
      });
    }
  }

  // Voice toggle button
  voiceBtn.addEventListener('click', function (e) {
    e.stopPropagation();
    voiceEnabled = !voiceEnabled;
    voiceBtn.textContent = voiceEnabled ? '🔊' : '🔇';
    voiceBtn.title = voiceEnabled ? 'Mute voice' : 'Unmute voice';
    if (!voiceEnabled && synth) synth.cancel();
  });

  // ── Widget toggle ──────────────────────────────────────────
  function toggleWidget() {
    isOpen = !isOpen;
    chatWidget.style.display = isOpen ? 'flex' : 'none';
    document.querySelector('.chat-fab .open-icon').style.display  = isOpen ? 'none'   : 'inline';
    document.querySelector('.chat-fab .close-icon').style.display = isOpen ? 'inline' : 'none';
    if (isOpen) {
      unread = 0;
      badge.style.display = 'none';
      scrollBottom();
      input.focus();
      // Speak greeting on open
      speak("Hey! I'm your IXOVA Assistant. How can I help you today?");
    } else {
      if (synth) synth.cancel();
    }
  }

  fab.addEventListener('click', toggleWidget);
  closeBtn.addEventListener('click', toggleWidget);

  // ── Messages ───────────────────────────────────────────────
  function scrollBottom() { msgBox.scrollTop = msgBox.scrollHeight; }

  function appendMsg(text, role) {
    const wrap = document.createElement('div');
    wrap.className = `chat-msg ${role}`;
    const initial = (typeof IXOVA_USER_INITIAL !== 'undefined') ? IXOVA_USER_INITIAL : '?';
    if (role === 'user') {
      wrap.innerHTML = `
        <div class="chat-bubble user-bubble">${text}</div>
        <div class="chat-avatar user-avatar">${initial}</div>`;
    } else {
      wrap.innerHTML = `
        <div class="chat-avatar bot-avatar">🤖</div>
        <div class="chat-bubble bot-bubble">${renderMarkdown(text)}</div>`;
      if (!isOpen) { unread++; badge.textContent = unread; badge.style.display = 'flex'; }
    }
    msgBox.appendChild(wrap);
    scrollBottom();
  }

  function showTyping() {
    const wrap = document.createElement('div');
    wrap.className = 'chat-msg bot'; wrap.id = 'wTyping';
    wrap.innerHTML = `
      <div class="chat-avatar bot-avatar">🤖</div>
      <div class="chat-bubble bot-bubble typing-dots"><span></span><span></span><span></span></div>`;
    msgBox.appendChild(wrap); scrollBottom();
  }
  function removeTyping() { const el = document.getElementById('wTyping'); if (el) el.remove(); }

  // ── Send ───────────────────────────────────────────────────
  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    input.disabled = true; sendBtn.disabled = true;
    document.getElementById('widgetSuggestions').style.display = 'none';
    appendMsg(text, 'user');
    showTyping();
    try {
      const res = await fetch(IXOVA_CHAT_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': IXOVA_CSRF },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      removeTyping();
      const reply = data.reply || 'Sorry, something went wrong.';
      appendMsg(reply, 'bot');
      speak(reply);
    } catch {
      removeTyping();
      appendMsg('Connection error. Please try again.', 'bot');
    } finally {
      input.disabled = false; sendBtn.disabled = false; input.focus();
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); sendMessage(); } });

  document.querySelectorAll('.widget-suggestion').forEach(btn => {
    btn.addEventListener('click', () => {
      input.value = btn.textContent.replace(/^[^\w]+/, '').trim();
      sendMessage();
    });
  });

  // Show badge after 3s
  setTimeout(() => {
    if (!isOpen) { unread = 1; badge.textContent = '1'; badge.style.display = 'flex'; }
  }, 3000);

})();
