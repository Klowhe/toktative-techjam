export function FeatureDetail({ featureId }) {
  // Hardcoded test data
  const features = {
    'feat_001': {
      id: 'feat_001',
      title: 'Teen Sleep Mode (US)',
      description: 'Feature that restricts app usage for users under 18 during night hours (10 PM - 6 AM), requiring parental consent to override. This includes push notification restrictions, content feed limitations, and direct messaging controls during these hours.',
      flag: 'Yes',
      regulations: ['UT Social Media Act', 'FL Online Protections', 'CA Protecting Our Kids'],
      created_at: '2025-08-26T10:30:00Z',
      review_status: 'none',
      regions_affected: ['United States'],
      impact_assessment: 'High - Affects all US users under 18',
      business_impact: 'Medium - May reduce engagement but improves compliance',
      technical_complexity: 'Medium - Requires age verification integration',
      rollout_timeline: '3-4 weeks',
      stakeholders: ['Legal Team', 'Product Safety', 'Engineering']
    },
    'feat_002': {
      id: 'feat_002', 
      title: 'Geofence US Rollout for Market Testing',
      description: 'Limit feature availability to US users only for initial market testing and performance evaluation. This allows controlled rollout and data collection before global expansion.',
      flag: 'No',
      regulations: [],
      created_at: '2025-08-27T14:15:00Z',
      review_status: 'none',
      regions_affected: ['United States'],
      impact_assessment: 'Low - Limited to beta testing group',
      business_impact: 'Low - Testing phase only',
      technical_complexity: 'Low - Simple geolocation check',
      rollout_timeline: '1-2 weeks',
      stakeholders: ['Product Team', 'Engineering', 'Analytics']
    },
    'feat_003': {
      id: 'feat_003',
      title: 'Filter Available Globally Except KR',
      description: 'New content filter available worldwide except in South Korea due to unclear regulatory requirements. Filter includes AI-powered content moderation and user reporting enhancements.',
      flag: 'Maybe',
      regulations: [],
      created_at: '2025-08-28T09:45:00Z',
      review_status: 'overridden',
      regions_affected: ['Global except South Korea'],
      impact_assessment: 'Medium - Affects content moderation globally',
      business_impact: 'Medium - Improves safety but excludes KR market',
      technical_complexity: 'High - Complex AI integration',
      rollout_timeline: '6-8 weeks',
      stakeholders: ['Legal Team', 'Safety Team', 'AI/ML Team']
    },
    'feat_004': {
      id: 'feat_004',
      title: 'Age Verification for EU Users',
      description: 'Implement mandatory age verification for users in European Union countries to comply with GDPR requirements. Uses third-party verification service with privacy-preserving technology.',
      flag: 'Yes',
      regulations: ['GDPR Article 8', 'EU Digital Services Act'],
      created_at: '2025-08-25T16:20:00Z',
      review_status: 'approved',
      regions_affected: ['European Union'],
      impact_assessment: 'High - Affects all EU users',
      business_impact: 'High - Required for EU compliance',
      technical_complexity: 'High - Third-party integration required',
      rollout_timeline: '8-10 weeks',
      stakeholders: ['Legal Team', 'Privacy Team', 'Engineering', 'Compliance']
    }
  };

  const feature = features[featureId];

  if (!feature) {
    return `
      <div style="min-height: 100vh; background: #ffffff; color: #1f2937; display: flex; align-items: center; justify-content: center;">
        <div style="text-align: center;">
          <h2 style="color: #ef4444; margin-bottom: 1rem;">Feature Not Found</h2>
          <p style="color: #6b7280; margin-bottom: 2rem;">The requested feature could not be found.</p>
          <button onclick="navigateTo('/features')" style="padding: 0.75rem 1.5rem; background: #009995; color: white; border: none; border-radius: 6px; cursor: pointer;">
            Back to Features
          </button>
        </div>
      </div>
    `;
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
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
        <!-- Breadcrumb -->
        <div style="margin-bottom: 2rem;">
          <nav style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.875rem;">
            <button onclick="navigateTo('/features')" style="background: none; border: none; color: #009995; cursor: pointer; text-decoration: underline;">Features</button>
            <span>/</span>
            <span>${feature.title}</span>
          </nav>
        </div>

        <!-- Header -->
        <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 2rem; gap: 2rem;">
          <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
              <h1 style="color: #1f2937; margin: 0; font-size: 2rem; font-weight: bold;">${feature.title}</h1>
              <span style="display: inline-block; padding: 0.375rem 0.875rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; color: white; background: ${getFlagColor(feature.flag)};">
                ${feature.flag}
              </span>
            </div>
            <p style="color: #6b7280; font-size: 1.125rem; line-height: 1.6; margin: 0;">${feature.description}</p>
          </div>
          <div style="display: flex; gap: 0.75rem;">
            <button style="padding: 0.75rem 1.5rem; background: #f3f4f6; color: #374151; border: none; border-radius: 6px; cursor: pointer;">
              Export Report
            </button>
            <button style="padding: 0.75rem 1.5rem; background: #009995; color: white; border: none; border-radius: 6px; cursor: pointer;">
              Override Classification
            </button>
          </div>
        </div>

        <!-- Main Grid -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
          <!-- Left Column -->
          <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <!-- Classification Details -->
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem;">
              <h3 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.25rem; font-weight: 600;">Classification Details</h3>
              
              <div style="display: grid; grid-template-columns: 1fr; gap: 1rem;">
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Review Status</label>
                  <span style="display: inline-block; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.875rem; font-weight: 500; color: ${feature.review_status === 'approved' ? '#22c55e' : feature.review_status === 'overridden' ? '#f59e0b' : '#6b7280'}; background: ${feature.review_status === 'approved' ? '#22c55e' : feature.review_status === 'overridden' ? '#f59e0b' : '#6b7280'}15;">
                    ${feature.review_status === 'none' ? 'No Review' : feature.review_status.charAt(0).toUpperCase() + feature.review_status.slice(1)}
                  </span>
                </div>
              </div>

              <div style="margin-top: 1rem;">
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

            <!-- Impact Assessment -->
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem;">
              <h3 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.25rem; font-weight: 600;">Impact Assessment</h3>
              
              <div style="display: grid; gap: 1rem;">
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Regions Affected</label>
                  <p style="color: #1f2937; margin: 0;">${feature.regions_affected.join(', ')}</p>
                </div>
                
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">User Impact</label>
                  <p style="color: #1f2937; margin: 0;">${feature.impact_assessment}</p>
                </div>
                
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Business Impact</label>
                  <p style="color: #1f2937; margin: 0;">${feature.business_impact}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column -->
          <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            <!-- Implementation Details -->
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem;">
              <h3 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.25rem; font-weight: 600;">Implementation Details</h3>
              
              <div style="display: grid; gap: 1rem;">
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Technical Complexity</label>
                  <p style="color: #1f2937; margin: 0;">${feature.technical_complexity}</p>
                </div>
                
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Expected Timeline</label>
                  <p style="color: #1f2937; margin: 0;">${feature.rollout_timeline}</p>
                </div>
                
                <div>
                  <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #6b7280; margin-bottom: 0.25rem;">Stakeholders</label>
                  <div style="display: flex; flex-wrap: wrap; gap: 0.375rem;">
                    ${feature.stakeholders.map(stakeholder => `
                      <span style="display: inline-block; padding: 0.25rem 0.5rem; background: #f3f4f6; color: #374151; border-radius: 4px; font-size: 0.75rem;">
                        ${stakeholder}
                      </span>
                    `).join('')}
                  </div>
                </div>
              </div>
            </div>

            <!-- Activity Log -->
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
                
                ${feature.review_status !== 'none' ? `
                  <div style="display: flex; gap: 0.75rem;">
                    <div style="width: 8px; height: 8px; background: #f59e0b; border-radius: 50%; margin-top: 0.375rem; flex-shrink: 0;"></div>
                    <div style="flex: 1;">
                      <p style="color: #1f2937; margin: 0; font-size: 0.875rem;">Classification ${feature.review_status}</p>
                      <p style="color: #6b7280; margin: 0; font-size: 0.75rem;">2 hours ago by Legal Team</p>
                    </div>
                  </div>
                ` : ''}
                
                <div style="display: flex; gap: 0.75rem;">
                  <div style="width: 8px; height: 8px; background: #6b7280; border-radius: 50%; margin-top: 0.375rem; flex-shrink: 0;"></div>
                  <div style="flex: 1;">
                    <p style="color: #1f2937; margin: 0; font-size: 0.875rem;">Feature documentation uploaded</p>
                    <p style="color: #6b7280; margin: 0; font-size: 0.75rem;">${formatDate(feature.created_at)}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div style="margin-top: 2rem; padding: 1.5rem; background: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb;">
          <h4 style="color: #1f2937; margin: 0 0 1rem 0; font-size: 1.125rem; font-weight: 600;">Available Actions</h4>
          <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
            <button style="padding: 0.75rem 1.5rem; background: #009995; color: white; border: none; border-radius: 6px; cursor: pointer;">
              Override Classification
            </button>
            <button style="padding: 0.75rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer;">
              Request Legal Review
            </button>
            <button style="padding: 0.75rem 1.5rem; background: #f3f4f6; color: #374151; border: none; border-radius: 6px; cursor: pointer;">
              Add Comments
            </button>
            <button style="padding: 0.75rem 1.5rem; background: #f3f4f6; color: #374151; border: none; border-radius: 6px; cursor: pointer;">
              Export Details
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}
