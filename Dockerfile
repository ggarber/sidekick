# Use Python 3.8 or later as specified in pyproject.toml
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install pip and build dependencies
RUN pip install --no-cache-dir pip setuptools wheel

# Install the project and its dependencies
RUN pip install --no-cache-dir .

# Set the default command
ENTRYPOINT ["python", "main.py"] 