// Simple working version with navigation
import { Login } from './pages/Login.js';
import { Upload } from './pages/Upload-simple.js';
import { Features } from './pages/Features.js';

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
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const title = formData.get('title');
      const description = formData.get('description');
      const prd_text = formData.get('prd_text');
      
      if (title && description && prd_text) {
        showToast('Feature submitted for analysis!', 'success');
        console.log('Feature submitted:', { title, description, prd_text });
        
        // Simulate analysis and create analyzed feature
        setTimeout(() => {
          // Generate a random classification result
          const classifications = [
            { flag: 'Yes', confidence: 0.92, regulations: ['GDPR Article 8', 'CA Privacy Act'] },
            { flag: 'No', confidence: 0.88, regulations: [] },
            { flag: 'Maybe', confidence: 0.65, regulations: ['EU Digital Services Act'] }
          ];
          const randomClassification = classifications[Math.floor(Math.random() * classifications.length)];
          
          // Store the analyzed feature globally
          analyzedFeature = {
            id: 'feat_analyzed_' + Date.now(),
            title: title.trim(),
            description: description.trim(),
            flag: randomClassification.flag,
            confidence: randomClassification.confidence,
            regulations: randomClassification.regulations,
            created_at: new Date().toISOString(),
            review_status: 'none',
            prd_content: prd_text.trim()
          };
          
          showToast(`Analysis complete! Classification: ${randomClassification.flag} - Redirecting to Features...`, 'success');
          
          // Redirect to features page after a short delay
          setTimeout(() => {
            navigateTo('/features');
          }, 1500);
        }, 2000);
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
  
  // Simulate document parsing
  setTimeout(() => {
    showToast('Document parsed successfully!', 'success');
    
    // Simulate extracted data - in real implementation, this would come from document parsing
    const extractedData = {
      title: 'Smart Content Filter for Global Markets',
      description: 'An AI-powered content filtering system designed to automatically detect and moderate inappropriate content across different geographical regions while respecting local cultural and regulatory differences.',
      content: `Feature Title: Smart Content Filter for Global Markets

Description: An AI-powered content filtering system designed to automatically detect and moderate inappropriate content across different geographical regions while respecting local cultural and regulatory differences.

Technical Requirements:
- Real-time content analysis using machine learning models
- Support for 15+ languages and regional dialects
- Configurable sensitivity levels per region
- Integration with existing moderation workflows
- Performance target: <200ms response time

Implementation Details:
- Deploy region-specific ML models
- Implement geo-location based rule sets
- Create admin dashboard for configuration
- Add user appeal mechanisms
- Ensure GDPR compliance for EU users

Geographical Considerations:
- EU: Strict privacy requirements under GDPR
- US: First Amendment considerations
- APAC: Varied regulatory frameworks per country
- Content policies must adapt to local laws`
    };
    
    // Fill the form with extracted data
    fillFormFields(extractedData);
    
    // Show the parsed info notification
    document.getElementById('parsed-info').style.display = 'block';
    
  }, 2000);
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

function sendToEmail(featureId) {
  showToast('Feature details will be sent to your email address.', 'success');
  // Here you would implement actual email sending functionality
}

function exportDetails(featureId) {
  showToast('Feature details exported successfully.', 'success');
  // Here you would implement actual export functionality
}

// Make functions global for onclick handlers
window.navigateTo = navigateTo;
window.logout = logout;
window.showToast = showToast;
window.handleFileUpload = handleFileUpload;
window.parseDocument = parseDocument;
window.toggleFeatureDetails = toggleFeatureDetails;
window.sendToEmail = sendToEmail;
window.exportDetails = exportDetails;

document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded');
  handleRoute();
});

// Handle browser back/forward
window.addEventListener('popstate', () => {
  handleRoute();
});
