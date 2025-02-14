// Add this at the top
const API_URL = "https://prosthetic-advisor.onrender.com"; // Render URL

// Replace showRecommendation() function
async function showRecommendation() {
  try {
    const response = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        ambulation: responses.ambulation,
        stability: responses.stability,
        risk: responses.risk
      })
    });
    
    const data = await response.json();
    
    // Update UI
    document.getElementById('recommendation-text').innerHTML = `
      <h3>Recommended: ${data.recommendation}</h3>
      <p>Confidence: ${Math.round(data.confidence * 100)}%</p>
      <div class="evidence-section">
        <h4>Clinical Evidence:</h4>
        <ul>${data.evidence.map(e => `<li>${e}</li>`).join('')}</ul>
      </div>
      <div class="guidelines">
        <h4>Applied Guidelines:</h4>
        <ul>${data.clinical_rules.map(r => `<li>${r}</li>`).join('')}</ul>
      </div>
    `;
    
  } catch (error) {
    document.getElementById('recommendation-text').innerHTML = `
      <p class="error">Recommendation service unavailable. Using fallback rules.</p>
    `;
    // Add fallback rule-based logic here
  }
}
