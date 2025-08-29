export function Upload() {
  return `
    <div style="min-height: 100vh; background: #ffffff; color: #1f2937;">
      <!-- Navigation -->
      <nav style="background: #121415; padding: 0 2rem; margin: 0; width: 100%; box-sizing: border-box;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h1 style="color: #FF3361; font-size: 1.5rem; font-weight: bold; margin: 0;">GeoReg Classifier</h1>
          <div style="display: flex; gap: 0; align-items: center; position: relative;">
            <div style="display: flex; flex-direction: column; align-items: center; position: relative; height: 60px; justify-content: center;">
              <button onclick="navigateTo('/upload')" style="padding: 0.75rem 1.5rem; background: transparent; color: white; border: none; cursor: pointer; font-size: 0.875rem;">Upload</button>
              <div style="width: 25%; height: 4px; background: #009995; border-radius: 2px; position: absolute; bottom: 8px;"></div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center; position: relative; height: 60px; justify-content: center;">
              <button onclick="navigateTo('/features')" style="padding: 0.75rem 1.5rem; background: transparent; color: #88898a; border: none; cursor: pointer; font-size: 0.875rem;">Features</button>
            </div>
            <button onclick="logout()" style="padding: 0.5rem 1rem; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; margin-left: auto;">Logout</button>
          </div>
        </div>
      </nav>

      <!-- Main Content -->
      <div style="padding: 20px; max-width: 800px; margin: 0 auto;">
        <div style="background: #f9fafb; padding: 2rem; border-radius: 12px; border: 1px solid #e5e7eb;">
          <h2 style="color: #1f2937; margin-bottom: 1rem; font-size: 1.5rem;">Upload PRD/TRD for Classification</h2>
          <p style="color: #6b7280; margin-bottom: 2rem;">Upload a document to auto-parse or manually enter your Product Requirements Document or Technical Requirements Document for geo-regulatory compliance analysis.</p>
          
          <!-- Document Upload Section -->
          <div style="margin-bottom: 2rem;">
            <label style="display: block; color: #374151; margin-bottom: 0.5rem; font-weight: 500;">Document Upload (Optional)</label>
            <div style="border: 2px dashed #d1d5db; border-radius: 8px; padding: 2rem; text-align: center; background: #ffffff; margin-bottom: 1rem;">
              <input type="file" id="document-input" accept=".pdf,.docx,.doc" 
                     style="display: none;" onchange="handleFileUpload(event)">
              <div onclick="document.getElementById('document-input').click()" style="cursor: pointer;">
                <p style="color: #374151; font-weight: 500; margin-bottom: 0.25rem; font-size: 0.875rem;">Click to upload document</p>
                <p style="color: #6b7280; font-size: 0.75rem;">PDF, DOCX files up to 10MB</p>
              </div>
              <div id="file-info" style="display: none; margin-top: 1rem; padding: 0.75rem; background: #ecfdf5; border: 1px solid #d1fae5; border-radius: 6px;">
                <p style="color: #065f46; margin: 0; font-size: 0.875rem;">
                  <strong>File uploaded:</strong> <span id="file-name"></span>
                </p>
              </div>
            </div>
            
            <button type="button" id="parse-btn" onclick="parseDocument()" disabled
                    style="width: 100%; padding: 0.75rem; background: #6b7280; border: none; border-radius: 8px; color: white; font-weight: 500; font-size: 0.875rem; cursor: not-allowed; margin-bottom: 0.5rem;">
              Parse Document
            </button>
            
            <p style="color: #6b7280; font-size: 0.75rem; line-height: 1.4;">
              <strong>Expected structure:</strong> "Feature Title:", "Description:", "Requirements:", "Implementation:", etc.
            </p>
          </div>

          <div id="parsed-info" style="display: none; margin-bottom: 1.5rem; padding: 1rem; background: #dbeafe; border: 1px solid #93c5fd; border-radius: 8px;">
            <p style="color: #1e40af; margin: 0; font-size: 0.875rem;">
              <strong>Document parsed successfully!</strong> Review and modify the fields below before submitting.
            </p>
          </div>

          <!-- Manual Entry Form -->
          <form id="upload-form">
            <div style="margin-bottom: 1.5rem;">
              <label style="display: block; color: #374151; margin-bottom: 0.5rem; font-weight: 500;">Feature Title</label>
              <input type="text" id="title-input" name="title" required 
                     style="width: 100%; padding: 0.75rem; background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; color: #1f2937; font-size: 1rem;"
                     placeholder="e.g., Teen Sleep Mode, Location-based Restrictions">
            </div>
            
            <div style="margin-bottom: 1.5rem;">
              <label style="display: block; color: #374151; margin-bottom: 0.5rem; font-weight: 500;">Feature Description</label>
              <textarea id="description-input" name="description" required rows="4"
                        style="width: 100%; padding: 0.75rem; background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; color: #1f2937; font-size: 1rem; resize: vertical;"
                        placeholder="Brief description of the feature..."></textarea>
            </div>
            
            <div style="margin-bottom: 2rem;">
              <label style="display: block; color: #374151; margin-bottom: 0.5rem; font-weight: 500;">PRD/TRD Content</label>
              <textarea id="content-input" name="prd_text" required rows="8"
                        style="width: 100%; padding: 0.75rem; background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; color: #1f2937; font-size: 1rem; resize: vertical;"
                        placeholder="Paste your full PRD/TRD content here..."></textarea>
            </div>
            
            <button type="submit" 
                    style="width: 100%; padding: 1rem; background: #FF3361; border: none; border-radius: 8px; color: white; font-weight: 600; font-size: 1rem; cursor: pointer;"
                    onmouseover="this.style.backgroundColor='#e11d48'"
                    onmouseout="this.style.backgroundColor='#FF3361'">
              Analyze for Compliance
            </button>
          </form>
        </div>
      </div>
    </div>
  `;
}
