# Incremental Promotion Pipeline

This pipeline enforces:

1. local checks
2. testing deployment
3. staging deployment
4. production deployment

Each deployment only syncs git deltas from `baseCommit..targetCommit` and does not upload the full workspace.

## Scripts

- `scripts/deploy/incremental-publish.ps1`
: single environment incremental deploy (`A/M/R` upload, `D/R-old` delete)
- `scripts/deploy/promote-chain.ps1`
: multi-stage promotion runner
- `scripts/deploy/promotion-pipeline.template.json`
: config template

## 1) Prepare pipeline config

Copy template:

```powershell
Copy-Item scripts/deploy/promotion-pipeline.template.json scripts/deploy/promotion-pipeline.json
```

Then edit `scripts/deploy/promotion-pipeline.json`:

- set testing/staging server IP/domain
- set each `remoteDir`
- keep/override `postDeployCommand`
- set `healthCheckUrl`
- set `enabled` for each stage

## 2) First-time baseline

Incremental deploy needs baseline commit at remote:

- file path on remote: `<remoteDir>/.deploy/last_commit`

If missing, set `initialBaseCommit` in that stage config for the first run.

You can use:

```powershell
git rev-parse HEAD~1
```

After first successful deploy, script auto-updates baseline to target commit.

## 3) Run full chain

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy/promote-chain.ps1
```

Optional:

- dry run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy/promote-chain.ps1 -DryRun
```

- skip local checks:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy/promote-chain.ps1 -SkipLocalChecks
```

- target specific commit:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy/promote-chain.ps1 -TargetCommit <commit>
```

## 4) Rollback safety

Every incremental deploy creates backup tar on remote:

- backup dir: `${remoteDir}_patch_backups`
- retention: configurable (`keepBackups`, default 10)

For release-level rollback (full directory backup) continue using:

- `scripts/deploy/remote-publish.ps1`
