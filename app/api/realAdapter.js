// Real API adapter for backend integration
const API_BASE_URL = 'http://localhost:5001/api';

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
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      let data;
      try {
        data = await response.json();
      } catch (e) {
        throw new Error('Invalid JSON response from server');
      }
      
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
      throw error;
    }
  }
}

// Export singleton instance
export const realApi = new RealApiAdapter();
