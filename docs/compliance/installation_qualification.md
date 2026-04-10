# Installation Qualification (IQ)

**Document ID:** IQ-TRPM-LIMS-001
**Version:** 0.1 (DRAFT)
**Execution date:** TODO
**Executed by:** TODO

## 1. Purpose

Confirm that TRPM-LIMS has been installed in accordance with the approved
configuration and that all supporting components are present and correctly
versioned.

## 2. Test environment

| Item | Expected | Actual | Pass/Fail | Evidence |
|---|---|---|---|---|
| Operating system | [TODO] | | | Screenshot |
| Python version | 3.12.x | | | `python --version` output |
| Django version | 6.0.x | | | `pip show django` |
| PostgreSQL version | 16.x | | | `psql --version` |
| Redis version | 7.x | | | `redis-cli --version` |
| Nginx version | 1.27.x | | | `nginx -v` |
| TRPM-LIMS git SHA | [TODO] | | | `git rev-parse HEAD` |

## 3. Environment variables

| Variable | Expected | Present? | Evidence |
|---|---|---|---|
| `SECRET_KEY` | set (not `django-insecure-*`) | | — |
| `DEBUG` | `False` | | — |
| `ALLOWED_HOSTS` | production hostnames | | — |
| `DATABASE_URL` | production Postgres DSN | | — |
| `ENABLE_PART11` | `True` (clinical) | | — |
| `ENABLE_HIPAA_MODE` | `True` (clinical) | | — |
| `SENTRY_DSN` | set | | — |

## 4. Django deploy check

Expected output: `System check identified no issues (X silenced).`

```
$ python manage.py check --deploy
```

Actual output: TODO — paste console output.

## 5. Database migrations

```
$ python manage.py showmigrations
```

Expected: all migrations marked `[X]` (applied). Actual: TODO.

## 6. Backup configuration

| Item | Expected | Actual | Pass/Fail |
|---|---|---|---|
| Nightly database backup scheduled | Yes | | |
| Backup retention ≥ 30 days | Yes | | |
| Backup restore drill completed | Within 30 days | | |

## 7. Result

| Item | Pass / Fail |
|---|---|
| All sections above pass | |
| Deviations logged | |

## 8. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Executor | | | |
| QA Reviewer | | | |
| System Owner | | | |
