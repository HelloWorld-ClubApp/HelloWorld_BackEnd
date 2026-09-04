# Supabase DB and Storage deployment guide

## 1. Supabase project values

- Project ref: `fwupktfmwgopspeuztte`
- API URL: `https://fwupktfmwgopspeuztte.supabase.co`
- Region: `ap-northeast-1`
- S3 endpoint: `https://fwupktfmwgopspeuztte.storage.supabase.co/storage/v1/s3`

Do not commit DB passwords, Supabase secret keys, S3 access keys, or email app passwords.
If a secret was pasted into chat or shared in a screenshot, rotate it before production deployment.

## 2. Required Supabase setup

1. In Supabase Storage, create a bucket named `uploads`.
2. Set the `uploads` bucket to public if the Flutter app should render images directly from `file_url`.
3. In Storage > S3 Configuration, enable S3 protocol.
4. Create a new S3 access key and keep the access key id and secret key only in backend environment variables.

## 3. Backend environment variables

Use `.env.supabase.example` as the template:

```env
DATABASE_URL=postgresql+psycopg2://postgres.fwupktfmwgopspeuztte:<DB_PASSWORD>@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres?sslmode=require
SECRET_KEY=<ROTATE_ME>
EMAIL_USER=<EMAIL_USER>
EMAIL_PASSWORD=<EMAIL_APP_PASSWORD>
EMAIL_FROM=<EMAIL_FROM>
SUPABASE_URL=https://fwupktfmwgopspeuztte.supabase.co
SUPABASE_STORAGE_BUCKET=uploads
SUPABASE_STORAGE_PUBLIC_BASE_URL=https://fwupktfmwgopspeuztte.supabase.co/storage/v1/object/public/uploads
SUPABASE_S3_ENDPOINT=https://fwupktfmwgopspeuztte.storage.supabase.co/storage/v1/s3
SUPABASE_S3_REGION=ap-northeast-1
SUPABASE_S3_ACCESS_KEY_ID=<S3_ACCESS_KEY_ID>
SUPABASE_S3_SECRET_ACCESS_KEY=<S3_SECRET_ACCESS_KEY>
```

Use the Supavisor pooler URL above for local deployment if the direct DB host only resolves to IPv6.

## 4. DB initialization and migration

After the real Supabase `DATABASE_URL` is configured, install dependencies:

```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
```

For a brand-new empty Supabase DB, start the API once so FastAPI creates the current SQLAlchemy schema:

```powershell
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

After startup succeeds, stop the server and stamp the DB at the current Alembic head:

```powershell
venv\Scripts\python.exe -m alembic stamp head
venv\Scripts\python.exe -m alembic current
```

For an already initialized DB, use Alembic migrations normally:

```powershell
venv\Scripts\python.exe -m alembic upgrade head
```

If this repository virtualenv is broken, recreate it first:

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

On this PC, `python`/`py` may not be on PATH. In that case, run the same command with an installed Python executable path.

## 5. File flow after the change

- `POST /api/v1/files/upload` uploads the file to Supabase Storage through the S3 endpoint.
- The `files.file_url` DB column stores the public Supabase object URL.
- `GET /api/v1/files/{file_id}/download` still works. For Supabase files, it redirects to the public object URL with a `download` query parameter.
- Existing local `/uploads/...` file records are still readable through the legacy FastAPI static mount while the old files remain on the server.

## 6. Frontend URL handling

Render `file_url`, `file_absolute_url`, `profile_image_url`, and `background_image_url` as-is when the value starts with `http://` or `https://`.

For old values that start with `/uploads`, prefix the backend API base URL during the migration period.
