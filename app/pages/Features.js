export function Features(analyzedFeature = null) {
  // Only show real analyzed features - no hardcoded data
  const features = analyzedFeature ? [analyzedFeature] : [];

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short', 
      day: 'numeric'
    });
  };

  const getFlagColor = (flag) => {
    switch(flag) {
      case 'Yes': return '#ef4444';
      case 'No': return '#22c55e';
      case 'Maybe': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'approved': return '#22c55e';
      case 'overridden': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  return `
    <div style="min-height: 100vh; background: #ffffff; color: #1f2937;">
      <!-- Navigation -->
      <nav style="background: #121415; padding: 0 2rem; margin: 0; width: 100%; box-sizing: border-box;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h1 style="color: #FF3361; font-size: 1.5rem; font-weight: bold; margin: 0;">GeoReg Classifier</h1>
          <div style="display: flex; gap: 0; align-items: center; position: relative;">
            <div style="display: flex; flex-direction: column; align-items: center; position: relative; height: 60px; justify-content: center;">
              <button onclick="navigateTo('/upload')" style="padding: 0.75rem 1.5rem; background: transparent; color: #88898a; border: none; cursor: pointer; font-size: 0.875rem;">Upload</button>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center; position: relative; height: 60px; justify-content: center;">
              <button onclick="navigateTo('/features')" style="padding: 0.75rem 1.5rem; background: transparent; color: white; border: none; cursor: pointer; font-size: 0.875rem;">Features</button>
              <div style="width: 25%; height: 4px; background: #009995; border-radius: 2px; position: absolute; bottom: 8px;"></div>
            </div>
            <button onclick="logout()" style="padding: 0.5rem 1rem; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; margin-left: 2rem;">Logout</button>
          </div>
        </div>
      </nav>

      <!-- Main Content -->
      <div style="padding: 20px; max-width: 1200px; margin: 0 auto;">
        <div style="margin-bottom: 2rem;">
          <h2 style="color: #1f2937; margin-bottom: 0.5rem; font-size: 1.75rem;">Classified Features</h2>
          <p style="color: #6b7280;">Review and manage geo-regulatory compliance classifications</p>
        </div>

        <!-- Features Table -->
        <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
          <table style="width: 100%; border-collapse: collapse;">
            <thead style="background: #f9fafb;">
              <tr>
                <th style="padding: 0.75rem; text-align: left; font-weight: 600; color: #374151; border-bottom: 1px solid #e5e7eb;">Feature</th>
                <th style="padding: 0.75rem; text-align: left; font-weight: 600; color: #374151; border-bottom: 1px solid #e5e7eb;">Flag</th>
                <th style="padding: 0.75rem; text-align: left; font-weight: 600; color: #374151; border-bottom: 1px solid #e5e7eb;">Reasoning</th>
                <th style="padding: 0.75rem; text-align: left; font-weight: 600; color: #374151; border-bottom: 1px solid #e5e7eb;">Age</th>
                <th style="padding: 0.75rem; text-align: left; font-weight: 600; color: #374151; border-bottom: 1px solid #e5e7eb;">Regulations</th>
                <th style="padding: 0.75rem; text-align: left; font-weight: 600; color: #374151; border-bottom: 1px solid #e5e7eb;">Regions Affected</th>
              </tr>
            </thead>
            <tbody>
              ${features.length > 0 ? features.map((feature, index) => `
                <tr style="border-bottom: 1px solid #f3f4f6;">
                  <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6; cursor: pointer;" onclick="toggleFeatureDetails('feature-${index}')">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                      <span id="arrow-feature-${index}" style="transition: transform 0.2s; font-size: 0.75rem; color: #6b7280;">▶</span>
                      <div>
                        <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.25rem;">${feature.title}</div>
                        <div style="color: #6b7280; font-size: 0.875rem; line-height: 1.4;">${feature.description.substring(0, 80)}...</div>
                      </div>
                    </div>
                  </td>
                  <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">
                    <span style="display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; color: white; background: ${getFlagColor(feature.flag)};">
                      ${feature.flag}
                    </span>
                  </td>
                  <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">
                    <div style="color: #374151; font-size: 0.875rem; line-height: 1.4;">
                      ${feature.reasoning ? feature.reasoning.substring(0, 120) + '...' : 'No reasoning provided'}
                    </div>
                  </td>
                  <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">
                    <span style="display: inline-block; padding: 0.25rem 0.75rem; background: #f3f4f6; color: #374151; border-radius: 4px; font-size: 0.75rem; font-weight: 500;">
                      ${feature.age || 'All Ages'}
                    </span>
                  </td>
                  <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">
                    <div style="display: flex; flex-wrap: wrap; gap: 0.25rem;">
                      ${feature.regulations.length > 0 
                        ? feature.regulations.slice(0, 2).map(reg => `
                            <span style="display: inline-block; padding: 0.125rem 0.5rem; background: #e0f2fe; color: #0369a1; border-radius: 4px; font-size: 0.75rem;">
                              ${reg}
                            </span>
                          `).join('')
                        : '<span style="color: #9ca3af; font-size: 0.875rem;">None</span>'
                      }
                      ${feature.regulations.length > 2 ? `<span style="color: #6b7280; font-size: 0.75rem;">+${feature.regulations.length - 2} more</span>` : ''}
                    </div>
                  </td>
                  <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">
                    <span style="color: #374151; font-size: 0.875rem;">${feature.regions_affected ? feature.regions_affected.join(', ') : 'Not specified'}</span>
                  </td>
                </tr>
                <tr id="feature-${index}-details" style="display: none;">
                  <td colspan="6" style="padding: 0; border: none;">
                    <div style="background: #f9fafb; padding: 2rem; border-top: 1px solid #e5e7eb;">
                      <!-- Feature Details -->
                      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                        <!-- Left Column - Basic Info -->
                        <div>
                          <h4 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.125rem; font-weight: 600;">Description</h4>
                          <p style="color: #6b7280; margin: 0 0 1.5rem 0; line-height: 1.6;">${feature.description}</p>
                          
                          <h4 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.125rem; font-weight: 600;">Classification Details</h4>
                          <div style="display: grid; gap: 0.75rem;">
                            <div>
                              <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Reasoning</label>
                              <p style="color: #1f2937; margin: 0; font-size: 0.875rem; line-height: 1.5;">${feature.reasoning || 'No reasoning provided'}</p>
                            </div>
                            
                            <div>
                              <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Target Age Group</label>
                              <span style="display: inline-block; padding: 0.375rem 0.875rem; border-radius: 4px; font-size: 0.875rem; font-weight: 500; color: #374151; background: #f3f4f6;">
                                ${feature.age || 'All Ages'}
                              </span>
                            </div>

                            <div>
                              <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.5rem;">Affected Regulations</label>
                              <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                                ${feature.regulations.length > 0 
                                  ? feature.regulations.map(reg => `
                                      <span style="display: inline-block; padding: 0.375rem 0.75rem; background: #e0f2fe; color: #0369a1; border-radius: 6px; font-size: 0.875rem;">
                                        ${reg}
                                      </span>
                                    `).join('')
                                  : '<span style="color: #9ca3af; font-style: italic;">No regulations identified</span>'
                                }
                              </div>
                            </div>
                          </div>
                        </div>

                        <!-- Right Column - AI Analysis -->
                        <div>
                          <h4 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.125rem; font-weight: 600;">AI Analysis Results</h4>
                          <div style="display: grid; gap: 1rem; margin-bottom: 1.5rem;">
                            <div>
                              <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.5rem;">Analysis Confidence</label>
                              <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <div style="flex: 1; height: 8px; background: #f3f4f6; border-radius: 4px; overflow: hidden;">
                                  <div style="height: 100%; background: ${feature.confidence > 0.8 ? '#22c55e' : feature.confidence > 0.6 ? '#f59e0b' : '#ef4444'}; width: ${(feature.confidence * 100)}%; border-radius: 4px;"></div>
                                </div>
                                <span style="font-size: 0.875rem; font-weight: 600; color: #374151;">${Math.round(feature.confidence * 100)}%</span>
                              </div>
                            </div>
                            
                            <div>
                              <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.5rem;">Risk Level</label>
                              <span style="display: inline-block; padding: 0.375rem 0.875rem; border-radius: 4px; font-size: 0.875rem; font-weight: 500; color: white; background: ${feature.risk_level === 'High' ? '#ef4444' : feature.risk_level === 'Medium' ? '#f59e0b' : '#22c55e'};">
                                ${feature.risk_level || 'Not assessed'}
                              </span>
                            </div>

                            <div>
                              <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.5rem;">Retrieved Documents</label>
                              <p style="color: #1f2937; margin: 0; font-size: 0.875rem;">Analysis based on ${window.lastAnalysisMetadata?.retrieved_documents || 'N/A'} relevant regulatory documents</p>
                            </div>

                            <div>
                              <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.5rem;">Analysis Date</label>
                              <p style="color: #1f2937; margin: 0; font-size: 0.875rem;">${formatDate(feature.created_at)}</p>
                            </div>
                          </div>

                          <h4 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.125rem; font-weight: 600;">Available Actions</h4>
                          <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
                            <button onclick="sendToEmail('${feature.id}')" style="padding: 0.75rem 1.25rem; background: #009995; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.875rem;">
                              Send to Email
                            </button>
                            <button onclick="exportDetails('${feature.id}')" style="padding: 0.75rem 1.25rem; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.875rem;">
                              Export Details
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              `).join('') : `
                <tr>
                  <td colspan="6" style="padding: 3rem; text-align: center; color: #6b7280;">
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 1rem;">
                      <div style="font-size: 3rem;">�</div>
                      <div>
                        <h3 style="color: #374151; margin: 0 0 0.5rem 0; font-size: 1.125rem;">No Features Analyzed Yet</h3>
                        <p style="margin: 0; font-size: 0.875rem;">Upload and analyze a PRD/TRD to see classification results here.</p>
                      </div>
                      <button onclick="navigateTo('/upload')" style="padding: 0.75rem 1.5rem; background: #009995; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.875rem; margin-top: 0.5rem;">
                        Upload Document
                      </button>
                    </div>
                  </td>
                </tr>
              `}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}
