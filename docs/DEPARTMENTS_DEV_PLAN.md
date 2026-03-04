# Departments Feature Development Plan

This document summarizes the work required to implement and deploy the
organization/departments feature on the admin UI (`/admin/users/departments`)
and the supporting backend API. It builds upon the earlier implementation
plan and artifacts already added to the repository.

## Overview

Departments provide an organizational hierarchy used for data scoping in
RBAC and user management. The front-end page allows administrators to view
the department tree, manage department records (create, update, delete),
assign members, and operate on department status. The backend exposes
RESTful endpoints under `/api/v1/admin/departments`.

This plan captures remaining development tasks, technical changes made, and
integration steps to finish the feature from a dev perspective.

## Backend Changes

1. **API Routes** - Added endpoints in `backend/api/v1/admin/__init__.py`:
   - `GET /departments` (supports `tree=true`)
   - `POST /departments`
   - `GET /departments/{id}`
   - `PUT /departments/{id}`
   - `DELETE /departments/{id}`
   - plus status, move, members, stats, options, etc.
2. **SQL DDL** - new `departments` table created by `docs/sql/001_create_departments.sql`.
3. **Permissions** - new codes `department:read`, `department:write` with
   checks in API and frontend.
4. **Authentication** - endpoints require admin authentication (tested with
   credentials `admin/admin123` in e2e script).
5. **E2E helper** - script `scripts/e2e_test_departments.py` performs login and
   CRUD operations to verify API.
6. **Migration** - Example migration script `scripts/migrate_departments.py`
   to import initial tree from JSON.

## Frontend Changes

1. **API module** - `frontend/src/api/modules/departments.js` defines all
   requests against `/api/v1/admin/departments` with helper `asDataResponse`.
2. **Page component** - `frontend/src/views/admin/users/DepartmentManagement.vue`:
   - Displays department tree with controls.
   - Uses reactive data and API calls to load list, create/edit/delete.
   - Includes dialogs for editing and member management.
   - Removed earlier static seed code; now uses `getDepartments({tree:true})`.
3. **Lint/build adjustments** - fixed template duplication and import issues.
   Added watchers and form validation.
4. **UI testing** - manually tested by running dev server and verifying page
   renders tree and operations succeed after backend start/login.

## Documentation & Seed Data

- `docs/departments_seed.json` contains example department hierarchy.
- `docs/DEPARTMENTS_IMPLEMENTATION_PLAN.md` outlines high-level plan and
  requirements.
- `docs/DEPARTMENTS_DEV_PLAN.md` (this doc) summarizes the concrete
  engineering work done.
- `docs/openapi/departments.yaml` describes the spec for external reference.

## Remaining Tasks

- [ ] Decide fate of the seed JSON (keep for demo or remove) and add
      instructions to import via migration script.
- [ ] Add automated backend tests for department endpoints.
- [ ] Add frontend unit tests (Vue component, API mocks) for CRUD logic.
- [ ] Add e2e coverage (Cypress/Playwright) to exercise UI flows from
      login through department management.
- [ ] Integrate department dropdowns on user creation/edit pages.
- [ ] Document permission requirements for department pages in RBAC guide.

## Deployment & Rollout

- Run SQL script `docs/sql/001_create_departments.sql` in production DB.
- Optionally run migration script with `docs/departments_seed.json`:
  ```bash
  python scripts/migrate_departments.py --dsn "postgres://..." --file docs/departments_seed.json
  ```
- Build frontend (`npm --prefix frontend run build`) and deploy assets.
- Ensure backend service is restarted with new routes and DB migrations.
- Assign initial departments and test with admin account.

## Verification Steps

1. **Backend smoke**: `curl -u admin:admin123 http://host/api/v1/admin/departments?tree=true` should return JSON tree.
2. **UI smoke**: Log in as admin, navigate to `/admin/users/departments`,
   create a new department, edit, delete it.
3. **Permission check**: Verify that a non-admin user (without
   `department:write`) can only view but not modify departments.
4. **RBAC integration**: When assigning a department to a user, ensure API
   call updates `user_departments` and subsequent data queries are filtered.

## Notes

- The UI component currently uses Element Plus; additional styling may be
  required depending on design guidelines.
- Tree operations and circular reference checks are implemented in Vue.
- The feature will enable later data-scope restrictions (e.g., viewing
  only matches in own department) by joining `user_departments`.

***
This document should be checked into version control (it lives at
`docs/DEPARTMENTS_DEV_PLAN.md`).
