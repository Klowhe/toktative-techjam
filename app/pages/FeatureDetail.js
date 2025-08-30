export function FeatureDetail({ featureId }) {
  // Use real analyzed feature data from window.analyzedFeature
  const feature = window.analyzedFeature;

  if (!feature) {
    return `
      <div style="min-height: 100vh; background: #ffffff; color: #1f2937; display: flex; align-items: center; justify-content: center;">
        <div style="text-align: center;">
          <h2 style="color: #ef4444; margin-bottom: 1rem;">No Feature Analysis Available</h2>
          <p style="color: #6b7280; margin-bottom: 2rem;">Please analyze a feature first from the Upload page.</p>
          <button onclick="navigateTo('/upload')" style="background: #009995; color: white; border: none; padding: 0.75rem 2rem; border-radius: 8px; cursor: pointer; font-weight: 500;">
            Go to Upload
          </button>
        </div>
      </div>
    `;
  }

  const getFlagColor = (flag) => {
    switch (flag) {
      case 'Yes': return '#ef4444';
      case 'No': return '#22c55e';
      case 'Maybe': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return `
    <div style="min-height: 100vh; background: #ffffff; color: #1f2937;">
      <nav style="background: #121415; padding: 0 2rem; margin: 0; width: 100%; box-sizing: border-box;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 2rem;">
            <h1 style="color: #ffffff; margin: 1rem 0; font-size: 1.5rem; font-weight: 700;">GeoReg Classifier</h1>
            <nav style="display: flex; gap: 1.5rem;">
              <button onclick="navigateTo('/upload')" style="color: #a1a1aa; background: none; border: none; cursor: pointer; padding: 0.5rem 0; font-size: 1rem;">Upload</button>
              <button onclick="navigateTo('/features')" style="color: #009995; background: none; border: none; cursor: pointer; padding: 0.5rem 0; font-size: 1rem; font-weight: 500;">Features</button>
            </nav>
          </div>
        </div>
      </nav>

      <div style="padding: 2rem; max-width: 1200px; margin: 0 auto;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem; font-size: 0.875rem; color: #6b7280;">
          <button onclick="navigateTo('/features')" style="background: none; border: none; color: #6b7280; cursor: pointer; text-decoration: underline;">Features</button>
          <span>&gt;</span>
          <span>${feature.title}</span>
        </div>

        <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 2rem; margin-bottom: 2rem;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;">
            <h2 style="color: #1f2937; margin: 0; font-size: 2rem; font-weight: 700;">${feature.title}</h2>
            <span style="display: inline-block; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.875rem; font-weight: 600; color: white; background: ${getFlagColor(feature.flag)};">
              ${feature.flag} - Regulatory Flag
            </span>
          </div>
          
          <p style="color: #6b7280; margin: 0 0 2rem 0; font-size: 1.125rem; line-height: 1.6;">
            ${feature.description || 'No description provided'}
          </p>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
          <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem;">
              <h3 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.25rem; font-weight: 600;">Classification Details</h3>
              
              <div style="display: grid; gap: 1rem;">
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Regulatory Flag</label>
                  <span style="display: inline-block; padding: 0.375rem 0.875rem; border-radius: 4px; font-size: 0.875rem; font-weight: 500; color: white; background: ${getFlagColor(feature.flag)};">
                    ${feature.flag}
                  </span>
                </div>
                
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Age Group Targeting</label>
                  <p style="color: #1f2937; margin: 0;">${feature.age || 'Not specified'}</p>
                </div>
                
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Identified Regulations</label>
                  <div style="display: flex; flex-wrap: wrap; gap: 0.375rem;">
                    ${(feature.regulations && feature.regulations.length > 0) ? 
                      feature.regulations.map(reg => `
                        <span style="display: inline-block; padding: 0.25rem 0.5rem; background: #f3f4f6; color: #374151; border-radius: 4px; font-size: 0.75rem;">
                          ${reg}
                        </span>
                      `).join('') : 
                      '<span style="color: #6b7280; font-style: italic;">No specific regulations identified</span>'
                    }
                  </div>
                </div>
              </div>
            </div>

            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem;">
              <h3 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.25rem; font-weight: 600;">AI Analysis</h3>
              
              <div>
                <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.5rem;">Reasoning</label>
                <div style="background: #f9fafb; padding: 1rem; border-radius: 6px; border-left: 4px solid #009995;">
                  <p style="color: #374151; margin: 0; line-height: 1.6; font-size: 0.875rem;">
                    ${feature.reasoning || 'No detailed reasoning provided'}
                  </p>
                </div>
              </div>
            </div>

            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem;">
              <h3 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.25rem; font-weight: 600;">Impact Assessment</h3>
              
              <div style="display: grid; gap: 1rem;">
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Regions Affected</label>
                  <p style="color: #1f2937; margin: 0;">${(feature.regions_affected && feature.regions_affected.length > 0) ? feature.regions_affected.join(', ') : 'Global'}</p>
                </div>
                
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">User Impact</label>
                  <p style="color: #1f2937; margin: 0;">${feature.impact_assessment || 'Impact assessment pending'}</p>
                </div>
                
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Business Impact</label>
                  <p style="color: #1f2937; margin: 0;">${feature.business_impact || 'Business impact analysis pending'}</p>
                </div>
              </div>
            </div>
          </div>

          <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem;">
              <h3 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.25rem; font-weight: 600;">Implementation Details</h3>
              
              <div style="display: grid; gap: 1rem;">
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Technical Complexity</label>
                  <p style="color: #1f2937; margin: 0;">${feature.technical_complexity || 'Assessment pending'}</p>
                </div>
                
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Expected Timeline</label>
                  <p style="color: #1f2937; margin: 0;">${feature.rollout_timeline || 'Timeline to be determined'}</p>
                </div>
                
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Stakeholders</label>
                  <div style="display: flex; flex-wrap: wrap; gap: 0.375rem;">
                    ${(feature.stakeholders && feature.stakeholders.length > 0) ? 
                      feature.stakeholders.map(stakeholder => `
                        <span style="display: inline-block; padding: 0.25rem 0.5rem; background: #f3f4f6; color: #374151; border-radius: 4px; font-size: 0.75rem;">
                          ${stakeholder}
                        </span>
                      `).join('') : 
                      '<span style="color: #6b7280; font-style: italic;">Stakeholders to be identified</span>'
                    }
                  </div>
                </div>
              </div>
            </div>

            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem;">
              <h3 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.25rem; font-weight: 600;">Activity Log</h3>
              
              <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                <div style="display: flex; gap: 0.75rem;">
                  <div style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%; margin-top: 0.375rem; flex-shrink: 0;"></div>
                  <div style="flex: 1;">
                    <p style="color: #1f2937; margin: 0; font-size: 0.875rem;">Feature classified as <strong>${feature.flag}</strong></p>
                    <p style="color: #6b7280; margin: 0; font-size: 0.75rem;">${formatDate(feature.created_at)}</p>
                  </div>
                </div>
                
                <div style="display: flex; gap: 0.75rem;">
                  <div style="width: 8px; height: 8px; background: #6b7280; border-radius: 50%; margin-top: 0.375rem; flex-shrink: 0;"></div>
                  <div style="flex: 1;">
                    <p style="color: #1f2937; margin: 0; font-size: 0.875rem;">Feature analysis initiated</p>
                    <p style="color: #6b7280; margin: 0; font-size: 0.75rem;">${formatDate(feature.created_at)}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div style="margin-top: 2rem; padding: 1.5rem; background: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb;">
          <h4 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.125rem; font-weight: 600;">Available Actions</h4>
          <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
            <button onclick="exportToCsv(window.analyzedFeature)" style="padding: 0.75rem 1.5rem; background: #009995; color: white; border: none; border-radius: 6px; cursor: pointer;">
              Export Details
            </button>
            <button onclick="sendToEmail()" style="padding: 0.75rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer;">
              Send to Email
            </button>
            <button onclick="navigateTo('/upload')" style="padding: 0.75rem 1.5rem; background: #f3f4f6; color: #374151; border: none; border-radius: 6px; cursor: pointer;">
              Analyze New Feature
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}
