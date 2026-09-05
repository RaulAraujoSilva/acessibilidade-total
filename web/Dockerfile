FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends libreoffice-writer libreoffice-impress ffmpeg xvfb xauth fonts-liberation fonts-dejavu && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY web/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY web/ /app/
COPY scripts/ /skill/scripts/
COPY references/ /skill/references/
RUN useradd --create-home app && mkdir -p /data && chown -R app:app /app /data
USER app
ENV PRIVATE_MEDIA_ROOT=/data
EXPOSE 8000
ENV SKILL_AUDITOR=/skill/scripts/audit_pptx.py
CMD ["python","start.py"]
