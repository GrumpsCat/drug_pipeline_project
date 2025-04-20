FROM python:3.10-slim

# Install RDKit dependencies and RDKit
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

# Install RDKit via conda (much easier and stable than pip)
RUN pip install --upgrade pip && \
    pip install streamlit pandas numpy requests Pillow plotly

RUN pip install rdkit-pypi==2022.9.5

# Set up Streamlit port
EXPOSE 8501

# Copy app files
WORKDIR /app
COPY . /app

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
