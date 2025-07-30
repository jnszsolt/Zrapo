FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg2 chromium-driver chromium \
    && apt-get clean
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
WORKDIR /app
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH=$PATH:/usr/bin/chromium
EXPOSE 3000
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "main:app"]
