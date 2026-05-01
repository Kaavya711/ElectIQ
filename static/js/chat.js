document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('chat-messages');
    const suggestions = document.querySelectorAll('.suggestion-chip');
    const charCounter = document.getElementById('char-counter');

    const countryCode = document.querySelector('meta[name="country_code"]')?.content || 'IN';

    // ── Message rendering ─────────────────────────────────────────────────────

    function formatBotText(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\[(.*?)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
            .replace(/\n/g, '<br>');
    }

    function addMessage(text, isUser = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${isUser ? 'user' : 'bot'}`;
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        msgDiv.innerHTML = `
            <div class="message-bubble" role="${isUser ? 'log' : 'status'}">${isUser ? text : formatBotText(text)}</div>
            <div class="message-time" aria-hidden="true">${time}</div>
        `;
        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
        return msgDiv;
    }

    function addTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'chat-message bot';
        div.id = 'typing-indicator';
        div.setAttribute('aria-label', 'AI is typing');
        div.innerHTML = `
            <div class="typing-indicator" role="status">
                <div class="dot"></div><div class="dot"></div><div class="dot"></div>
            </div>
        `;
        messagesContainer.appendChild(div);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        document.getElementById('typing-indicator')?.remove();
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function setInputState(disabled) {
        input.disabled = disabled;
        sendBtn.disabled = disabled;
        sendBtn.setAttribute('aria-busy', disabled ? 'true' : 'false');
    }

    // ── Streaming send (SSE) ──────────────────────────────────────────────────

    async function sendMessageStreaming(text) {
        setInputState(true);
        input.value = '';
        if (charCounter) charCounter.textContent = '0 / 500';

        addMessage(text, true);
        addTypingIndicator();

        try {
            const resp = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, country: countryCode })
            });

            if (!resp.ok || !resp.body) {
                throw new Error('Stream unavailable');
            }

            removeTypingIndicator();

            // Create bot message bubble to stream into
            const msgDiv = document.createElement('div');
            msgDiv.className = 'chat-message bot';
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            bubble.setAttribute('role', 'status');
            const timeEl = document.createElement('div');
            timeEl.className = 'message-time';
            timeEl.setAttribute('aria-hidden', 'true');
            timeEl.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            msgDiv.appendChild(bubble);
            msgDiv.appendChild(timeEl);
            messagesContainer.appendChild(msgDiv);

            const reader = resp.body.getReader();
            const decoder = new TextDecoder();
            let accumulated = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    const payload = line.slice(6);
                    if (payload === '[DONE]') break;

                    // Unescape newlines encoded for SSE
                    accumulated += payload.replace(/\\n/g, '\n');
                    bubble.innerHTML = formatBotText(accumulated);
                    scrollToBottom();
                }
            }

        } catch (err) {
            // Fallback to non-streaming if SSE fails
            console.warn('Streaming failed, falling back:', err);
            await sendMessageFallback(text);
            return;
        } finally {
            setInputState(false);
            input.focus();
        }
    }

    // ── Non-streaming fallback ────────────────────────────────────────────────

    async function sendMessageFallback(text) {
        try {
            const resp = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, country: countryCode })
            });
            const data = await resp.json();
            removeTypingIndicator();
            addMessage(data.response || "Sorry, I couldn't process that.");
        } catch {
            removeTypingIndicator();
            addMessage("Network error. Please check your connection and try again.");
        } finally {
            setInputState(false);
            input.focus();
        }
    }

    async function sendMessage(text) {
        if (!text.trim()) return;
        await sendMessageStreaming(text);
    }

    // ── Event listeners ───────────────────────────────────────────────────────

    sendBtn?.addEventListener('click', () => sendMessage(input.value));

    input?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(input.value);
        }
    });

    input?.addEventListener('input', function () {
        if (charCounter) charCounter.textContent = `${this.value.length} / 500`;
        this.style.height = '48px';
        this.style.height = this.scrollHeight + 'px';
    });

    suggestions.forEach(chip => {
        chip.addEventListener('click', () => sendMessage(chip.textContent.trim()));
        chip.setAttribute('role', 'button');
        chip.setAttribute('tabindex', '0');
        chip.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage(chip.textContent.trim());
        });
    });
});