Quyida sizning loyihangiz uchun namunaviy `README.md` faylini yozib beraman. Bu faylda loyihaning maqsadi, o‘rnatish bo‘yicha ko‘rsatmalar, foydalanish misollari va boshqa foydali ma'lumotlar kiritilgan bo‘ladi. Siz uni loyihangizning o‘ziga xos xususiyatlariga moslashtirib o‘zgartirishingiz mumkin.

---

# Telegram Parser Project

Bu loyiha Telegram guruhlaridan xabarlar va foydalanuvchi ma'lumotlarini yig‘ish, saqlash va boshqarish uchun mo‘ljallangan. Loyiha FastAPI orqali REST API, SQLAlchemy yordamida PostgreSQL databazasi va SQLAdmin bilan ma'muriy panelni taqdim etadi. Alembic migratsiyalari databaza sxemasini boshqarish uchun ishlatiladi.

## Loyiha maqsadi
- Telegram guruhlaridan xabarlar, foydalanuvchi ma'lumotlari va profil rasmlarini yig‘ish.
- Yig‘ilgan ma'lumotlarni PostgreSQL databazasida saqlash.
- FastAPI orqali ma'lumotlarni JSON formatida taqdim etish.
- SQLAdmin orqali ma'lumotlarni ko‘rish va boshqarish uchun veb-interfeys yaratish.

## Texnologiyalar
- **Python 3.12**: Asosiy dasturlash tili.
- **FastAPI**: REST API framework.
- **SQLAlchemy**: ORM va databaza migratsiyalari uchun.
- **Alembic**: Databaza sxemasini boshqarish.
- **PostgreSQL**: Ma'lumotlar bazasi.
- **SQLAdmin**: Ma'muriy veb-interfeys.
- **Asyncpg**: PostgreSQL uchun asinxron driver.

## O‘rnatish

### 1. Loyihani klonlash
```bash
git clone https://github.com/your-username/telegram-parser.git
cd telegram-parser
```

### 2. Virtual muhitni yaratish
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

### 3. Kerakli paketlarni o‘rnatish
```bash
pip install -r requirements.txt
```
`requirements.txt` faylini quyidagi tarkib bilan yarating:
```
fastapi==0.110.0
uvicorn==0.29.0
sqlalchemy==2.0.29
asyncpg==0.29.0
alembic==1.13.1
sqladmin==0.16.1
```

### 4. PostgreSQL sozlamalari
- PostgreSQL o‘rnatilgan bo‘lishi kerak (masalan, `sudo apt install postgresql` Linux uchun).
- `meta` foydalanuvchisi va `telegram_parser_db` bazasini yarating:
  ```bash
  psql -U postgres
  ```
  ```sql
  CREATE USER meta WITH PASSWORD 'your_password';
  CREATE DATABASE telegram_parser_db OWNER meta;
  GRANT USAGE, CREATE ON SCHEMA public TO meta;
  ```

### 5. `.env` faylini sozlash
Loyiha ildizida `.env` faylini yarating va quyidagi ma'lumotlarni qo‘shing:
```
DATABASE_URL=postgresql+asyncpg://meta:your_password@localhost/telegram_parser_db
```
Bu URL `alembic.ini` va ilova kodida ishlatiladi.

### 6. Alembic migratsiyalarini ishga tushirish
- `alembic.ini` faylida `sqlalchemy.url` ni `.env` dagi `DATABASE_URL` ga moslang:
  ```
  sqlalchemy.url = postgresql+asyncpg://meta:your_password@localhost/telegram_parser_db
  ```
- Dastlabki migratsiyani yarating va qo‘llang:
  ```bash
  alembic revision --autogenerate -m "Initial migration"
  alembic upgrade head
  ```

## Loyihani ishga tushirish

### 1. FastAPI serverini ishga tushirish
```bash
uvicorn src.api:app --reload
```
- `/messages` endpointiga `http://localhost:8000/messages` orqali kirishingiz mumkin.

### 2. SQLAdmin panelini ishga tushirish
```bash
uvicorn src.admin:app --reload
```
- Admin panelga `http://localhost:8000/admin` orqali kiring.

## Foydalanish misollari

### 1. Xabarlar ro‘yxatini olish (FastAPI)
```bash
curl http://localhost:8000/messages
```
**Javob** (agar ma'lumot bo‘lmasa):
```json
[]
```

### 2. Databaza holatini tekshirish
```bash
psql -U meta -d telegram_parser_db -c "SELECT COUNT(*) FROM messages;"
```

## Modelni o‘zgartirish va migratsiya
Agar `src/models.py` da o‘zgarish qilsangiz:
1. Modelni yangilang (masalan, yangi `status` maydonini qo‘shing).
2. Yangi migratsiyani yarating:
   ```bash
   alembic revision --autogenerate -m "Add status column"
   ```
3. Migratsiyani qo‘llang:
   ```bash
   alembic upgrade head
   ```

## Loyiha tuzilmasi
```
telegram-parser/
├── migrations/           # Alembic migratsiya fayllari
│   ├── env.py
│   └── versions/
├── src/                 # Asosiy kod
│   ├── api.py          # FastAPI endpointlari
│   ├── admin.py        # SQLAdmin sozlamalari
│   └── models.py       # SQLAlchemy modellari
├── .env                # Muhit o‘zgaruvchilari
├── alembic.ini         # Alembic konfiguratsiyasi
├── requirements.txt    # Kerakli paketlar
└── README.md           # Ushbu fayl
```

## Qo‘shimcha xususiyatlar
- **Profil rasmlari**: Keyingi bosqichda `user_profile_photo` va `group_profile_photo` uchun fayl saqlash va yuklash qo‘shiladi.
- **Telegram integratsiyasi**: Telegram API orqali ma'lumot yig‘ish uchun qo‘shimcha modul qo‘shilishi mumkin.

## Muallif
- Firdavs (GitHub: @Firdavs28033)

## Litsenziya
Ushbu loyiha MIT litsenziyasi ostida tarqatiladi.

---

