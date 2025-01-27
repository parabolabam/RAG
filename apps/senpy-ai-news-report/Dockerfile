FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install poetry==1.8.4

# Disable virtual environments in Poetry
RUN poetry config virtualenvs.create false

# Copy just the dependency files first
COPY pyproject.toml poetry.lock /app/

COPY . .

ENV VIRTUAL_ENV=/app/.venv \
  PATH="/app/.venv/bin:$PATH"
# Install dependencies
RUN poetry install --no-dev

# Copy the rest of the code

# Command to run the application
ENTRYPOINT ["uvicorn", "senpy_ai_chatbot.main:app", "--host", "0.0.0.0", "--port", "8000"]

