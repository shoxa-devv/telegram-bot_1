# Python ning rasmiy engil (slim) versiyasidan foydalanamiz
FROM python:3.11-slim

# Ishchi katalogni belgilaymiz
WORKDIR /app

# Atrof-muhit o'zgaruvchilarini o'rnatamiz
# PYTHONDONTWRITEBYTECODE 1 - .pyc fayllarni yozmaydi
# PYTHONUNBUFFERED 1 - loglarni buferlamasdan chiqaradi
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Tizimga kerakli kutubxonalarni o'rnatish (agar kerak bo'lsa)
# ffmpeg ovozli xabarlarni ishlash uchun kerak bo'lishi mumkin (whisper)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Talablar faylini nusxalaymiz va o'rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Qolgan kodni nusxalaymiz
COPY . .

# Botni ishga tushirish
CMD ["python", "main.py"]