// DOM Elements
const arabicInput = document.getElementById('arabicInput');
const translateBtn = document.getElementById('translateBtn');
const loadingDiv = document.getElementById('loadingIndicator');
const searchInput = document.getElementById('searchInput');
const wordListDiv = document.getElementById('wordList');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const pageInfo = document.getElementById('pageInfo');

// API Configuration
const API_URL = `${window.location.protocol}//${window.location.hostname}:5000/api`;
const sessionId = 'session_' + Date.now();

// Pagination State
let currentPage = 1;
let totalPages = 1;
const wordsPerPage = 10;
let currentSearch = '';

// Initialize app
window.addEventListener('load', () => {
    arabicInput.focus();
    loadWordList();
    
    // Setup hamburger menu
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');
    
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }
});

// Translate and Add Word
async function translateAndAdd() {
    const word = arabicInput.value.trim();
    
    if (!word) {
        alert('Please enter an Arabic word');
        return;
    }
    
    try {
        // Disable button and show loading
        translateBtn.disabled = true;
        loadingDiv.style.display = 'block';
        
        // Step 1: Translate the word
        const translateResponse = await fetch(`${API_URL}/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ word })
        });
        
        const translateResult = await translateResponse.json();
        
        if (!translateResult.success) {
            throw new Error('Translation failed');
        }
        
        // Step 2: Save to database
        const saveResponse = await fetch(`${API_URL}/words`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                words: [{
                    word: translateResult.word,
                    translation: translateResult.translation,
                    phonetic: translateResult.phonetic,
                    sentence: translateResult.sentence,
                    arabic_sentence: translateResult.arabic_sentence
                }],
                sessionId: sessionId
            })
        });
        
        const saveResult = await saveResponse.json();
        
        if (!saveResult.success) {
            throw new Error('Failed to save word');
        }
        
        // Step 3: Clear input and reload list
        arabicInput.value = '';
        arabicInput.focus();
        await loadWordList();
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error translating word. Please make sure the server is running.');
    } finally {
        translateBtn.disabled = false;
        loadingDiv.style.display = 'none';
    }
}

// Load Word List with Pagination
async function loadWordList(page = 1, search = '') {
    try {
        const params = new URLSearchParams({
            limit: wordsPerPage,
            offset: (page - 1) * wordsPerPage
        });
        
        if (search) {
            params.append('search', search);
        }
        
        const response = await fetch(`${API_URL}/words?${params}`);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error('Failed to load words');
        }
        
        const words = result.words || [];
        const total = result.total || 0;
        
        // Update pagination state
        currentPage = page;
        totalPages = Math.ceil(total / wordsPerPage) || 1;
        currentSearch = search;
        
        // Render word list
        renderWordList(words);
        updatePagination();
        
    } catch (error) {
        console.error('Error loading words:', error);
        wordListDiv.innerHTML = `
            <div class="empty-state">
                <p>Error loading words</p>
                <p style="font-size: 0.9rem;">Make sure the server is running</p>
            </div>
        `;
    }
}

// Render Word List
function renderWordList(words) {
    if (words.length === 0) {
        wordListDiv.innerHTML = `
            <div class="empty-state">
                <p>No words yet</p>
                <p style="font-size: 0.9rem;">Add your first Arabic word to get started!</p>
            </div>
        `;
        return;
    }
    
    const wordItems = words.map(word => {
        return `
            <div class="vocab-card">
                <div class="card-header">
                    <button class="audio-btn" onclick="playAudio('${word.word}', ${word.id})" title="Play audio">
                        <span class="material-symbols-outlined">volume_up</span>
                    </button>
                    <div class="card-arabic-word">${word.word}</div>
                    <button class="delete-btn" onclick="deleteWord(${word.id})" title="Delete">
                        <span class="material-symbols-outlined">delete</span>
                    </button>
                </div>
                <div class="card-body">
                    <div class="word-info-row">
                        <div class="info-column">
                            <div class="label">Phonetic</div>
                            <div class="phonetic">${word.phonetic || ''}</div>
                        </div>
                        <div class="info-column">
                            <div class="label">English</div>
                            <div class="meaning">${word.translation}</div>
                        </div>
                    </div>
                    
                    ${word.sentence || word.arabic_sentence ? `
                        <div class=\"label\" style=\"text-align: center;\">Example</div>
                        <div class=\"example-box\">
                            ${word.arabic_sentence ? `<div class=\"example-ar\">${word.arabic_sentence}</div>` : ''}
                            ${word.sentence ? `<div class=\"example-en\">${word.sentence}</div>` : ''}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    wordListDiv.innerHTML = wordItems;
}

// Update Pagination Controls
function updatePagination() {
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
}

// Delete Word
async function deleteWord(wordId) {
    if (!confirm('Are you sure you want to delete this word?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/words/${wordId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error('Failed to delete word');
        }
        
        // Reload current page
        await loadWordList(currentPage, currentSearch);
        
    } catch (error) {
        console.error('Error deleting word:', error);
        alert('Error deleting word');
    }
}

// Play Audio (placeholder for future implementation)
function playAudio(arabicWord, wordId) {
    // TODO: Implement text-to-speech or audio playback
    console.log('Play audio for:', arabicWord);
    alert('Audio playback coming soon!');
}

// Play Audio (placeholder for future implementation)
function playAudio(arabicWord, wordId) {
    // TODO: Implement text-to-speech or audio playback
    console.log('Play audio for:', arabicWord);
    alert('Audio playback coming soon!');
}

// Search Handler (debounced)
let searchTimeout;
searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        loadWordList(1, e.target.value.trim());
    }, 300);
});

// Pagination Handlers
prevBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        loadWordList(currentPage - 1, currentSearch);
    }
});

nextBtn.addEventListener('click', () => {
    if (currentPage < totalPages) {
        loadWordList(currentPage + 1, currentSearch);
    }
});

// Translate Button Handler
translateBtn.addEventListener('click', translateAndAdd);

// Enter Key Handler
arabicInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        translateAndAdd();
    }
});

