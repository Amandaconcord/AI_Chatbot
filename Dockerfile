# ──────────────────────────────────────────────────────────────
# Loan-Bot CI Image
# ──────────────────────────────────────────────────────────────
# Start from an official slim Python matching your AML env
FROM python:3.11-slim AS base

# Install system deps you need; keep this lean
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc git \
    && rm -rf /var/lib/apt/lists/*

# ─── Create a virtual-env inside the container (optional) ─────
ENV VENV=/opt/venv
RUN python -m venv $VENV
ENV PATH="$VENV/bin:$PATH"

# ─── Copy only the dependency files first for caching ─────────
WORKDIR /app
COPY requirements-dev.txt ./     # dev deps (pytest, ruff, etc.)
# If you manage prod deps in environment.yml/conda: COPY that too

RUN pip install --upgrade pip && \
    pip install -r requirements-dev.txt

# ─── Copy the actual source code last ─────────────────────────
COPY src/ ./src
COPY tests/ ./tests

# Install your package in editable mode inside the image
RUN pip install -e .

CMD ["python", "-c", "import AI_Chatbot as m; print(m.hello())"]
