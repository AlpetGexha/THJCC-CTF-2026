FROM ghcr.io/astral-sh/uv:debian

WORKDIR /python-docker

COPY pyproject.toml uv.lock .python-version ./

ARG UPLOAD_FOLDER

ENV TZ=Asia/Taipei
ENV PYTHONUNBUFFERED=1

RUN useradd -m appuser

RUN chown -R appuser:appuser /python-docker

RUN mkdir -p ${UPLOAD_FOLDER}

RUN chown -R appuser:appuser ${UPLOAD_FOLDER}

USER appuser
RUN uv run python3 -c "print('Download Environment earlier for caching')"

USER root
COPY . .

RUN chown -R appuser:appuser .venv .

RUN chown -R root:root templates && \
    chmod -R 755 templates

RUN chown -R root:root app.py && \
    chmod -R 755 app.py

USER appuser

# Run the application
CMD [ "uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
