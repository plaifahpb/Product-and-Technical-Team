# Production Notes

## Recommended deployment
- Small team: Flask + SQLite + Waitress/Gunicorn
- Larger team: Flask + PostgreSQL + Gunicorn + Nginx
- Enterprise auth: replace demo login with Google Workspace / Microsoft Entra ID SSO

## Data editing policy
- Admin/Manager: create, edit, delete all tasks
- Staff: create/edit tasks
- Viewer: read-only
- Audit Log records create/update/delete operations

## Next hardening items
1. Replace plaintext demo passwords with password hashing.
2. Move config to environment variables.
3. Use PostgreSQL for concurrent writes.
4. Add SSO and owner-level permission mapping.
5. Schedule daily backup of database.
