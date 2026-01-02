document.addEventListener('gesturestart', (e) => e.preventDefault());
const pathAudio = "audios/";
const pathImg = "img/";

// Global variables for game data
let levels, database;

// Global variables for game state
let configHints = false;
let isProgressiveMode = false;
let isSecondPass = false;
let difficultyThreshold = 70;
let currentLevel = 0;
let score = 0;
let flowState = 'SETUP';
let gameQueue = [];
let currentItem = null;
let currentBoxIndex = 0;
let presentationQueue = [];
let presentationIndex = 0;
let targetIndices = [];
let learnedLetters = new Set();
let phaseCorrectAttempts = 0;
let phaseTotalAttempts = 0;

// All game functions are now global, accessible by onclick attributes
function finishSetup() {
    const checkboxHints = document.getElementById('toggleHints');
    configHints = checkboxHints.checked;
    const checkboxProg = document.getElementById('toggleProgressive');
    isProgressiveMode = checkboxProg.checked;
    const diffSelect = document.getElementById('difficultySelect');
    difficultyThreshold = parseInt(diffSelect.value);
    document.getElementById('screenSetup').classList.add('hidden');
    initLevel(0);
}

function showScreen(screenName) {
    document.getElementById('screenSetup').classList.add('hidden');
    document.getElementById('screenPresentation').classList.add('hidden');
    document.getElementById('screenGame').classList.add('hidden');
    if (screenName === 'PRESENTATION') {
        document.getElementById('screenPresentation').classList.remove('hidden');
    } else if (screenName === 'GAME') {
        document.getElementById('screenGame').classList.remove('hidden');
        document.getElementById('screenGame').classList.add('flex');
    }
}

function initLevel(lvl) {
    currentLevel = lvl;
    isSecondPass = false;
    if (!database[currentLevel]) {
        alert("Parabéns! Fim do Jogo.");
        window.location.reload();
        return;
    }
    learnedLetters = new Set();
    for(let i=0; i<=currentLevel; i++) {
        if(levels[i]) levels[i].unlock.forEach(l => learnedLetters.add(l));
    }
    startIntroSyllables();
}

function startIntroSyllables() {
    flowState = 'INTRO';
    const data = levels[currentLevel];
    const title = currentLevel === 0 ? "Vogais" : `Família do ${data.letter}`;
    const syllables = data.syllables || [];
    let html = `<h2 class="text-5xl font-bold text-blue-500 mb-8 animate__animated animate__fadeInDown">${title}</h2><div class="flex justify-center gap-4 flex-wrap mb-6">`;
    syllables.forEach((syl, idx) => {
        html += `<div class="text-6xl md:text-8xl font-bold bg-white text-blue-500 border-4 border-blue-200 rounded-3xl px-6 py-4 shadow-lg animate__animated animate__zoomIn" style="animation-delay: ${idx*100}ms">${syl}</div>`;
    });
    html += `</div>`;
    document.getElementById('presentationTitle').textContent = "INTRODUÇÃO";
    document.getElementById('presentationContent').innerHTML = html;
    showScreen('PRESENTATION');
}

function startPresentationWords() {
    flowState = 'PRES';
    presentationQueue = [...database[currentLevel].items];
    presentationIndex = 0;
    showNextPresentationWord();
}

function showNextPresentationWord() {
    if (presentationIndex >= presentationQueue.length) {
        if (currentLevel === 0) startWordGame();
        else startSyllableGame();
        return;
    }
    const item = presentationQueue[presentationIndex];
    let mediaHtml = item.image ?
        `<img src="${pathImg + item.image}" class="max-h-60 mx-auto drop-shadow-md animate__animated animate__jackInTheBox" onerror="this.style.display='none'; this.nextElementSibling.style.display='block'"> <span style="display:none" class="text-9xl animate__animated animate__jackInTheBox">${item.emoji}</span>` :
        `<span class="text-9xl animate__animated animate__jackInTheBox">${item.emoji}</span>`;
    let html = `<div class="bg-white border-4 border-purple-200 rounded-3xl p-8 mb-6 shadow-sm w-full max-w-lg mx-auto">${mediaHtml}</div><div class="text-7xl font-bold text-gray-600 tracking-widest uppercase mb-4 animate__animated animate__fadeInUp">${item.word}</div>`;
    document.getElementById('presentationTitle').textContent = "PALAVRAS NOVAS";
    document.getElementById('presentationContent').innerHTML = html;
    showScreen('PRESENTATION');
    playAudio(item.word);
}

function advanceLinearFlow() {
    if (flowState === 'INTRO') startPresentationWords();
    else if (flowState === 'PRES') { presentationIndex++; showNextPresentationWord(); }
    else if (flowState === 'TRANSITION_TO_SYL') startSyllableGame();
    else if (flowState === 'TRANSITION_TO_WORD') startWordGame();
    else if (flowState === 'END_PHASE') initLevel(currentLevel + 1);
    else if (flowState === 'RETRY') { if (currentLevel === 0) startWordGame(); else startSyllableGame(); }
}

function prepareGameQueue() {
    gameQueue = [...database[currentLevel].items].sort(() => Math.random() - 0.5);
    if (isProgressiveMode && !isSecondPass) {
        configHints = true;
    }
    if (!isSecondPass) {
        phaseTotalAttempts = 0;
        phaseCorrectAttempts = 0;
    }
    updateStatsUI();
}

function startSyllableGame() {
    flowState = 'GAME_SYL';
    document.getElementById('gameLevelDisplay').textContent = levels[currentLevel].letter + " (Sílabas)";
    prepareGameQueue();
    showScreen('GAME');
    renderKeyboard();
    nextGameItem();
}

function startWordGame() {
    flowState = 'GAME_WORD';
    document.getElementById('gameLevelDisplay').textContent = levels[currentLevel].letter + " (Palavras)";
    prepareGameQueue();
    showScreen('GAME');
    renderKeyboard();
    nextGameItem();
}

function updateStatsUI() {
    document.getElementById('scoreDisplay').textContent = score;
    let acc = 100;
    if (phaseTotalAttempts > 0) acc = Math.round((phaseCorrectAttempts / phaseTotalAttempts) * 100);
    document.getElementById('accuracyDisplay').textContent = acc + "%";
    const accEl = document.getElementById('accuracyDisplay');
    if(acc < difficultyThreshold && difficultyThreshold > 0) {
        accEl.classList.remove('text-green-600'); accEl.classList.add('text-orange-500');
    } else {
        accEl.classList.remove('text-orange-500'); accEl.classList.add('text-green-600');
    }
}

function nextGameItem() {
    if (gameQueue.length === 0) {
        if (isProgressiveMode && !isSecondPass) {
            isSecondPass = true;
            configHints = false;
            showIntermission();
            return;
        }
        checkEndPhase();
        isSecondPass = false;
        return;
    }
    currentItem = gameQueue.pop();
    const total = database[currentLevel].items.length;
    const progress = ((total - gameQueue.length) / total) * 100;
    document.getElementById('progressBar').style.width = `${progress}%`;
    if (flowState === 'GAME_SYL') {
        document.getElementById('gameInstruction').textContent = "Complete a sílaba:";
        targetIndices = findSyllableIndices(currentItem.word, levels[currentLevel].letter);
        if (targetIndices.length === 0) targetIndices = Array.from({length: currentItem.word.length}, (_, i) => i);
    } else {
        document.getElementById('gameInstruction').textContent = "Escreva a palavra:";
        targetIndices = Array.from({length: currentItem.word.length}, (_, i) => i);
    }
    renderGameRound();
}

function showIntermission() {
    const html = `
        <div class="bg-blue-100 border-4 border-blue-300 rounded-full p-8 mb-6 shadow-sm inline-block animate__animated animate__bounceIn">
            <span class="text-8xl">🙈</span>
        </div>
        <h2 class="text-4xl font-bold text-blue-600 mb-4 animate__animated animate__fadeIn">Agora sem ajuda!</h2>
        <p class="text-xl text-gray-500 max-w-md mx-auto mb-8">Você consegue fazer de novo sem as cores?</p>
        <button onclick="startSecondPass()" class="bg-blue-500 hover:bg-blue-400 text-white text-2xl font-bold py-4 px-10 rounded-2xl shadow-[0_6px_0_rgb(37,99,235)] active:shadow-none active:translate-y-2 transition-all uppercase tracking-widest">
            VAMOS LÁ!
        </button>
    `;
    document.getElementById('presentationTitle').textContent = "DESAFIO";
    document.getElementById('presentationContent').innerHTML = html;
    showScreen('PRESENTATION');
}

function startSecondPass() {
    gameQueue = [...database[currentLevel].items].sort(() => Math.random() - 0.5);
    phaseTotalAttempts = 0;
    phaseCorrectAttempts = 0;
    updateStatsUI();
    showScreen('GAME');
    renderKeyboard();
    nextGameItem();
}

function renderGameRound() {
    document.getElementById('successOverlay').classList.add('hidden');
    const imgContainer = document.getElementById('gameImageContainer');
    if (currentItem.image) {
        imgContainer.innerHTML = `<img src="${pathImg + currentItem.image}" class="max-h-full max-w-full object-contain animate__animated animate__fadeIn" onerror="this.outerHTML='<span class=\\'text-8xl\\'>${currentItem.emoji}</span>'">`;
    } else {
        imgContainer.innerHTML = `<span class="text-8xl animate__animated animate__fadeIn">${currentItem.emoji}</span>`;
    }
    playAudio(currentItem.word);
    const container = document.getElementById('inputContainer');
    container.innerHTML = '';
    currentBoxIndex = targetIndices[0];
    for (let i = 0; i < currentItem.word.length; i++) {
        const div = document.createElement('div');
        div.className = 'letter-box w-12 h-14 md:w-16 md:h-20 border-4 rounded-xl flex items-center justify-center text-3xl md:text-5xl font-bold shadow-sm bg-white m-1';
        div.id = `box-${i}`;
        if (!targetIndices.includes(i)) {
            div.classList.add('filled-static');
            div.textContent = currentItem.word[i];
        } else {
            div.classList.add('text-gray-700', 'border-gray-300');
        }
        container.appendChild(div);
    }
    updateActiveBox();
    setTimeout(updateKeyboardHints, 50);
}

function handleInput(char) {
    if (!document.getElementById('successOverlay').classList.contains('hidden')) return;
    if (currentBoxIndex >= currentItem.word.length) return;
    while (currentBoxIndex < currentItem.word.length && !targetIndices.includes(currentBoxIndex)) currentBoxIndex++;
    if (currentBoxIndex >= currentItem.word.length) return;
    phaseTotalAttempts++;
    const targetChar = currentItem.word[currentBoxIndex];
    const normInput = char.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const normTarget = targetChar.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    if (normInput === normTarget) {
        phaseCorrectAttempts++;
        const box = document.getElementById(`box-${currentBoxIndex}`);
        if(box) {
            box.textContent = targetChar;
            box.classList.remove('active-box');
            box.classList.add('correct', 'animate__animated', 'animate__bounceIn');
        }
        document.getElementById('sndCorrect').currentTime = 0;
        document.getElementById('sndCorrect').play();
        currentBoxIndex++;
        while (currentBoxIndex < currentItem.word.length && !targetIndices.includes(currentBoxIndex)) currentBoxIndex++;
        if (currentBoxIndex >= currentItem.word.length) {
            roundWon();
        } else {
            updateActiveBox();
            updateKeyboardHints();
        }
    } else {
        const box = document.getElementById(`box-${currentBoxIndex}`);
        if(box) {
            box.classList.add('incorrect');
            setTimeout(() => box.classList.remove('incorrect'), 400);
        }
    }
    updateStatsUI();
}

function roundWon() {
    const overlay = document.getElementById('successOverlay');
    overlay.classList.remove('hidden');
    document.getElementById('sndWordWin').currentTime = 0;
    document.getElementById('sndWordWin').play();
    score += 10;
    updateStatsUI();
    fireConfetti();
    document.querySelectorAll('.key').forEach(k => k.classList.remove('hint-active', 'hint-inactive'));
}

function checkEndPhase() {
    const acc = phaseTotalAttempts === 0 ? 0 : (phaseCorrectAttempts / phaseTotalAttempts) * 100;
    let title, msg, nextState;
    if (acc < difficultyThreshold) {
        document.getElementById('sndLose').play();
        title = "Vamos tentar de novo?";
        msg = `Você fez ${Math.round(acc)}%. Precisa de ${difficultyThreshold}% para passar.`;
        nextState = 'RETRY';
        document.getElementById('presentationTitle').textContent = "REVISÃO";
    } else {
        document.getElementById('sndLevelWin').play();
        if (flowState === 'GAME_SYL') {
            title = "Sílabas Completas!";
            msg = "Agora vamos escrever as palavras inteiras.";
            nextState = 'TRANSITION_TO_WORD';
        } else {
            title = "Nível Concluído!";
            const nextLvl = levels[currentLevel + 1];
            msg = nextLvl ? `Você desbloqueou: ${nextLvl.letter}` : "Você terminou o jogo!";
            nextState = 'END_PHASE';
        }
        document.getElementById('presentationTitle').textContent = "PARABÉNS";
    }
    flowState = nextState;
    const isFail = nextState === 'RETRY';
    const colorClass = isFail ? 'text-orange-500' : 'text-green-500';
    const borderClass = isFail ? 'border-orange-200' : 'border-green-200';
    const emoji = isFail ? '💪' : '⭐';
    let html = `<div class="bg-white border-4 ${borderClass} rounded-full p-10 mb-6 shadow-sm inline-block"><span class="text-8xl">${emoji}</span></div><h2 class="text-4xl font-bold ${colorClass} mb-4">${title}</h2><p class="text-xl text-gray-500 max-w-md mx-auto">${msg}</p>`;
    document.getElementById('presentationContent').innerHTML = html;
    showScreen('PRESENTATION');
}

function renderKeyboard() {
    const layout = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"];
    const container = document.getElementById('keyboardContainer');
    container.innerHTML = '';
    layout.forEach(row => {
        const rowDiv = document.createElement('div'); rowDiv.className = "flex justify-center gap-1";
        row.split('').forEach(char => {
            const btn = document.createElement('button'); btn.textContent = char; btn.id = `key-${char}`;
            let btnClass = "key"; if (learnedLetters.has(char)) btnClass += " key-learned";
            btn.className = btnClass;
            btn.addEventListener('touchstart', (e) => { e.preventDefault(); handleInput(char); btn.classList.add('active-press'); });
            btn.addEventListener('touchend', (e) => { e.preventDefault(); btn.classList.remove('active-press'); });
            btn.addEventListener('click', (e) => { handleInput(char); });
            rowDiv.appendChild(btn);
        });
        container.appendChild(rowDiv);
    });
}

function updateKeyboardHints() {
    document.querySelectorAll('.key').forEach(k => k.classList.remove('hint-active', 'hint-inactive'));
    if (!configHints || !currentItem || !document.getElementById('successOverlay').classList.contains('hidden')) return;
    let tempIndex = currentBoxIndex;
    while (tempIndex < currentItem.word.length && !targetIndices.includes(tempIndex)) tempIndex++;
    if (tempIndex < currentItem.word.length) {
        const targetChar = currentItem.word[tempIndex].normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        document.querySelectorAll('.key').forEach(k => {
            const keyChar = k.textContent.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            if (keyChar === targetChar) k.classList.add('hint-active');
            else k.classList.add('hint-inactive');
        });
    }
}

function updateActiveBox() {
    document.querySelectorAll('.letter-box').forEach(b => b.classList.remove('active-box'));
    let tempIndex = currentBoxIndex;
    while (tempIndex < currentItem.word.length && !targetIndices.includes(tempIndex)) tempIndex++;
    if (tempIndex < currentItem.word.length) {
        const current = document.getElementById(`box-${tempIndex}`);
        if (current) current.classList.add('active-box');
    }
}

function findSyllableIndices(word, levelLetter) {
    const indices = [];
    const regex = new RegExp(`(${levelLetter})[AEOIUÁÉÍÓÚÃÕÂÊÔ]`, 'i');
    const match = word.match(regex);
    if (match && match.index !== undefined) { indices.push(match.index, match.index + 1); }
    else if (word.toUpperCase().startsWith(levelLetter)) { indices.push(0, 1); }
    return indices;
}

function playAudio(text) {
    const fn = text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") + ".mp3";
    new Audio(pathAudio + fn).play().catch(()=>{});
}
window.playCurrentAudio = () => { if(currentItem) playAudio(currentItem.word); };

const canvas = document.getElementById('confetti-canvas');
const ctx = canvas.getContext('2d');
let particles = [];
function resizeCanvas() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
window.addEventListener('resize', resizeCanvas);
resizeCanvas();
function fireConfetti() { for (let i = 0; i < 100; i++) particles.push({ x: window.innerWidth/2, y: window.innerHeight/2, vx: (Math.random()-0.5)*15, vy: (Math.random()-0.5)*15, size: Math.random()*8+4, color: `hsl(${Math.random()*360},100%,50%)`, life: 100 }); requestAnimationFrame(animateConfetti); }
function animateConfetti() { ctx.clearRect(0, 0, canvas.width, canvas.height); particles = particles.filter(p => p.life > 0); particles.forEach(p => { p.x += p.vx; p.y += p.vy; p.vy += 0.2; p.life--; ctx.fillStyle = p.color; ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2); ctx.fill(); }); if (particles.length > 0) requestAnimationFrame(animateConfetti); }

// Initialization logic
document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.querySelector('#screenSetup button');
    startButton.disabled = true;
    startButton.textContent = 'Carregando...';

    fetch('database.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            levels = data.levels;
            database = data.database;
            startButton.disabled = false;
            startButton.textContent = 'COMEÇAR ➔';
        })
        .catch(error => {
            console.error('Error loading database:', error);
            startButton.textContent = 'Erro ao Carregar';
            startButton.style.backgroundColor = '#ef4444'; // Red color for error
        });
});