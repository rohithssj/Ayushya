FROM node:22-slim

# Install Python 3, pip, venv, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create virtual environment at /app/.venv to match API route python resolution logic
RUN python3 -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Install Python dependencies into virtualenv
COPY requirements-rag.txt ./
RUN pip install --no-cache-dir -r requirements-rag.txt

# Pre-download SentenceTransformer model to cache in Docker layer
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Install Node dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy application source code, scripts, and pre-computed vector data
COPY . .

# Build Next.js application
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# Set runtime binding and environment
ENV HOSTNAME="0.0.0.0"
ENV PORT=3000
EXPOSE 3000

CMD ["npm", "run", "start"]
