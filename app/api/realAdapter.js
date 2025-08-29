// Real API adapter for backend integration
const API_BASE_URL = 'http://localhost:5000/api';

export class RealApiAdapter {
  async analyzeFeature(featureData) {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: featureData.title,
          description: featureData.description,
          prd_text: featureData.prd_text || featureData.requirements,
          source_file: 'eu_dsa.pdf' // Default to EU DSA for now
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Analysis failed');
      }

      return {
        success: true,
        feature: data.feature,
        metadata: {
          raw_analysis: data.raw_analysis,
          retrieved_documents: data.retrieved_documents,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('Real API Error:', error);
      
      // Fallback to mock data if backend is unavailable
      if (error.message.includes('fetch')) {
        console.warn('Backend unavailable, using mock data');
        return this.generateMockResponse(featureData);
      }
      
      throw error;
    }
  }

  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
      const data = await response.json();
      return { healthy: response.ok, data };
    } catch (error) {
      return { healthy: false, error: error.message };
    }
  }

  async getAvailableSources() {
    try {
      const response = await fetch(`${API_BASE_URL}/sources`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching sources:', error);
      return {
        sources: ['eu_dsa.pdf'],
        collections: { 'eu_dsa.pdf': 'eu_dsa_collection' }
      };
    }
  }

  // Fallback mock response when backend is unavailable
  generateMockResponse(featureData) {
    const mockClassifications = [
      {
        flag: 'Yes',
        confidence: 0.87,
        regulations: ['EU Digital Services Act', 'GDPR Article 8'],
        reasoning: 'Feature involves user data collection and content moderation that may conflict with EU regulations.',
        age: 'Under 18',
        risk_level: 'High'
      },
      {
        flag: 'No',
        confidence: 0.92,
        regulations: [],
        reasoning: 'Feature appears compliant with current EU regulatory framework.',
        age: 'All Ages',
        risk_level: 'Low'
      },
      {
        flag: 'Maybe',
        confidence: 0.65,
        regulations: ['EU Digital Services Act'],
        reasoning: 'Feature requires further legal review to determine compliance status.',
        age: 'All Ages',
        risk_level: 'Medium'
      }
    ];

    const randomClassification = mockClassifications[Math.floor(Math.random() * mockClassifications.length)];

    return {
      success: true,
      feature: {
        id: 'mock_' + Date.now(),
        title: featureData.title,
        description: featureData.description,
        flag: randomClassification.flag,
        confidence: randomClassification.confidence,
        regulations: randomClassification.regulations,
        reasoning: randomClassification.reasoning,
        age: randomClassification.age,
        regions_affected: ['European Union'],
        created_at: new Date().toISOString(),
        review_status: 'none',
        impact_assessment: `Mock analysis suggests ${randomClassification.flag.toLowerCase()} regulatory risk`,
        business_impact: 'Simulated analysis - backend unavailable',
        technical_complexity: 'Medium - Mock assessment',
        rollout_timeline: '4-6 weeks (estimated)',
        stakeholders: ['Legal Team', 'Compliance', 'Product Team'],
        risk_level: randomClassification.risk_level
      },
      metadata: {
        raw_analysis: 'Mock analysis generated - backend server not available',
        retrieved_documents: 0,
        timestamp: new Date().toISOString(),
        mock: true
      }
    };
  }
}

// Export singleton instance
export const realApi = new RealApiAdapter();
