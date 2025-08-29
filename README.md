# Geo-Reg Compliance Classifier

A TikTok-styled web application for classifying feature compliance with geo-regulatory requirements using AI analysis.

## Features

- **Upload & Classify**: Submit PRD/TRD documents for AI-powered compliance analysis
- **Results Dashboard**: View, filter, and search compliance classifications
- **Feature Detail**: Deep dive into analysis results with citations and audit trail
- **Override System**: Reviewers can override AI decisions with audit tracking
- **Audit Dashboard**: KPIs, charts, and CSV export for compliance reporting
- **Mock Authentication**: Lightweight login system (all users get Reviewer role)

## Tech Stack

- **Frontend**: Lynx JS (React-style components), Vanilla JavaScript ES6+
- **Styling**: Custom CSS with TikTok brand colors (red #FF3361, cyan #25F4EE)
- **Data Layer**: MockAdapter (localStorage) with HttpAdapter interface for future backend
- **Charts**: SVG-based bar charts
- **Router**: Custom SPA router
- **Build**: Vite

## Project Structure

```
/app
  /api
    api.ts              # API interface and types
    mockAdapter.ts      # Mock implementation with localStorage
    httpAdapter.ts      # HTTP adapter for future backend
  /pages
    Login.ts           # Mock authentication page
    Upload.ts          # Feature upload and classification
    Features.ts        # Results dashboard with filters
    FeatureDetail.ts   # Feature detail with override capability
    Audit.ts           # KPIs, charts, and export
  /components
    TopNav.ts          # Navigation component
    FlagBadge.ts       # Compliance flag badges
    RegChip.ts         # Regulation chips
    ConfidenceMeter.ts # Confidence visualization
    AuditTimeline.ts   # Event timeline
    OverrideModal.ts   # Review override modal
    CsvExportButton.ts # CSV export functionality
    Table.ts           # Reusable data table
    Toast.ts           # Toast notifications
  /lib
    router.ts          # SPA routing
    store.ts           # Reactive state management
    csv.ts             # CSV utilities
    validators.ts      # Form validation
    utils.ts           # Common utilities
  /styles
    globals.css        # TikTok-styled global CSS
```

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Open in browser**:
   Visit `http://localhost:3000`

## Usage

### 1. Login
- Enter any name and email
- All users get "Reviewer" role for demo purposes

### 2. Upload Feature
- Fill in feature title and description
- Paste PRD/TRD text or upload .txt/.md file
- Optionally select region hints
- Click "Classify Compliance"

### 3. View Results
- Browse all analyzed features in the dashboard
- Filter by flag (Yes/No/Maybe), regulation, date range
- Search across titles, descriptions, and reasoning
- Export filtered results to CSV

### 4. Feature Detail
- Click any feature title to view detailed analysis
- See AI reasoning, regulations, confidence, and citations
- View audit timeline of all actions
- Override AI decision (requires Reviewer role)

### 5. Audit Dashboard
- View KPIs: total analyzed, compliance percentages, top regulation
- Interactive bar chart showing features by regulation
- Export filtered data to CSV

## AI Classification Logic

The MockAdapter uses simple heuristics to simulate AI analysis:

- **Yes** (compliance required): Text mentions "under 18", "minor", "parental", "age gate", "curfew", "night", "teen", "youth", "child"
  - Regulations: UT Social Media Act, FL Online Protections, CA Protecting Our Kids
  - Confidence: 80-95%

- **No** (no compliance issues): Text mentions "geofence", "market test", "rollout test", "business", "testing", "pilot"
  - Regulations: None
  - Confidence: 85-95%

- **Maybe** (needs review): All other cases
  - Regulations: None
  - Confidence: 50-70%

## Data Types

Key data structures include:

- **Feature**: Basic feature information (title, description, metadata)
- **Analysis**: AI classification results (flag, reason, regulations, confidence)
- **Review**: Human override decisions with audit trail
- **Artifact**: Stored PRD/TRD content with hash

## API Interface

The app uses a consistent API interface that can switch between MockAdapter (current) and HttpAdapter (future backend):

```typescript
interface Api {
  me(): Promise<User>;
  classify(body: ClassifyRequest): Promise<{feature_id: string; analysis: Analysis}>;
  listFeatures(query: ListFeaturesQuery): Promise<{items: FeatureRow[]; total: number}>;
  getFeature(id: string): Promise<{feature: Feature; artifacts: Artifact; analysis: Analysis; reviews: Review[]}>;
  createReview(id: string, body: CreateReviewRequest): Promise<{review_id: string}>;
  exportCsv(query: ListFeaturesQuery): Promise<Blob>;
}
```

## Seed Data

The app comes with 3 pre-loaded examples:

1. **Teen sleep mode (US)** → Yes (youth protection regulations)
2. **Geofence US rollout for market testing** → No (business decision)
3. **Filter available globally except KR** → Maybe (unclear requirements)

## Mobile Support

- Responsive design for mobile devices
- Touch-friendly navigation
- Collapsible filters and sections
- Optimized table layouts

## Future Backend Integration

To connect a real backend:

1. Replace `createApi('mock')` with `createApi('http')` in components
2. Update `HttpAdapter` base URL to point to your API
3. No UI changes required - same interface contracts

## Browser Support

- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge
- Mobile Safari, Chrome Mobile

## License

MIT License