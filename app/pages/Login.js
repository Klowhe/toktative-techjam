export function Login() {
  return `
    <div style="min-height: 100vh; background: #ffffff; color: #1f2937; padding: 20px; display: flex; align-items: center; justify-content: center;">
      <div style="background: #f9fafb; padding: 2rem; border-radius: 12px; text-align: center; max-width: 400px; width: 100%; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <h1 style="color: #FF3361; margin-bottom: 1rem; font-size: 2rem; font-weight: bold;">GeoReg Classifier</h1>
        <p style="color: #6b7280; margin-bottom: 2rem;">Compliance classification for global features</p>
        
        <form id="login-form">
          <div style="margin-bottom: 1rem;">
            <label style="display: block; color: #374151; margin-bottom: 0.5rem; font-weight: 500;">Name</label>
            <input type="text" name="name" required 
                   style="width: 100%; padding: 0.75rem; background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; color: #1f2937; font-size: 1rem;">
          </div>
          
          <div style="margin-bottom: 1.5rem;">
            <label style="display: block; color: #374151; margin-bottom: 0.5rem; font-weight: 500;">Email</label>
            <input type="email" name="email" required 
                   style="width: 100%; padding: 0.75rem; background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; color: #1f2937; font-size: 1rem;">
          </div>
          
          <button type="submit" 
                  style="width: 100%; padding: 0.75rem; background: #FF3361; border: none; border-radius: 8px; color: white; font-weight: 600; font-size: 1rem; cursor: pointer; transition: background-color 0.2s;"
                  onmouseover="this.style.backgroundColor='#e11d48'"
                  onmouseout="this.style.backgroundColor='#FF3361'">
            Sign In
          </button>
        </form>
        
        <p style="color: #9ca3af; font-size: 0.875rem; margin-top: 1rem;">
          Demo account - Enter any name and email
        </p>
      </div>
    </div>
  `;
}
