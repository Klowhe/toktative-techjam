# AWS Deployment Configuration

This document outlines the configuration needed to deploy the frontend with AWS Lambda + SageMaker architecture.

## Environment Variables

When deploying to AWS, set the following environment variables:

### Production Environment
```bash
NODE_ENV=production
AWS_REGION=us-east-1
API_GATEWAY_URL=https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/prod
LAMBDA_FUNCTION_NAME=rag_query_function
```

## Build Process

1. **Build Frontend for Production:**
   ```bash
   NODE_ENV=production npm run build
   ```

2. **Deploy to S3 + CloudFront (Recommended):**
   ```bash
   aws s3 sync dist/ s3://your-frontend-bucket/
   aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
   ```

## AWS Architecture Integration

### API Gateway Endpoints Expected:
- `POST /api/analyze` - Feature analysis
- `POST /api/parse` - Document parsing  
- `POST /api/send-email` - Email sending
- `GET /health` - Health check

### Lambda Function Structure:
```python
def lambda_handler(event, context):
    # Route based on HTTP method and path
    if event['httpMethod'] == 'POST' and event['path'] == '/api/analyze':
        return handle_analyze(event, context)
    elif event['httpMethod'] == 'POST' and event['path'] == '/api/parse':
        return handle_parse(event, context)
    # ... other routes
```

### CORS Configuration:
Ensure your API Gateway has CORS enabled for your frontend domain.

## Frontend Changes Summary:
- ✅ Dynamic API URL configuration
- ✅ Environment-based config loading
- ✅ AWS-compatible headers
- ✅ Error handling for Lambda cold starts
- ✅ Flexible endpoint configuration
