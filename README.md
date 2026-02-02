# Downstream Slow Service

A mock external API service that responds slowly, designed for testing backend system resilience, timeout handling, and cascade failure scenarios.

## 🎯 Purpose

This service is part of a load testing demonstration project. It simulates:
- Slow external API responses
- Unpredictable latency
- Random failures
- Service degradation
- Timeout scenarios

**Related Repository**: [backend-load-testing](https://github.com/yourusername/backend-load-testing)

## 🚀 Quick Start

### Local Development
```bash
# Clone repository
git clone https://github.com/yourusername/downstream-slow-service.git
cd downstream-slow-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn app.main:app --reload --port 8001

# Access API docs
open http://localhost:8001/docs
```

### Docker
```bash
# Build image
docker build -t downstream-service:latest -f docker/Dockerfile .

# Run container
docker run -p 8001:8001 \
  -e DEFAULT_DELAY=5 \
  -e FAILURE_RATE=0.2 \
  downstream-service:latest

# Test
curl http://localhost:8001/health
```

### Kubernetes (Minikube)
```bash
# Build image in Minikube
eval $(minikube docker-env)
docker build -t downstream-service:latest -f docker/Dockerfile .

# Create namespace (if not exists)
kubectl create namespace load-testing

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify
kubectl get pods -n load-testing
kubectl get svc -n load-testing

# Test from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n load-testing -- \
  curl http://downstream-service:8001/health
```

## 📚 API Endpoints

### Health & Info
- `GET /` - Service information
- `GET /health` - Health check
- `GET /stats` - Request statistics

### Testing Endpoints
- `GET /slow?delay=5` - Configurable delay (1-30 seconds)
- `GET /random?min_delay=1&max_delay=10` - Random delay
- `GET /sometimes-fail?failure_rate=0.3` - Random failures
- `GET /timeout-trap` - 60 second response (timeout testing)
- `GET /cascade?levels=3` - Cascading delays

## 🧪 Usage Examples

### Test Timeout Handling
```bash
# Your main service should timeout before 60 seconds
curl "http://localhost:8001/timeout-trap"
```

### Test Retry Logic
```bash
# 50% of requests will fail
for i in {1..10}; do
  curl "http://localhost:8001/sometimes-fail?failure_rate=0.5"
done
```

### Test Latency Impact
```bash
# Slow responses affect upstream services
curl "http://localhost:8001/slow?delay=10"
```

## ⚙️ Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_DELAY` | 3 | Default delay for /slow endpoint |
| `MAX_DELAY` | 30 | Maximum allowed delay |
| `FAILURE_RATE` | 0.0 | Default failure rate (0.0-1.0) |
| `PORT` | 8001 | Server port |

## 🧪 Testing
```bash
# Install test dependencies
pip install pytest pytest-cov httpx

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## 📊 Integration with Main Service

This service is called by the [backend-load-testing](https://github.com/yourusername/backend-load-testing) service to demonstrate:

1. **Cascade Failures**: When this service is slow, main service degrades
2. **Timeout Handling**: Proper timeout configuration in main service
3. **Circuit Breaker**: Main service should fail-fast when this fails
4. **Retry Logic**: How main service handles transient failures

## 🎓 Learning Scenarios

### Scenario 1: Downstream Latency Impact
```bash
# Set this service to be slow
export DEFAULT_DELAY=10

# Main service calls will be slow too
# Demonstrates: Backpressure, timeout importance
```

### Scenario 2: Cascade Failure
```bash
# Stop this service
kubectl scale deployment downstream-service -n load-testing --replicas=0

# Main service /cascade-failure endpoint will fail
# Demonstrates: Error propagation, circuit breaker need
```

### Scenario 3: Intermittent Failures
```bash
# Set random failures
export FAILURE_RATE=0.3

# 30% of requests fail randomly
# Demonstrates: Retry logic, exponential backoff
```

## 📖 Architecture