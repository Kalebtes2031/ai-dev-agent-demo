FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ssh \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for projects
RUN mkdir -p ai_dev_agent/projects

# Make start script executable
RUN chmod +x start.sh

# Environment variables (to be set in Render)
# TELEGRAM_BOT_TOKEN
# OPENAI_API_KEY
# GITHUB_SSH_PRIVATE_KEY
# GITHUB_USERNAME

CMD ["./start.sh"]
