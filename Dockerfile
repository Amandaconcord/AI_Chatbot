
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc git \
    && rm -rf /var/lib/apt/lists/*


ENV VENV=/opt/venv
RUN python -m venv $VENV
ENV PATH="$VENV/bin:$PATH"


# … same lines as before …

# ─── Copy dependency files first (for cache) ──────────────────
WORKDIR /app
COPY requirements-dev.txt ./

# If you manage prod deps in environment.yml/conda:
# COPY environment.yml ./

RUN pip install --upgrade pip && \
    pip install -r requirements-dev.txt

# ─── Copy package metadata THEN source code ───────────────────
COPY setup.cfg ./   
COPY pyproject.toml ./             
# If you later move to pyproject.toml, copy that too
# COPY pyproject.toml ./

COPY src/ ./src
COPY tests/ ./tests

# Now editable-install will work, because setup.cfg is present
RUN pip install -e .

CMD ["python", "-c", "import AI_Chatbot as m; print(m.hello())"]
