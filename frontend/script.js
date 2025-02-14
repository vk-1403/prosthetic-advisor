let currentStep = 0;
let responses = {};
let demographics = {};
const totalSteps = 5; // Welcome + Demographics + 3 assessment steps
const API_URL = "https://your-render-service.onrender.com"; // Replace with your Render URL

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.option-card').forEach(card => {
        card.addEventListener('click', handleOptionClick);
    });
});

// Event Handlers
function handleOptionClick() {
    this.parentElement.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
    this.classList.add('selected');
    responses[this.dataset.category] = this.dataset.value;
    setTimeout(progressToNextStep, 300);
}

// Navigation Functions
function showDemographics() {
    document.getElementById('welcome').style.display = 'none';
    document.getElementById('demographics').style.display = 'block';
    currentStep = 1;
    updateProgress();
}

function backToWelcome() {
    document.getElementById('welcome').style.display = 'block';
    document.getElementById('demographics').style.display = 'none';
    currentStep = 0;
    updateProgress();
}

function startAssessment() {
    const requiredFields = ['patientName', 'patientAge', 'patientGender',
                           'patientCountry', 'patientState', 'clinicianName'];
    for(const fieldId of requiredFields) {
        const field = document.getElementById(fieldId);
        if(!field.value.trim()) {
            alert(`Please fill in ${field.labels[0].textContent}`);
            field.focus();
            return;
        }
    }

    demographics = {
        name: document.getElementById('patientName').value,
        age: document.getElementById('patientAge').value,
        gender: document.getElementById('patientGender').value,
        country: document.getElementById('patientCountry').value,
        state: document.getElementById('patientState').value,
        clinician: document.getElementById('clinicianName').value
    };

    document.getElementById('demographics').style.display = 'none';
    document.getElementById('step1').style.display = 'block';
    currentStep = 2;
    updateProgress();
}

// ML Integration
async function getMLRecommendation() {
    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ambulation: responses.ambulation,
                stability: responses.stability,
                risk: responses.risk,
                age: demographics.age,
                gender: demographics.gender
            })
        });
        
        if (!response.ok) throw new Error('API Error');
        return await response.json();
    } catch (error) {
        console.error('ML API failed, using fallback');
        return getRuleBasedRecommendation();
    }
}

async function logDecision(recommendation) {
    try {
        await fetch(`${API_URL}/collect-data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...demographics,
                ...responses,
                recommendation: recommendation
            })
        });
    } catch (error) {
        console.error('Data collection failed');
    }
}

// Recommendation Flow
async function showRecommendation() {
    document.querySelectorAll('.assessment-card').forEach(card => card.style.display = 'none');
    document.getElementById('result').style.display = 'block';
    
    const mlResponse = await getMLRecommendation();
    await logDecision(mlResponse.recommendation);
    
    document.getElementById('recommendation-text').innerHTML = `
        <h3>Recommended: ${mlResponse.recommendation}</h3>
        <p>AI Confidence: ${Math.round(mlResponse.confidence * 100)}%</p>
    `;
    
    document.getElementById('patient-summary').innerHTML = `
        <h4>Patient Summary</h4>
        <p>${demographics.name}, ${demographics.age}yo ${demographics.gender}<br>
        Location: ${demographics.state}, ${demographics.country}<br>
        Clinician: ${demographics.clinician}</p>
    `;
    
    document.querySelector('#confidence-meter::after').style.width = 
        `${Math.round(mlResponse.confidence * 100)}%`;
}

// Utility Functions
function progressToNextStep() {
    if(currentStep < totalSteps-1) {
        document.getElementById(`step${currentStep-1}`).style.display = 'none';
        currentStep++;
        document.getElementById(`step${currentStep-1}`).style.display = 'block';
        updateProgress();
    } else {
        showRecommendation();
    }
}

function previousStep() {
    if(currentStep > 2) {
        document.getElementById(`step${currentStep-1}`).style.display = 'none';
        currentStep--;
        document.getElementById(`step${currentStep-1}`).style.display = 'block';
        updateProgress();
    } else if(currentStep === 2) {
        document.getElementById('step1').style.display = 'none';
        document.getElementById('demographics').style.display = 'block';
        currentStep = 1;
        updateProgress();
    }
}

function updateProgress() {
    const progress = (currentStep / totalSteps) * 100;
    document.getElementById('progress').style.width = `${progress}%`;
}

function restartAssessment() {
    currentStep = 0;
    responses = {};
    demographics = {};
    document.getElementById('welcome').style.display = 'block';
    document.getElementById('result').style.display = 'none';
    document.getElementById('progress').style.width = '0';
    document.querySelectorAll('.option-card').forEach(card => card.classList.remove('selected'));
    document.querySelectorAll('input, select').forEach(field => field.value = '');
}

// Fallback Recommendation System
function getRuleBasedRecommendation() {
    // ... (keep your original rule-based logic here as fallback)
}