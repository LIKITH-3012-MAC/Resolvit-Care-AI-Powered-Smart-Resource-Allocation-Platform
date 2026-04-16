/**
 * RESOLVIT Neural Assistant Engine
 * Pure JS implementation of the Spherical Chatbot, SSE Streaming, and Intent Routing.
 */

class NeuralAssistant {
  constructor() {
    // 1. Resolve API_URL dynamically (prefer relative /api for unified Flask architecture)
    this.API_URL = window.API_BASE_URL || '/api';
    
    // If running on local dev with a specific port mismatch, check hostname
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      if (typeof API_BASE_URL !== 'undefined') {
        this.API_URL = API_BASE_URL;
      }
    }

    this.history = [];
    this.isOpen = false;
    this.isThinking = false;
    this.initHTML();
    this.bindEvents();
    this.showWelcome();
  }

  // Generate the structural DOM elements once on boot
  initHTML() {
    const container = document.createElement('div');
    container.id = 'neural-assistant-root';
    container.innerHTML = `
      <!-- Launcher -->
      <div class="chat-launcher" id="chat-launcher">
        <span class="chat-launcher-icon">✨</span>
      </div>

      <!-- Main Panel Workspace -->
      <div class="chat-panel" id="chat-panel">
        <div class="chat-header">
          <div class="chat-header-title">
            <div class="chat-avatar">⚡</div>
            <div class="chat-name">
              RESOLVIT Assistant
              <span class="chat-status"><span class="chat-status-dot"></span>Online</span>
            </div>
          </div>
          <button class="chat-close" id="chat-close">×</button>
        </div>

        <div class="chat-body" id="chat-body">
          <!-- Messages inject here -->
        </div>

        <div class="chat-footer">
          <div class="chat-input-wrapper">
            <input type="text" id="chat-input" class="chat-input" placeholder="Type a message or request help..." autocomplete="off">
          </div>
          <button class="chat-send-btn" id="chat-send-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(container);
  }

  bindEvents() {
    document.getElementById('chat-launcher').addEventListener('click', () => this.togglePanel());
    document.getElementById('chat-close').addEventListener('click', () => this.togglePanel(false));
    
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    
    sendBtn.addEventListener('click', () => this.handleSendMessage());
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.handleSendMessage();
      }
    });
  }

  togglePanel(forceState) {
    this.isOpen = forceState !== undefined ? forceState : !this.isOpen;
    const panel = document.getElementById('chat-panel');
    const launcherIcon = document.querySelector('.chat-launcher-icon');
    
    if (this.isOpen) {
      panel.classList.add('active');
      launcherIcon.innerHTML = '✕';
      setTimeout(() => document.getElementById('chat-input').focus(), 300);
    } else {
      panel.classList.remove('active');
      launcherIcon.innerHTML = '✨';
    }
  }

  showWelcome() {
    this.appendBotMessage("Hello! I am the RESOLVIT Intelligent Assistant. I can help you understand this platform, or assist you in filing a community issue. What do you need today?");
    this.appendQuickActions([
      { label: "Report an Issue Near Me", text: "I want to file a complaint" },
      { label: "What is RESOLVIT?", text: "What is this website?" },
      { label: "Check Cases", action: () => window.location.href = '/cases.html' }
    ]);
  }

  appendUserMessage(text) {
    const body = document.getElementById('chat-body');
    const msg = document.createElement('div');
    msg.className = 'chat-msg msg-user';
    msg.textContent = text;
    body.appendChild(msg);
    this.scrollToBottom();
    this.history.push({ role: 'user', content: text });
  }

  appendBotMessage(text, saveHistory = true) {
    const body = document.getElementById('chat-body');
    const msg = document.createElement('div');
    msg.className = 'chat-msg msg-bot';
    msg.innerHTML = text; // Allow basic br tags
    body.appendChild(msg);
    this.scrollToBottom();
    if (saveHistory) {
      this.history.push({ role: 'assistant', content: text });
    }
    return msg; // Return DOM node for streaming updates
  }

  appendQuickActions(actions) {
    const body = document.getElementById('chat-body');
    const wrapper = document.createElement('div');
    wrapper.className = 'quick-actions';
    
    actions.forEach(action => {
      const chip = document.createElement('button');
      chip.className = 'quick-chip';
      chip.textContent = action.label;
      chip.onclick = () => {
        wrapper.remove();
        if (action.action) {
          action.action();
        } else if (action.text) {
          document.getElementById('chat-input').value = action.text;
          this.handleSendMessage();
        }
      };
      wrapper.appendChild(chip);
    });
    
    body.appendChild(wrapper);
    this.scrollToBottom();
  }

  showTyping() {
    const body = document.getElementById('chat-body');
    const msg = document.createElement('div');
    msg.className = 'chat-msg msg-bot typing-indicator';
    msg.id = 'chat-typing';
    msg.innerHTML = `<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>`;
    body.appendChild(msg);
    this.scrollToBottom();
  }

  hideTyping() {
    const typing = document.getElementById('chat-typing');
    if (typing) typing.remove();
  }

  scrollToBottom() {
    const body = document.getElementById('chat-body');
    body.scrollTop = body.scrollHeight;
  }

  // --- INTENT ROUTER: Complaint Workflow Output ---
  injectComplaintForm() {
    const body = document.getElementById('chat-body');
    const wrapper = document.createElement('div');
    wrapper.className = 'chat-form-card';
    wrapper.innerHTML = `
      <h4>📍 Structured Complaint Intake</h4>
      <div class="form-group">
        <label class="form-label">Category</label>
        <select id="chat-complaint-type" class="form-select">
          <option value="disaster_relief">Disaster Relief</option>
          <option value="food_support">Food Shortage</option>
          <option value="medical_emergency">Medical Emergency</option>
          <option value="infrastructure">Infrastructure Issue</option>
          <option value="other">Other</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Location</label>
        <div style="display:flex;gap:4px;">
          <input type="text" id="chat-complaint-location" class="form-input" placeholder="City or Area">
          <button id="chat-gps-btn" class="quick-chip" style="width:auto;margin:0;">🌍 Use GPS</button>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Description (optional)</label>
        <textarea id="chat-complaint-desc" class="form-input" rows="2" placeholder="More details..."></textarea>
      </div>
      <button class="chat-btn-submit" id="chat-submit-btn">Complete Submission</button>
    `;
    body.appendChild(wrapper);
    this.scrollToBottom();

    // Bind Form Events
    document.getElementById('chat-gps-btn').addEventListener('click', (e) => {
      e.target.textContent = 'Locating...';
      if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((pos) => {
          document.getElementById('chat-complaint-location').value = `${pos.coords.latitude.toFixed(4)}, ${pos.coords.input_length || pos.coords.longitude.toFixed(4)}`;
          e.target.textContent = '🌍 GPS Set';
        });
      } else {
        e.target.textContent = 'Unsupported';
      }
    });

    document.getElementById('chat-submit-btn').addEventListener('click', async (e) => {
      const btn = e.target;
      btn.disabled = true;
      btn.textContent = 'Authorizing & Submitting...';
      
      const payload = {
        title: "Chatbot Filed Need",
        description: document.getElementById('chat-complaint-desc').value,
        category: document.getElementById('chat-complaint-type').value,
        location: document.getElementById('chat-complaint-location').value,
      };

      try {
        // Send to backend /reports endpoint
        const res = await fetch(`${this.API_URL}/reports`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        wrapper.remove();
        if(res.ok) {
          this.appendBotMessage("✅ Your complaint has been successfully recorded and routed to the response dashboard. We will notify field teams immediately.");
        } else {
          // If unauthorized or error
          this.appendBotMessage("⚠️ System received it, but you might need to <a href='/login.html' style='color:#a78bfa;'>Log In</a> to track it persistently in your dashboard, though anonymous intake is routed.");
        }
      } catch (err) {
        wrapper.remove();
        this.appendBotMessage("❌ Hmm, the network dropped when trying to file that. Try refreshing if it persists.");
      }
    });
  }

  // --- CORE STREAMING LOGIC ---
  async handleSendMessage() {
    if (this.isThinking) return;
    const inputEl = document.getElementById('chat-input');
    const text = inputEl.value.trim();
    if (!text) return;

    inputEl.value = '';
    this.appendUserMessage(text);
    
    this.isThinking = true;
    this.showTyping();

    try {
      // Setup payload
      const payload = {
        message: text,
        history: this.history.slice(0, -1) // Exclude current user message newly added
      };

      // Call API SSE
      const response = await fetch(`${this.API_URL}/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken') || ''}`
        },
        body: JSON.stringify(payload)
      });

      this.hideTyping();
      
      if (!response.ok) {
        throw new Error('API request failed');
      }

      // Stream Reader setup
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      const botMsgNode = this.appendBotMessage("", false); // empty node to fill
      let accumulatedText = "";
      let intentTriggered = false;

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunkStr = decoder.decode(value, { stream: true });
        // The SSE sends "data: {...}\n\n"
        const lines = chunkStr.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (dataStr === '[DONE]') continue;
            try {
              const dataObj = JSON.parse(dataStr);
              if (dataObj.content) {
                accumulatedText += dataObj.content;
                
                // INTENT ROUTER INTERCEPTOR ✨
                if (accumulatedText.includes('[WORKFLOW:COMPLAINT]')) {
                  intentTriggered = true;
                  botMsgNode.innerHTML = "I understand you want to report an issue. Let me assemble a priority form for you.";
                  // Break outer loop logic basically handled by just modifying UI directly
                }
                
                // Render text if not triggering form
                if (!intentTriggered) {
                  // simple markdown bolding parser
                  const rendered = accumulatedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                  botMsgNode.innerHTML = rendered;
                }
                this.scrollToBottom();
              }
            } catch (e) {
              // Ignore partial JSON chunks common in some SSE
            }
          }
        }
      }

      if (intentTriggered) {
        setTimeout(() => this.injectComplaintForm(), 600);
        this.history.push({ role: 'assistant', content: "[Triggered structured workflow.]" });
      } else {
        this.history.push({ role: 'assistant', content: accumulatedText });
      }

    } catch (error) {
      this.hideTyping();
      this.appendBotMessage(`Sorry, the Cognitive Engine is unresponsive right now. (${error.message})`);
    } finally {
      this.isThinking = false;
    }
  }
}

// Inject Chatbot once DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.RESOLVIT_ASST = new NeuralAssistant();
});
