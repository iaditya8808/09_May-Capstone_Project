FROM python:3.11-slim

WORKDIR /code

# Copy requirements first to leverage Docker cache
COPY app/requirements.txt ./app/

# Install dependencies
RUN pip install --no-cache-dir -r app/requirements.txt

# Copy the rest of the application and tests
COPY app/ ./app/
COPY tests/ ./tests/

# Set working directory to the app folder where main.py is located
WORKDIR /code/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
