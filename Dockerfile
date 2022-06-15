FROM python:3.9-slim AS build

COPY ./requirements.txt .
RUN set -x \
    && pip install --user -r requirements.txt


FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1 \
    PATH=/app/.local/bin:$PATH

EXPOSE 8000

WORKDIR /app

RUN set -x && \
    addgroup --gid 1000 app && \
    adduser --uid 1000 --gid 1000 --system --home /app app

COPY --from=build --chown=1000 /root/.local .local
COPY . .

USER app

CMD ["python", "run.py"]