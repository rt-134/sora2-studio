# 🎬 VETREX STUDIO — Sora-2

واجهة ويب احترافية لتوليد الفيديوهات باستخدام نموذج Sora-2 من VETREX AI

## ✨ الميزات

- **توليد الفيديو من النص** (Text-to-Video) — أنشئ مشاهد سينمائية من وصف نصي
- **تحريك الصور** (Image-to-Motion) — أضف الحركة والحياة للصور الثابتة
- **نسب عرض مرنة** — 16:9 • 9:16 • 1:1
- **واجهة عربية أنيقة** — تصميم سيبربانك حديث مع RTL كامل
- **وحدة تحكم لايف** — متابعة التوليد في الوقت الفعلي
- **أرشيف الجلسة** — حفظ الفيديوهات المولدة محلياً

## 🚀 التشغيل السريع

### المتطلبات
- Python 3.8 أو أحدث
- pip

### التثبيت والتشغيل

```bash
# 1. استنساخ المستودع
git clone https://github.com/rt-134/sora2-studio.git
cd sora2-studio

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. التشغيل
python app.py
```

### الوصول
افتح المتصفح على:
```
http://localhost:5000
```

## 📡 الـ API Endpoints

| المسار | الطريقة | الوصف |
|--------|--------|--------|
| `/` | GET | الصفحة الرئيسية |
| `/api/generate` | POST | توليد فيديو من نص |
| `/api/edit` | POST | تحريك صورة مع نص |
| `/api/results/<task_id>` | GET | الحصول على نتيجة المهمة |
| `/api/upload` | POST | رفع صورة |
| `/uploads/<name>` | GET | تحميل الملف |

## 🌐 النشر

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

### Render / Railway
ربط المستودع مباشرة على المنصة

## 👨‍💻 المطور
VETREX AI Team
