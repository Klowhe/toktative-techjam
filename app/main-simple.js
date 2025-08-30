// Simple working version with navigation
import { Login } from './pages/Login.js';
import { Upload } from './pages/Upload-simple.js';
import { Features } from './pages/Features.js';
import { realApi } from './api/realAdapter.js';

console.log('Main.js loaded');

let currentUser = null;
let analyzedFeature = null; // Store the latest analyzed feature

// Simple router
function navigateTo(path) {
  window.history.pushState({}, '', path);
  handleRoute();
}

function handleRoute() {
  const path = window.location.pathname;
  const root = document.getElementById('root');
  
  if (!root) {
    console.error('Root element not found!');
    return;
  }
  
  if (!currentUser && path !== '/login' && path !== '/') {
    // Redirect to login if not authenticated
    navigateTo('/login');
    return;
  }
  
  try {
    switch (path) {
      case '/':
      case '/login':
        root.innerHTML = Login();
        setupLoginHandler();
        break;
      case '/upload':
        root.innerHTML = Upload();
        setupUploadHandler();
        checkBackendStatus();
        break;
      case '/features':
        root.innerHTML = Features(analyzedFeature);
        break;
      default:
        navigateTo('/login');
    }
  } catch (error) {
    console.error('Error rendering page:', error);
    root.innerHTML = `<div style="color: red; padding: 20px;">Error: ${error.message}</div>`;
  }
}

function setupLoginHandler() {
  const form = document.getElementById('login-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const name = formData.get('name');
      const email = formData.get('email');
      
      if (name && email) {
        currentUser = { name: name.trim(), email: email.trim() };
        console.log('User logged in:', currentUser);
        showToast(`Welcome, ${currentUser.name}!`, 'success');
        
        setTimeout(() => {
          navigateTo('/upload');
        }, 1000);
      }
    });
  }
}

function setupUploadHandler() {
  const form = document.getElementById('upload-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const title = formData.get('title');
      const description = formData.get('description');
      const prd_text = formData.get('prd_text');
      
      if (title && description && prd_text) {
        showToast('Feature submitted for analysis!', 'info');
        console.log('Feature submitted:', { title, description, prd_text });
        
        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Analyzing...';
        submitButton.disabled = true;
        
        try {
          // Call real API for analysis
          const result = await realApi.analyzeFeature({
            title: title.trim(),
            description: description.trim(),
            prd_text: prd_text.trim()
          });
          
          if (result.success) {
            // Store the analyzed feature and metadata globally
            analyzedFeature = result.feature;
            window.analyzedFeature = result.feature;
            window.rawAnalysis = result.raw_analysis;
            window.lastAnalysisMetadata = {
              raw_analysis: result.raw_analysis,
              retrieved_documents: result.retrieved_documents,
              mode: result.mode
            };
            
            showToast(`Analysis complete! Classification: ${result.feature.flag} - Redirecting to Features...`, 'success');
            
            // Log analysis details
            console.log('Analysis result:', result);
            if (result.raw_analysis) {
              console.log('Raw analysis:', result.raw_analysis);
            }
            
            // Redirect to features page after a short delay
            setTimeout(() => {
              navigateTo('/features');
            }, 1500);
          } else {
            throw new Error('Analysis failed');
          }
          
        } catch (error) {
          console.error('Analysis error:', error);
          showToast(`Analysis failed: ${error.message}`, 'error');
        } finally {
          // Reset button state
          submitButton.textContent = originalText;
          submitButton.disabled = false;
        }
      }
    });
  }
}

function parseDocument() {
  const fileInput = document.getElementById('document-input');
  const file = fileInput.files[0];
  
  if (!file) {
    showToast('Please select a document to upload', 'error');
    return;
  }
  
  showToast('Parsing document...', 'info');
  console.log('Parsing document:', file.name);
  
    // Create FormData to send file to backend
  const formData = new FormData();
  formData.append('document', file);
  
  // Call backend parse endpoint
  fetch('http://localhost:5001/api/parse', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      showToast('Document parsed successfully!', 'success');
      
      // Fill the form with extracted data
  fillFormFields(data.extracted_data);
  
  // Show the parsed info notification
  document.getElementById('parsed-info').style.display = 'block';
} else {
  showToast(data.error || 'Failed to parse document', 'error');
}
})
.catch(error => {
console.error('Error parsing document:', error);
showToast('Error parsing document. Please try manual entry.', 'error');
});
}

// Feature action functions
function sendToEmail(featureId) {
  const feature = window.analyzedFeature;
  if (!feature) {
    showToast('No feature data available', 'error');
    return;
  }
  
  // Create modal to ask for email address
  const modal = document.createElement('div');
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  `;
  
  const modalContent = document.createElement('div');
  modalContent.style.cssText = `
    background: white;
    padding: 2rem;
    border-radius: 12px;
    max-width: 500px;
    width: 90%;
    position: relative;
  `;
  
  modalContent.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
      <h3 style="margin: 0; color: #1f2937;">Send Analysis Report</h3>
      <button onclick="this.closest('.email-modal').remove()" style="background: #ef4444; color: white; border: none; border-radius: 6px; padding: 0.5rem 1rem; cursor: pointer;">Cancel</button>
    </div>
    <div style="margin-bottom: 1.5rem;">
      <p style="color: #6b7280; margin-bottom: 1rem;">Enter the email address where you want to send the analysis report for "${feature.title}":</p>
      <input type="email" id="email-input" placeholder="user@example.com" required 
             style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 6px; font-size: 1rem;" />
    </div>
    <div style="display: flex; gap: 0.75rem; justify-content: flex-end;">
      <button onclick="this.closest('.email-modal').remove()" style="padding: 0.75rem 1.5rem; background: #6b7280; color: white; border: none; border-radius: 6px; cursor: pointer;">Cancel</button>
      <button onclick="sendEmailReport()" style="padding: 0.75rem 1.5rem; background: #009995; color: white; border: none; border-radius: 6px; cursor: pointer;">Send Email</button>
    </div>
  `;
  
  modal.className = 'email-modal';
  modal.appendChild(modalContent);
  document.body.appendChild(modal);
  
  // Focus on email input
  setTimeout(() => {
    document.getElementById('email-input').focus();
  }, 100);
  
  // Close modal on outside click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  });
  
  // Handle Enter key
  document.getElementById('email-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendEmailReport();
    }
  });
}

function sendEmailReport() {
  const emailInput = document.getElementById('email-input');
  const email = emailInput.value.trim();
  
  if (!email) {
    showToast('Please enter an email address', 'error');
    return;
  }
  
  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    showToast('Please enter a valid email address', 'error');
    return;
  }
  
  const feature = window.analyzedFeature;
  const modal = document.querySelector('.email-modal');
  
  // Show loading state
  modal.querySelector('button[onclick="sendEmailReport()"]').textContent = 'Sending...';
  modal.querySelector('button[onclick="sendEmailReport()"]').disabled = true;
  
  // Prepare email data
  const emailData = {
    to: email,
    subject: `Regulatory Analysis Report: ${feature.title}`,
    feature: feature,
    raw_analysis: window.rawAnalysis
  };
  
  // Send email via backend
  fetch('http://localhost:5001/api/send-email', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(emailData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      showToast(`Analysis report sent successfully to ${email}`, 'success');
      modal.remove();
    } else {
      throw new Error(data.error || 'Failed to send email');
    }
  })
  .catch(error => {
    console.error('Error sending email:', error);
    showToast(`Failed to send email: ${error.message}`, 'error');
    // Reset button state
    modal.querySelector('button[onclick="sendEmailReport()"]').textContent = 'Send Email';
    modal.querySelector('button[onclick="sendEmailReport()"]').disabled = false;
  });
}

function exportDetails(featureId) {
  const feature = window.analyzedFeature;
  if (!feature) {
    showToast('No feature data available', 'error');
    return;
  }
  
  // Create CSV content
  const csvContent = [
    ['Field', 'Value'],
    ['Feature Title', feature.title],
    ['Description', feature.description],
    ['Regulatory Flag', feature.flag],
    ['Confidence', `${Math.round(feature.confidence * 100)}%`],
    ['Age Group', feature.age],
    ['Risk Level', feature.risk_level],
    ['Analysis Date', new Date(feature.created_at).toLocaleString()],
    ['Reasoning', feature.reasoning],
    ['Regulations', feature.regulations?.join('; ') || 'None'],
    ['Business Impact', feature.business_impact],
    ['Technical Complexity', feature.technical_complexity],
    ['Rollout Timeline', feature.rollout_timeline],
    ['Stakeholders', feature.stakeholders?.join('; ') || 'None'],
    ['Regions Affected', feature.regions_affected?.join('; ') || 'None']
  ].map(row => row.map(field => `"${field.replace(/"/g, '""')}"`).join(',')).join('\n');
  
  // Create and download file
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `regulatory-analysis-${feature.title.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
  
  showToast('Analysis details exported as CSV', 'success');
}

function viewRawAnalysis(featureId) {
  const feature = window.analyzedFeature;
  const rawAnalysis = window.rawAnalysis;
  
  if (!rawAnalysis) {
    showToast('No raw analysis data available', 'error');
    return;
  }
  
  // Create modal for raw analysis
  const modal = document.createElement('div');
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  `;
  
  const modalContent = document.createElement('div');
  modalContent.style.cssText = `
    background: white;
    padding: 2rem;
    border-radius: 12px;
    max-width: 80%;
    max-height: 80%;
    overflow-y: auto;
    position: relative;
  `;
  
  modalContent.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
      <h3 style="margin: 0; color: #1f2937;">Full AI Analysis Report</h3>
      <button onclick="this.closest('.modal').remove()" style="background: #ef4444; color: white; border: none; border-radius: 6px; padding: 0.5rem 1rem; cursor: pointer;">Close</button>
    </div>
    <div style="background: #f9fafb; padding: 1.5rem; border-radius: 8px; border: 1px solid #e5e7eb;">
      <h4 style="margin: 0 0 1rem 0; color: #374151;">Feature: ${feature?.title || 'Unknown'}</h4>
      <pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.875rem; line-height: 1.5; color: #1f2937; margin: 0;">${rawAnalysis}</pre>
    </div>
  `;
  
  modal.className = 'modal';
  modal.appendChild(modalContent);
  document.body.appendChild(modal);
  
  // Close modal on outside click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  });
}

function fillFormFields(data) {
  document.getElementById('title-input').value = data.title;
  document.getElementById('description-input').value = data.description;
  document.getElementById('content-input').value = data.content;
}

function handleFileUpload(event) {
  const file = event.target.files[0];
  const fileInfo = document.getElementById('file-info');
  const fileName = document.getElementById('file-name');
  const parseBtn = document.getElementById('parse-btn');
  
  if (file) {
    fileName.textContent = file.name;
    fileInfo.style.display = 'block';
    parseBtn.disabled = false;
    parseBtn.style.background = '#009995';
    parseBtn.style.cursor = 'pointer';
    parseBtn.textContent = 'Parse Document';
  } else {
    fileInfo.style.display = 'none';
    parseBtn.disabled = true;
    parseBtn.style.background = '#6b7280';
    parseBtn.style.cursor = 'not-allowed';
  }
}

function logout() {
  currentUser = null;
  showToast('Logged out successfully', 'info');
  navigateTo('/login');
}

function showToast(message, type = 'success') {
  // Remove existing toast
  const existingToast = document.querySelector('.toast');
  if (existingToast) {
    existingToast.remove();
  }
  
  const colors = {
    success: '#22c55e',
    error: '#ef4444',
    info: '#3b82f6'
  };
  
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${colors[type] || colors.success};
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
  `;
  toast.textContent = message;
  
  // Add CSS animation
  if (!document.querySelector('#toast-styles')) {
    const style = document.createElement('style');
    style.id = 'toast-styles';
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
    `;
    document.head.appendChild(style);
  }
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// Check backend API status
async function checkBackendStatus() {
  const statusElement = document.getElementById('backend-status');
  if (!statusElement) return;
  
  try {
    const health = await realApi.checkHealth();
    if (health.healthy) {
      statusElement.textContent = 'AI Backend Online';
      statusElement.style.background = '#22c55e';
      statusElement.style.color = 'white';
    } else {
      statusElement.textContent = 'Backend Offline (Mock Mode)';
      statusElement.style.background = '#f59e0b';
      statusElement.style.color = 'white';
    }
  } catch (error) {
    statusElement.textContent = 'Backend Offline (Mock Mode)';
    statusElement.style.background = '#f59e0b';
    statusElement.style.color = 'white';
  }
}

// Global functions for collapsible features
function toggleFeatureDetails(featureId) {
  const detailsRow = document.getElementById(featureId + '-details');
  const arrow = document.getElementById('arrow-' + featureId);
  
  if (detailsRow && arrow) {
    if (detailsRow.style.display === 'none' || detailsRow.style.display === '') {
      detailsRow.style.display = 'table-row';
      arrow.style.transform = 'rotate(90deg)';
    } else {
      detailsRow.style.display = 'none';
      arrow.style.transform = 'rotate(0deg)';
    }
  }
}

// Make functions global for onclick handlers
window.navigateTo = navigateTo;
window.logout = logout;
window.showToast = showToast;
window.handleFileUpload = handleFileUpload;
window.parseDocument = parseDocument;
window.toggleFeatureDetails = toggleFeatureDetails;
window.sendToEmail = sendToEmail;
window.sendEmailReport = sendEmailReport;
window.exportDetails = exportDetails;

document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded');
  handleRoute();
});

// Handle browser back/forward
window.addEventListener('popstate', () => {
  handleRoute();
});
