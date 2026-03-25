const API_URL = 'http://localhost:8000/analyze';

// DOM Elements
const jobInput = document.getElementById('jobInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const btnText = document.querySelector('.btn-text');
const spinner = document.querySelector('.spinner');
const errorMsg = document.getElementById('errorMsg');

const placeholderPanel = document.getElementById('placeholderPanel');
const resultsPanel = document.getElementById('resultsPanel');

const scoreCircle = document.getElementById('scoreCircle');
const scoreText = document.getElementById('scoreText');
const verdictBadge = document.getElementById('verdictBadge');
const explanationText = document.getElementById('explanationText');
const riskFactorsList = document.getElementById('riskFactorsList');
const recBox = document.getElementById('recBox');
const recText = document.getElementById('recText');

// Event Listeners
analyzeBtn.addEventListener('click', handleAnalyze);
clearBtn.addEventListener('click', clearInput);

function clearInput() {
    jobInput.value = '';
    jobInput.focus();
}

async function handleAnalyze() {
    const text = jobInput.value.trim();
    
    if (!text) {
        showError('Please paste a job description first.');
        return;
    }
    
    // UI Loading State
    hideError();
    analyzeBtn.disabled = true;
    btnText.textContent = 'Analyzing...';
    spinner.classList.remove('hidden');
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            throw new Error('Failed to analyze the post. Server may be down.');
        }
        
        const data = await response.json();
        renderResults(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        analyzeBtn.disabled = false;
        btnText.textContent = 'Analyze Post';
        spinner.classList.add('hidden');
    }
}

function renderResults(data) {
    placeholderPanel.classList.add('hidden');
    resultsPanel.classList.remove('hidden');
    
    const { verdict, spam_score, analysis } = data;
    
    // Update Score Circle (Gauge)
    // Formula for stroke-dasharray: value, 100
    // Spam score is 0-100. Let's animate it.
    setTimeout(() => {
        scoreCircle.setAttribute('stroke-dasharray', `${spam_score}, 100`);
    }, 100);
    
    scoreText.textContent = `${Math.round(spam_score)}%`;
    
    // Update Badge & Colors
    verdictBadge.textContent = verdict;
    verdictBadge.className = 'badge'; // Reset classes
    scoreCircle.className.baseVal = 'circle'; // Reset SVG classes
    recBox.style.borderColor = 'rgba(255,255,255,0.1)';
    recBox.style.background = 'rgba(0,0,0,0.2)';
    
    if (verdict === 'FAKE') {
        verdictBadge.classList.add('fake');
        scoreCircle.classList.add('stroke-fake');
        recBox.style.borderColor = 'rgba(239, 68, 68, 0.3)';
        recBox.style.background = 'var(--fake-bg)';
    } else if (verdict === 'SUSPICIOUS') {
        verdictBadge.classList.add('suspicious');
        scoreCircle.classList.add('stroke-suspicious');
        recBox.style.borderColor = 'rgba(245, 158, 11, 0.3)';
        recBox.style.background = 'var(--suspicious-bg)';
    } else {
        verdictBadge.classList.add('legit');
        scoreCircle.classList.add('stroke-legit');
        recBox.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        recBox.style.background = 'var(--legit-bg)';
        // For legit, spam score is usually low, but we show the Confidence in Legit instead
        // or just let it be low. Let's explicitly show it's safe.
    }
    
    // Update LLM Text
    explanationText.textContent = analysis.explanation;
    recText.textContent = analysis.recommendation;
    
    // Update Risk Factors
    riskFactorsList.innerHTML = '';
    
    if (analysis.risk_factors && analysis.risk_factors.length > 0) {
        analysis.risk_factors.forEach(factor => {
            const li = document.createElement('li');
            li.textContent = factor;
            
            // Apply visual class based on verdict
            if (verdict === 'FAKE') li.classList.add('alert-factor');
            else if (verdict === 'SUSPICIOUS') li.classList.add('warn-factor');
            else li.classList.add('safe-factor');
            
            riskFactorsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No specific risk markers detected.';
        li.classList.add('safe-factor');
        riskFactorsList.appendChild(li);
    }
}

function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.classList.remove('hidden');
}

function hideError() {
    errorMsg.classList.add('hidden');
}
