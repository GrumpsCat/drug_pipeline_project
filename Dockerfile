FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    wget \
    curl \
    git \
    ca-certificates \
    libboost-all-dev \
    cmake \
    libeigen3-dev \
    libpng-dev \
    libfreetype6-dev \
    libx11-dev \
    libtiff-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip
RUN pip install streamlit pandas numpy requests Pillow plotly rdkit-pypi==2022.9.5

# Copy app code
WORKDIR /app
COPY . /app

# Expose the Streamlit port
EXPOSE 7860

# Start the app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
