# Release Env Setup

Use this flow to prepare a publish-ready local release env in one step.

## 1) Generate `.env.release`

```powershell
.\scripts\deploy\init-release-env.ps1 `
  -Domain "your-domain.com" `
  -CertbotEmail "ops@your-domain.com"
```

This writes `.env.release` with:
- domain + certbot email
- strong random `POSTGRES_PASSWORD`
- strong random `SECRET_KEY`
- PostgreSQL `DATABASE_URL` / `ASYNC_DATABASE_URL`
- `CORS_ORIGINS` / `ALLOWED_ORIGINS`

## 2) Publish

```powershell
.\scripts\deploy\remote-publish.ps1 `
  -HostName "<server-ip-or-host>" `
  -UserName "<ssh-user>" `
  -Domain "your-domain.com" `
  -CertbotEmail "ops@your-domain.com" `
  -SshKeyPath "C:\Users\<you>\.ssh\id_rsa"
```

If `.env.release` is missing, `remote-publish.ps1` now auto-generates it before packaging.
