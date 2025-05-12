FROM python:3.9

WORKDIR /app

# نصب وابستگی‌های سیستمی برای تبدیل SVG به PNG
RUN apt-get update && apt-get install -y \
    librsvg2-bin \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# نصب کتابخانه‌های پایتون
RUN pip install fastapi uvicorn kerykeion pytz gunicorn wand

# ایجاد پوشه برای ذخیره SVG
RUN mkdir -p /app/svg

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3330"]
