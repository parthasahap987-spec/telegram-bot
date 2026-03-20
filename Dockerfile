FROM python:3.10-slim

WORKDIR /app

COPY . .

# Install system dependencies (IMPORTANT 🔥)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libx11-xcb1 \
    libxfixes3 \
    libxext6 \
    libx11-6 \
    libxcb1 \
    libxrender1 \
    libfontconfig1 \
    libfreetype6 \
    ca-certificates \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright browsers
RUN playwright install

CMD ["python", "auto_post.py"]
