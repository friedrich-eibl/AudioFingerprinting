# Dockerfile

# 1. Use an official Python runtime as a parent image
#    Choose a specific version. 'slim' variants are smaller.
#    Make sure this matches the Python version you developed with.
FROM python:3.10-slim
# Or FROM python:3.11-slim, FROM python:3.9-slim, etc.

# 2. Set environment variables
#    Prevents Python from writing pyc files to disc (optional)
ENV PYTHONDONTWRITEBYTECODE 1
#    Ensures Python output is sent straight to terminal (recommended)
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory in the container
WORKDIR /app

# 4. Install system dependencies (if any)
#    Example: RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*
#    (Uncomment and modify if your app needs system libraries like gcc, postgresql-client, etc.)

# 5. Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# 6. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 7. Copy the rest of your application code into the container
COPY . .

# 8. Create a non-root user to run the application (Security Best Practice)
RUN addgroup --system app && adduser --system --group app
# If using Alpine base image: RUN addgroup -S app && adduser -S -G app app
USER app

# 9. Expose the port the app runs on (informational)
#    This should match the port Uvicorn will run on inside the container
EXPOSE 8000

# 10. Define the command to run your application
#     Replace 'main:app' with your actual filename and FastAPI instance variable
#     Example: if your file is app.py and variable is api (api = FastAPI()), use "app:api"
#     Use 0.0.0.0 to make it accessible from outside the container.
#     Add --proxy-headers if running behind a reverse proxy that handles TLS/SSL.
#     Remove --reload for production builds.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# For Development with auto-reload: CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
