/* ==========================================================================
   SOMNIA AI - ADVANCED SLEEP WELLNESS ASSISTANT JAVASCRIPT ENGINE
   ========================================================================== */

class SomniaApp {
    constructor() {
        this.state = {
            activeTab: 'dashboard',
            username: 'Rest Explorer',
            sleepScore: 88,
            targetHours: 8.0,
            targetBedtime: '22:45',
            chronotype: 'bear',
            calcMode: 'wake',
            activeSound: 'binaural',
            isPlayingSound: false,
            volume: 0.7,
            sleepTimerMinutes: 30,
            sleepTimerInterval: null,
            sleepTimerSecondsLeft: 0,
            breathingRunning: false,
            breathingCycleCount: 0,
            breathingInterval: null,
            breathingPhase: 'idle',
            journalRating: 4,
            journalEntries: [],
            nightShiftActive: false,
            auroraActive: true
        };

        // Web Audio Context & Nodes
        this.audioCtx = null;
        this.masterGain = null;
        this.activeOscillators = [];
        this.activeNoiseNode = null;
        this.analyser = null;
        this.animFrameId = null;

        // Dr. Somnia AI Knowledge Base
        this.aiKnowledge = {
            "3 AM": "Waking up around 3 AM often coincides with the transition between deep sleep and lighter REM cycles as core body temperature drops. Common triggers include blood sugar dips, nocturnal cortisol surges, or room temperature shifts. Try not looking at the clock and practicing slow 4-7-8 breathing.",
            "caffeine": "Caffeine has an average half-life of 5 to 7 hours and a quarter-life of up to 12 hours. For an 11:00 PM bedtime, your strict Adenosine protection deadline is 2:00 PM. Drinking coffee after this time blocks adenosine receptors and reduces stage 3 deep sleep by up to 20%.",
            "deep sleep": "To boost Stage 3 Deep Sleep (Delta wave recovery): 1) Keep bedroom temperature at 65°F-67°F, 2) Finish heavy meals 3 hours before sleep, 3) Get 20 minutes of morning sunlight to anchor your circadian cortisol peak.",
            "cbt-i": "CBT-I (Cognitive Behavioral Therapy for Insomnia) is the gold standard clinical treatment for sleep difficulty. Key pillars include Sleep Restriction Therapy, Stimulus Control (only use the bed for sleep), and Cognitive Restructuring to reduce bedtime performance anxiety.",
            "racing mind": "When thoughts race at night, your sympathetic nervous system is elevated. Try cognitive shuffling (naming words starting with a random letter) or complete 3 cycles of 4-7-8 breathing to activate the vagus nerve and downregulate heart rate variability."
        };

        this.init();
    }

    init() {
        this.loadSettingsFromStorage();
        this.setupNavigation();
        this.setupLiveClock();
        this.setupChartTooltips();
        this.calculateSleepCycles();
        this.loadJournalEntries();
        this.updateEnvAudit();
        this.renderAnalyticsCharts();

        console.log("Somnia AI 6-Page Engine initialized successfully.");
    }

    /* --------------------------------------------------------------------------
       1. Navigation & Tab Control (6 Pages)
       -------------------------------------------------------------------------- */
    setupNavigation() {
        const navBtns = document.querySelectorAll('.nav-btn');
        navBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabTarget = btn.getAttribute('data-tab');
                this.switchTab(tabTarget);
            });
        });
    }

    switchTab(tabId) {
        this.state.activeTab = tabId;

        // Update nav buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
        });

        // Update tab pages
        document.querySelectorAll('.tab-page').forEach(page => {
            page.classList.toggle('active', page.id === `tab-${tabId}`);
        });

        // Tab specific initializations
        if (tabId === 'analytics') {
            setTimeout(() => this.renderAnalyticsCharts(), 100);
        } else if (tabId === 'relaxation') {
            this.setupVisualizer();
        }
    }

    /* --------------------------------------------------------------------------
       2. Live Circadian Clock & Status
       -------------------------------------------------------------------------- */
    setupLiveClock() {
        const updateClock = () => {
            const now = new Date();
            const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const hour = now.getHours();

            let phaseLabel = "Circadian Phase: Day Alertness";
            let phaseSub = `${timeStr} • High Cortisol Focus Window`;

            if (hour >= 21 || hour < 2) {
                phaseLabel = "Circadian Phase: Melatonin Surge";
                phaseSub = `${timeStr} • Optimal Sleep Window`;
            } else if (hour >= 2 && hour < 6) {
                phaseLabel = "Circadian Phase: Circadian Nadir";
                phaseSub = `${timeStr} • Lowest Body Temp & Deep Recovery`;
            } else if (hour >= 6 && hour < 10) {
                phaseLabel = "Circadian Phase: Cortisol Awakening Pulse";
                phaseSub = `${timeStr} • Daylight Exposure Window`;
            }

            const labelEl = document.getElementById('current-phase-label');
            const subEl = document.getElementById('live-clock');
            if (labelEl) labelEl.textContent = phaseLabel;
            if (subEl) subEl.textContent = phaseSub;
        };

        updateClock();
        setInterval(updateClock, 30000);
    }

    /* --------------------------------------------------------------------------
       3. Interactive Timeline Tooltips
       -------------------------------------------------------------------------- */
    setupChartTooltips() {
        const points = document.querySelectorAll('.chart-point');
        const tooltip = document.getElementById('chart-tooltip');
        const wrapper = document.getElementById('sleep-chart-wrapper');

        if (!points || !tooltip || !wrapper) return;

        points.forEach(point => {
            point.addEventListener('mouseenter', () => {
                const info = point.getAttribute('data-info');
                tooltip.textContent = info;
                tooltip.classList.remove('hidden');

                const rect = point.getBoundingClientRect();
                const wrapperRect = wrapper.getBoundingClientRect();

                tooltip.style.left = `${rect.left - wrapperRect.left + 15}px`;
                tooltip.style.top = `${rect.top - wrapperRect.top - 35}px`;
            });

            point.addEventListener('mouseleave', () => {
                tooltip.classList.add('hidden');
            });
        });
    }

    /* --------------------------------------------------------------------------
       4. PAGE 2: ANALYTICS CANVAS CHARTS (NO DEPENDENCIES)
       -------------------------------------------------------------------------- */
    renderAnalyticsCharts() {
        this.render7DayScoresCanvas();
        this.renderStageDonutCanvas();
        this.renderHRVLatencyCanvas();
    }

    render7DayScoresCanvas() {
        const canvas = document.getElementById('canvas-7day-scores');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const width = canvas.width;
        const height = canvas.height;
        ctx.clearRect(0, 0, width, height);

        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const scores = [82, 85, 78, 89, 92, 88, 91];
        const barWidth = 45;
        const gap = (width - 80 - (days.length * barWidth)) / (days.length - 1);
        const startX = 50;
        const chartHeight = height - 60;

        // Draw grid target line (85 score)
        const targetY = chartHeight - ((85 / 100) * chartHeight) + 20;
        ctx.beginPath();
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = 'rgba(16, 185, 129, 0.5)';
        ctx.lineWidth = 1.5;
        ctx.moveTo(30, targetY);
        ctx.lineTo(width - 20, targetY);
        ctx.stroke();

        ctx.setLineDash([]);
        ctx.font = '10px "Plus Jakarta Sans"';
        ctx.fillStyle = '#10B981';
        ctx.fillText('Target Goal (85)', width - 110, targetY - 6);

        // Render Bars
        days.forEach((day, idx) => {
            const score = scores[idx];
            const barH = (score / 100) * chartHeight;
            const x = startX + idx * (barWidth + gap);
            const y = chartHeight - barH + 20;

            const grad = ctx.createLinearGradient(0, y, 0, chartHeight + 20);
            if (score >= 88) {
                grad.addColorStop(0, '#8B5CF6');
                grad.addColorStop(1, '#6366F1');
            } else {
                grad.addColorStop(0, '#06B6D4');
                grad.addColorStop(1, '#3B82F6');
            }

            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.roundRect(x, y, barWidth, barH, 8);
            ctx.fill();

            // Value text
            ctx.font = '700 12px "Outfit"';
            ctx.fillStyle = '#FFFFFF';
            ctx.textAlign = 'center';
            ctx.fillText(score.toString(), x + barWidth / 2, y - 8);

            // Day text
            ctx.font = '600 11px "Plus Jakarta Sans"';
            ctx.fillStyle = '#94A3B8';
            ctx.fillText(day, x + barWidth / 2, height - 10);
        });
    }

    renderStageDonutCanvas() {
        const canvas = document.getElementById('canvas-stage-donut');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const width = canvas.width;
        const height = canvas.height;
        ctx.clearRect(0, 0, width, height);

        const centerX = width / 2;
        const centerY = height / 2;
        const outerRadius = 80;
        const innerRadius = 55;

        const stages = [
            { name: 'Deep', ratio: 0.23, color: '#8B5CF6' },
            { name: 'REM', ratio: 0.24, color: '#06B6D4' },
            { name: 'Light', ratio: 0.48, color: '#818CF8' },
            { name: 'Awake', ratio: 0.05, color: '#F59E0B' }
        ];

        let startAngle = -Math.PI / 2;

        stages.forEach(s => {
            const sliceAngle = s.ratio * 2 * Math.PI;
            const endAngle = startAngle + sliceAngle;

            ctx.beginPath();
            ctx.arc(centerX, centerY, outerRadius, startAngle, endAngle);
            ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true);
            ctx.closePath();
            ctx.fillStyle = s.color;
            ctx.fill();

            startAngle = endAngle;
        });

        // Center Text
        ctx.font = '800 22px "Outfit"';
        ctx.fillStyle = '#F8FAFC';
        ctx.textAlign = 'center';
        ctx.fillText('7h 48m', centerX, centerY + 4);

        ctx.font = '600 11px "Plus Jakarta Sans"';
        ctx.fillStyle = '#94A3B8';
        ctx.fillText('Total Rest', centerX, centerY + 20);
    }

    renderHRVLatencyCanvas() {
        const canvas = document.getElementById('canvas-hrv-latency');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const width = canvas.width;
        const height = canvas.height;
        ctx.clearRect(0, 0, width, height);

        const hrvPoints = [58, 62, 60, 65, 70, 68, 72, 64, 69, 71, 66, 68, 74, 70];
        const latencyPoints = [22, 18, 25, 14, 12, 15, 10, 16, 12, 11, 15, 12, 9, 11];

        const padding = 40;
        const chartW = width - (padding * 2);
        const chartH = height - (padding * 2);

        // Draw Line 1: HRV (Cyan)
        ctx.beginPath();
        ctx.strokeStyle = '#06B6D4';
        ctx.lineWidth = 3;
        hrvPoints.forEach((val, idx) => {
            const x = padding + (idx * (chartW / (hrvPoints.length - 1)));
            const y = height - padding - ((val - 50) / 30 * chartH);
            if (idx === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();

        // Draw Line 2: Latency (Amber)
        ctx.beginPath();
        ctx.strokeStyle = '#F59E0B';
        ctx.lineWidth = 3;
        latencyPoints.forEach((val, idx) => {
            const x = padding + (idx * (latencyPoints.length > 1 ? chartW / (latencyPoints.length - 1) : 0));
            const y = height - padding - (val / 30 * chartH);
            if (idx === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();
    }

    /* --------------------------------------------------------------------------
       5. Dr. Somnia AI Conversational Engine
       -------------------------------------------------------------------------- */
    sendQuickPrompt(text) {
        const input = document.getElementById('chat-input');
        if (input) {
            input.value = text;
            this.handleChatSubmit(new Event('submit'));
        }
    }

    handleChatSubmit(event) {
        event.preventDefault();
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;

        this.renderChatMessage(message, 'user');
        input.value = '';

        setTimeout(() => {
            const aiResponse = this.generateAIResponse(message);
            this.renderChatMessage(aiResponse, 'bot');
        }, 700);
    }

    generateAIResponse(userText) {
        const lower = userText.toLowerCase();

        if (lower.includes('3 am') || lower.includes('wake up') || lower.includes('waking up')) {
            return this.aiKnowledge["3 AM"];
        } else if (lower.includes('caffeine') || lower.includes('coffee') || lower.includes('cutoff')) {
            return this.aiKnowledge["caffeine"];
        } else if (lower.includes('deep sleep') || lower.includes('rem') || lower.includes('stage 3')) {
            return this.aiKnowledge["deep sleep"];
        } else if (lower.includes('cbt') || lower.includes('cbt-i') || lower.includes('insomnia')) {
            return this.aiKnowledge["cbt-i"];
        } else if (lower.includes('racing') || lower.includes('mind') || lower.includes('thought') || lower.includes('stress')) {
            return this.aiKnowledge["racing mind"];
        }

        return `Based on your circadian profile (${this.state.chronotype.toUpperCase()} Chronotype):
        
To optimize your sleep efficiency tonight:
1. **Lighting Shift**: Dim room lights to warm amber at 9:00 PM to spark melatonin secretion.
2. **Audio Entrainment**: Play 15 minutes of 432Hz Binaural Delta waves in the Relaxation tab.
3. **Latency Target**: Aim to enter bed at ${this.state.targetBedtime} for your full ${this.state.targetHours} hour target.`;
    }

    renderChatMessage(text, sender) {
        const chatContainer = document.getElementById('chat-messages-container');
        if (!chatContainer) return;

        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${sender}-message`;

        const iconClass = sender === 'bot' ? 'fa-user-doctor' : 'fa-user';

        msgDiv.innerHTML = `
            <div class="message-avatar"><i class="fa-solid ${iconClass}"></i></div>
            <div class="message-content">
                <p>${text.replace(/\n/g, '<br>')}</p>
                <span class="message-time">${timeStr}</span>
            </div>
        `;

        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    clearChat() {
        const chatContainer = document.getElementById('chat-messages-container');
        if (chatContainer) {
            chatContainer.innerHTML = `
                <div class="chat-message bot-message">
                    <div class="message-avatar"><i class="fa-solid fa-user-doctor"></i></div>
                    <div class="message-content">
                        <p>Chat history cleared. How else can I assist your sleep wellness today?</p>
                        <span class="message-time">Just now</span>
                    </div>
                </div>
            `;
        }
    }

    /* --------------------------------------------------------------------------
       6. 90-Minute Sleep Cycle Optimizer
       -------------------------------------------------------------------------- */
    setCalcMode(mode) {
        this.state.calcMode = mode;
        document.getElementById('calc-mode-wake').classList.toggle('active', mode === 'wake');
        document.getElementById('calc-mode-sleep').classList.toggle('active', mode === 'sleep');
        this.calculateSleepCycles();
    }

    calculateSleepCycles() {
        const timeInput = document.getElementById('target-time-input');
        const container = document.getElementById('cycle-results-container');
        if (!timeInput || !container) return;

        const [hours, minutes] = timeInput.value.split(':').map(Number);
        const baseDate = new Date();
        baseDate.setHours(hours, minutes, 0, 0);

        const latencyMinutes = 14;
        const results = [];

        for (let cycles = 6; cycles >= 3; cycles--) {
            const totalSleepMins = (cycles * 90) + latencyMinutes;
            const targetDate = new Date(baseDate.getTime());

            if (this.state.calcMode === 'wake') {
                targetDate.setMinutes(targetDate.getMinutes() - totalSleepMins);
            } else {
                targetDate.setMinutes(targetDate.getMinutes() + totalSleepMins);
            }

            const formattedTime = targetDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const hoursVal = (cycles * 1.5).toFixed(1);
            const isRecommended = (cycles === 5 || cycles === 6);

            results.push({
                cycles,
                time: formattedTime,
                duration: `${hoursVal} hrs (${cycles} Cycles)`,
                isRecommended
            });
        }

        container.innerHTML = results.map(r => `
            <div class="cycle-result-item ${r.isRecommended ? 'recommended' : ''}">
                <div>
                    <div class="cycle-time text-primary">${r.time}</div>
                    <span class="text-sub" style="font-size:11px;">${this.state.calcMode === 'wake' ? 'Go to sleep at' : 'Wake up at'}</span>
                </div>
                <div class="cycle-details">
                    <span class="badge ${r.isRecommended ? 'badge-success' : 'badge-info'}">${r.duration}</span>
                </div>
            </div>
        `).join('');
    }

    /* --------------------------------------------------------------------------
       7. Web Audio Soundscape Engine
       -------------------------------------------------------------------------- */
    initAudioContext() {
        if (!this.audioCtx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            this.audioCtx = new AudioCtx();
            this.masterGain = this.audioCtx.createGain();
            this.analyser = this.audioCtx.createAnalyser();

            this.masterGain.gain.setValueAtTime(this.state.volume, this.audioCtx.currentTime);
            this.masterGain.connect(this.analyser);
            this.analyser.connect(this.audioCtx.destination);
        }

        if (this.audioCtx.state === 'suspended') {
            this.audioCtx.resume();
        }
    }

    selectSound(soundKey) {
        this.state.activeSound = soundKey;

        document.querySelectorAll('.sound-card').forEach(card => {
            card.classList.toggle('active', card.id === `sound-card-${soundKey}`);
        });

        if (this.state.isPlayingSound) {
            this.stopAudioSynthesis();
            this.startAudioSynthesis();
        }
    }

    toggleSoundPlay() {
        if (this.state.isPlayingSound) {
            this.stopAudioSynthesis();
        } else {
            this.startAudioSynthesis();
        }
    }

    startAudioSynthesis() {
        this.initAudioContext();
        this.stopAudioSynthesisNodes();

        const now = this.audioCtx.currentTime;
        const soundKey = this.state.activeSound;

        if (soundKey === 'binaural') {
            const oscL = this.audioCtx.createOscillator();
            const oscR = this.audioCtx.createOscillator();
            const merger = this.audioCtx.createChannelMerger(2);

            oscL.type = 'sine';
            oscL.frequency.setValueAtTime(216, now);
            oscR.type = 'sine';
            oscR.frequency.setValueAtTime(219.5, now);

            oscL.connect(merger, 0, 0);
            oscR.connect(merger, 0, 1);
            merger.connect(this.masterGain);

            oscL.start();
            oscR.start();
            this.activeOscillators.push(oscL, oscR);
        } else if (soundKey === 'pink') {
            const bufferSize = this.audioCtx.sampleRate * 3;
            const buffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
            const data = buffer.getChannelData(0);

            let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
            for (let i = 0; i < bufferSize; i++) {
                const white = Math.random() * 2 - 1;
                b0 = 0.99886 * b0 + white * 0.0555179;
                b1 = 0.99332 * b1 + white * 0.0750759;
                b2 = 0.96900 * b2 + white * 0.1538520;
                b3 = 0.86650 * b3 + white * 0.3104856;
                b4 = 0.55000 * b4 + white * 0.5329522;
                b5 = -0.7616 * b5 - white * 0.0168980;
                data[i] = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362;
                data[i] *= 0.11;
                b6 = white * 0.115926;
            }

            const noiseSource = this.audioCtx.createBufferSource();
            noiseSource.buffer = buffer;
            noiseSource.loop = true;
            noiseSource.connect(this.masterGain);
            noiseSource.start();

            this.activeNoiseNode = noiseSource;
        } else if (soundKey === 'rain') {
            const bufferSize = this.audioCtx.sampleRate * 2;
            const buffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                data[i] = (Math.random() * 2 - 1) * 0.15;
            }

            const noiseSource = this.audioCtx.createBufferSource();
            noiseSource.buffer = buffer;
            noiseSource.loop = true;

            const filter = this.audioCtx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(800, now);

            noiseSource.connect(filter);
            filter.connect(this.masterGain);
            noiseSource.start();

            this.activeNoiseNode = noiseSource;
        } else if (soundKey === 'space') {
            const osc1 = this.audioCtx.createOscillator();
            const osc2 = this.audioCtx.createOscillator();
            osc1.type = 'sine';
            osc1.frequency.setValueAtTime(55, now);
            osc2.type = 'sine';
            osc2.frequency.setValueAtTime(110, now);

            osc1.connect(this.masterGain);
            osc2.connect(this.masterGain);
            osc1.start();
            osc2.start();

            this.activeOscillators.push(osc1, osc2);
        }

        this.state.isPlayingSound = true;
        this.updateAudioUI();
        this.startSleepTimer();
    }

    stopAudioSynthesisNodes() {
        this.activeOscillators.forEach(osc => {
            try { osc.stop(); osc.disconnect(); } catch (e) {}
        });
        this.activeOscillators = [];

        if (this.activeNoiseNode) {
            try { this.activeNoiseNode.stop(); this.activeNoiseNode.disconnect(); } catch (e) {}
            this.activeNoiseNode = null;
        }
    }

    stopAudioSynthesis() {
        this.stopAudioSynthesisNodes();
        this.state.isPlayingSound = false;
        this.updateAudioUI();

        if (this.state.sleepTimerInterval) {
            clearInterval(this.state.sleepTimerInterval);
            this.state.sleepTimerInterval = null;
        }
    }

    setVolume(val) {
        this.state.volume = val / 100;
        if (this.masterGain && this.audioCtx) {
            this.masterGain.gain.setValueAtTime(this.state.volume, this.audioCtx.currentTime);
        }
    }

    setSleepTimer(mins) {
        this.state.sleepTimerMinutes = mins;
        if (this.state.isPlayingSound) {
            this.startSleepTimer();
        }
    }

    startSleepTimer() {
        if (this.state.sleepTimerInterval) {
            clearInterval(this.state.sleepTimerInterval);
        }

        if (this.state.sleepTimerMinutes === 'off') return;

        this.state.sleepTimerSecondsLeft = parseInt(this.state.sleepTimerMinutes) * 60;
        this.state.sleepTimerInterval = setInterval(() => {
            this.state.sleepTimerSecondsLeft--;
            if (this.state.sleepTimerSecondsLeft <= 0) {
                this.stopAudioSynthesis();
                alert("Sleep timer completed. Soundscapes powered off.");
            }
        }, 1000);
    }

    updateAudioUI() {
        const icon = document.getElementById('play-btn-icon');
        const badge = document.getElementById('sound-status-badge');
        const soundName = document.getElementById('playing-sound-name');

        if (icon) {
            icon.className = this.state.isPlayingSound ? 'fa-solid fa-pause' : 'fa-solid fa-play';
        }

        if (badge && soundName) {
            if (this.state.isPlayingSound) {
                badge.classList.add('playing');
                soundName.textContent = `Playing: ${this.state.activeSound.toUpperCase()}`;
            } else {
                badge.classList.remove('playing');
                soundName.textContent = 'Audio Standby';
            }
        }
    }

    setupVisualizer() {
        const canvas = document.getElementById('audio-visualizer-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const draw = () => {
            this.animFrameId = requestAnimationFrame(draw);
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (!this.state.isPlayingSound || !this.analyser) {
                ctx.beginPath();
                ctx.moveTo(0, canvas.height / 2);
                ctx.lineTo(canvas.width, canvas.height / 2);
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                ctx.lineWidth = 2;
                ctx.stroke();
                return;
            }

            const bufferLength = this.analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            this.analyser.getByteTimeDomainData(dataArray);

            ctx.lineWidth = 2;
            ctx.strokeStyle = '#06B6D4';
            ctx.beginPath();

            const sliceWidth = canvas.width * 1.0 / bufferLength;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                const v = dataArray[i] / 128.0;
                const y = v * canvas.height / 2;

                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
                x += sliceWidth;
            }

            ctx.lineTo(canvas.width, canvas.height / 2);
            ctx.stroke();
        };

        if (!this.animFrameId) draw();
    }

    /* --------------------------------------------------------------------------
       8. Guided 4-7-8 Breathing Circle
       -------------------------------------------------------------------------- */
    toggleBreathing() {
        if (this.state.breathingRunning) {
            this.stopBreathing();
        } else {
            this.startBreathing();
        }
    }

    startBreathing() {
        this.state.breathingRunning = true;
        const btn = document.getElementById('btn-breathing-toggle');
        if (btn) btn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause Session';
        this.runBreathingCycle();
    }

    stopBreathing() {
        this.state.breathingRunning = false;
        if (this.state.breathingInterval) {
            clearTimeout(this.state.breathingInterval);
        }

        const ring = document.getElementById('breathing-ring');
        const text = document.getElementById('breathing-text');
        const timer = document.getElementById('breathing-countdown');
        const btn = document.getElementById('btn-breathing-toggle');

        if (ring) ring.className = 'breathing-ring-outer';
        if (text) text.textContent = 'Ready';
        if (timer) timer.textContent = '--';
        if (btn) btn.innerHTML = '<i class="fa-solid fa-play"></i> Start 4-7-8 Session';
    }

    runBreathingCycle() {
        if (!this.state.breathingRunning) return;

        const ring = document.getElementById('breathing-ring');
        const text = document.getElementById('breathing-text');
        const timer = document.getElementById('breathing-countdown');

        ring.className = 'breathing-ring-outer inhale';
        text.textContent = 'Inhale';
        this.countdownStep(4, timer, () => {
            if (!this.state.breathingRunning) return;

            ring.className = 'breathing-ring-outer hold';
            text.textContent = 'Hold Breath';
            this.countdownStep(7, timer, () => {
                if (!this.state.breathingRunning) return;

                ring.className = 'breathing-ring-outer exhale';
                text.textContent = 'Exhale Slowly';
                this.countdownStep(8, timer, () => {
                    if (!this.state.breathingRunning) return;

                    this.state.breathingCycleCount++;
                    const countEl = document.getElementById('breathing-cycles-count');
                    if (countEl) countEl.textContent = this.state.breathingCycleCount;

                    this.runBreathingCycle();
                });
            });
        });
    }

    countdownStep(seconds, timerEl, onComplete) {
        let count = seconds;
        timerEl.textContent = count;

        const step = () => {
            if (!this.state.breathingRunning) return;
            count--;
            if (count > 0) {
                timerEl.textContent = count;
                this.state.breathingInterval = setTimeout(step, 1000);
            } else {
                onComplete();
            }
        };

        this.state.breathingInterval = setTimeout(step, 1000);
    }

    /* --------------------------------------------------------------------------
       9. Environment Audit & Sleep Journal
       -------------------------------------------------------------------------- */
    updateEnvAudit() {
        const tempEl = document.getElementById('slider-temp');
        if (!tempEl) return;

        const temp = parseFloat(tempEl.value);
        const humidity = parseInt(document.getElementById('slider-humidity').value);
        const light = parseInt(document.getElementById('slider-light').value);
        const noise = parseInt(document.getElementById('slider-noise').value);

        document.getElementById('val-temp').textContent = `${temp.toFixed(1)} °F`;
        document.getElementById('val-humidity').textContent = `${humidity} %`;
        document.getElementById('val-light').textContent = `${light} Lux`;
        document.getElementById('val-noise').textContent = `${noise} dB`;

        // Update dashboard climate indicators
        const dashTemp = document.getElementById('dash-temp-val');
        const dashHum = document.getElementById('dash-humidity-val');
        const dashNoise = document.getElementById('dash-noise-val');
        if (dashTemp) dashTemp.textContent = `${temp.toFixed(1)}°F`;
        if (dashHum) dashHum.textContent = `${humidity}%`;
        if (dashNoise) dashNoise.textContent = `${noise} dB`;

        let score = 100;
        let tips = [];

        if (temp > 68) {
            score -= (temp - 68) * 4;
            tips.push("Cool room down closer to 66°F.");
        }
        if (humidity < 40 || humidity > 55) {
            score -= 10;
            tips.push("Adjust humidity to 45% for clear airway breathing.");
        }
        if (light > 5) {
            score -= (light * 2);
            tips.push("Block light leak sources to reach 0-5 Lux.");
        }
        if (noise > 30) {
            score -= (noise - 30) * 1.5;
            tips.push("Use pink noise soundscapes to mask ambient sound spikes.");
        }

        score = Math.max(20, Math.min(100, Math.round(score)));
        const scoreEl = document.getElementById('env-score-val');
        if (scoreEl) scoreEl.textContent = `${score}%`;

        const adviceText = document.getElementById('env-advice-text');
        if (adviceText) {
            adviceText.textContent = tips.length ? tips.join(' ') : 'Your room climate is in peak condition for restorative Stage 3 Deep sleep!';
        }
    }

    setRating(val) {
        this.state.journalRating = val;
        document.querySelectorAll('.star-btn').forEach((btn, idx) => {
            btn.classList.toggle('active', idx < val);
        });
    }

    saveJournalEntry(event) {
        event.preventDefault();
        const dreamNote = document.getElementById('dream-note').value;

        const tags = [];
        ['caffeine', 'alcohol', 'screen', 'meal', 'stress'].forEach(id => {
            const el = document.getElementById(`tag-${id}`);
            if (el && el.checked) tags.push(el.value);
        });

        const newEntry = {
            id: Date.now(),
            date: new Date().toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' }),
            rating: this.state.journalRating,
            tags,
            note: dreamNote || 'No notes added'
        };

        this.state.journalEntries.unshift(newEntry);
        localStorage.setItem('somnia_journal', JSON.stringify(this.state.journalEntries));

        document.getElementById('dream-note').value = '';
        this.renderJournalHistory();
    }

    loadJournalEntries() {
        const saved = localStorage.getItem('somnia_journal');
        if (saved) {
            try {
                this.state.journalEntries = JSON.parse(saved);
            } catch (e) {
                this.state.journalEntries = [];
            }
        }

        if (this.state.journalEntries.length === 0) {
            this.state.journalEntries.push({
                id: 1,
                date: 'Aug 9, 2026',
                rating: 4,
                tags: ['Late Caffeine'],
                note: 'Vivid dream about floating in an ocean of blue light. Felt very refreshed upon waking.'
            });
        }

        this.renderJournalHistory();
    }

    renderJournalHistory() {
        const container = document.getElementById('journal-history-list');
        const countEl = document.getElementById('journal-count');

        if (!container) return;
        if (countEl) countEl.textContent = this.state.journalEntries.length;

        container.innerHTML = this.state.journalEntries.map(entry => `
            <div class="journal-entry-card">
                <div>
                    <div style="font-weight:700;font-size:13px;margin-bottom:2px;">${'⭐'.repeat(entry.rating)}</div>
                    <p style="font-size:12px;color:var(--text-secondary);">${entry.note}</p>
                    ${entry.tags.length ? `<div style="margin-top:6px;display:flex;gap:4px;flex-wrap:wrap;">${entry.tags.map(t => `<span class="badge badge-info" style="font-size:10px;">${t}</span>`).join('')}</div>` : ''}
                </div>
                <span class="journal-entry-meta">${entry.date}</span>
            </div>
        `).join('');
    }

    /* --------------------------------------------------------------------------
       10. PAGE 6: SETTINGS MANAGER
       -------------------------------------------------------------------------- */
    loadSettingsFromStorage() {
        const savedSettings = localStorage.getItem('somnia_settings');
        if (savedSettings) {
            try {
                const parsed = JSON.parse(savedSettings);
                this.state.username = parsed.username || 'Rest Explorer';
                this.state.targetHours = parsed.targetHours || 8.0;
                this.state.targetBedtime = parsed.targetBedtime || '22:45';
                this.state.chronotype = parsed.chronotype || 'bear';
                this.state.nightShiftActive = !!parsed.nightShiftActive;
            } catch (e) {}
        }

        // Apply UI values
        const nameEl = document.getElementById('setting-username');
        const hoursEl = document.getElementById('setting-target-hours');
        const bedtimeEl = document.getElementById('setting-bedtime');
        const chronoEl = document.getElementById('setting-chronotype');
        const nightShiftEl = document.getElementById('toggle-night-shift');

        if (nameEl) nameEl.value = this.state.username;
        if (hoursEl) hoursEl.value = this.state.targetHours;
        if (bedtimeEl) bedtimeEl.value = this.state.targetBedtime;
        if (chronoEl) chronoEl.value = this.state.chronotype;
        if (nightShiftEl) nightShiftEl.checked = this.state.nightShiftActive;

        const greeting = document.getElementById('greeting-username');
        if (greeting) greeting.textContent = this.state.username;

        this.toggleNightShift(this.state.nightShiftActive);
    }

    saveSettings(event) {
        event.preventDefault();
        this.state.username = document.getElementById('setting-username').value;
        this.state.targetHours = parseFloat(document.getElementById('setting-target-hours').value);
        this.state.targetBedtime = document.getElementById('setting-bedtime').value;
        this.state.chronotype = document.getElementById('setting-chronotype').value;

        localStorage.setItem('somnia_settings', JSON.stringify({
            username: this.state.username,
            targetHours: this.state.targetHours,
            targetBedtime: this.state.targetBedtime,
            chronotype: this.state.chronotype,
            nightShiftActive: this.state.nightShiftActive
        }));

        const greeting = document.getElementById('greeting-username');
        if (greeting) greeting.textContent = this.state.username;

        alert('Settings saved successfully!');
    }

    toggleNightShift(enabled) {
        this.state.nightShiftActive = enabled;
        const overlay = document.getElementById('night-shift-overlay');
        if (overlay) {
            overlay.classList.toggle('hidden', !enabled);
        }
    }

    toggleAurora(enabled) {
        this.state.auroraActive = enabled;
        document.querySelectorAll('.aurora-glow').forEach(el => {
            el.style.opacity = enabled ? '0.35' : '0';
        });
    }

    exportJournalJSON() {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.state.journalEntries, null, 2));
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute("href", dataStr);
        downloadAnchor.setAttribute("download", `somnia_journal_export_${Date.now()}.json`);
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();
    }

    resetAppData() {
        if (confirm("Are you sure you want to reset all stored sleep journal and setting data?")) {
            localStorage.clear();
            location.reload();
        }
    }
}

// Instantiate global app controller
const app = new SomniaApp();
