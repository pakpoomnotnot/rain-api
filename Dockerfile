# ใช้ Python slim image
FROM python:3.11-slim

# ตั้ง working directory
WORKDIR /app

# ติดตั้ง dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอก source code
COPY ./app ./app

# ประกาศ port ที่ container จะ expose
EXPOSE 9000

# รัน FastAPI ด้วย uvicorn บน port 9000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
