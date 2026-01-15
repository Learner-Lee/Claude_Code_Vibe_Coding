FROM ubuntu:24.04

# Set working directory
WORKDIR /app

# Install system dependencies, Python and ncmdump
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    wget \
    unzip \
    ca-certificates \
    libtag1v5 \
    && rm -rf /var/lib/apt/lists/*

# Download and install ncmdump (v1.5.1)
RUN wget -q https://github.com/taurusxin/ncmdump/releases/download/1.5.1/ncmdump-1.5.1-linux-amd64.zip \
    -O /tmp/ncmdump.zip \
    && unzip /tmp/ncmdump.zip -d /tmp/ \
    && mv /tmp/ncmdump /usr/local/bin/ncmdump \
    && chmod +x /usr/local/bin/ncmdump \
    && rm -rf /tmp/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/

# Create directories for uploads and outputs
RUN mkdir -p uploads outputs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8000/health || exit 1

# Run the application
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
