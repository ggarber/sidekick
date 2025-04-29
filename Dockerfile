# Update base image to Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only the necessary files
COPY pyproject.toml ./
COPY actions/ ./actions/
COPY providers/ ./providers/
COPY repository/ ./repository/
COPY *.py ./

# Install pip and build dependencies
RUN pip install --no-cache-dir pip setuptools wheel

# Install the project and its dependencies
RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app

ENTRYPOINT ["python" "main.py"]
