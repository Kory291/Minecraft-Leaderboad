FROM python:latest
WORKDIR /app

RUN adduser --quiet --disabled-password dockeruser

COPY --chown=dockeruser . .
RUN --mount=from=ghcr.io/astral-sh/uv:latest,source=/uv,target=/bin/uv \
  uv sync

USER dockeruser

CMD [ "/app/.venv/bin/flask","--app","/app/main", "run", "--host", "0.0.0.0" ]
