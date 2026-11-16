# Westeros Travel Guide API

A tiny HTTP service that returns a fast fact about iconic places in the Seven Kingdoms
(King's Landing, Winterfell, The Wall and more). Locations are a hardcoded dictionary,
so there is no database. Built with Python 3 and only the standard library.

## What it does

| Endpoint | Response |
|---|---|
| `GET /` | Greeting |
| `GET /healthz` | `200` `{"status": "ok"}` (no database, instant) |
| `GET /locations` | List of available location slugs |
| `GET /locations/<slug>` | Name, region and a fast fact; `404` if unknown |

Example: `curl localhost:8080/locations/the-wall`

## How to run

Requires Python 3.8+. No dependencies to install.

```bash
./scripts/run.sh
```

## Port

The service listens on the `PORT` environment variable and defaults to **8080**.

```bash
PORT=9000 ./scripts/run.sh
```

## How to test

```bash
./scripts/test.sh
```

Exits 0 on success and prints a normalised summary line such as `TESTS: 7/7`.
The tests start the real server and call it over HTTP.

## Project layout

- `app.py` - HTTP server and routing
- `locations.py` - the hardcoded Westeros data
- `tests/test_app.py` - tests
- `scripts/run.sh`, `scripts/test.sh` - the course contract

## Container image (M3)

Build and smoke-test locally:

```bash
docker build -t westeros:dev .
docker run -d --rm --name westeros -e PORT=9123 -p 9123:9123 westeros:dev
curl --fail http://localhost:9123/healthz
docker stop westeros
```

The image runs `app.py` as user `1000:1000`. It listens on `0.0.0.0` and
uses the `PORT` environment variable, including ports other than 8080.

Pull requests run the tests. Every push to `main` runs the tests, builds the
image, smoke-tests `/healthz`, and scans for CRITICAL vulnerabilities with an
available fix. Only successful scans allow publication to:

```text
ghcr.io/itsuserisblessofgod/westeros-travel-guide:<full-commit-sha>
ghcr.io/itsuserisblessofgod/westeros-travel-guide:latest
```

`needs: test` prevents publication after failed tests. The publish job receives
`packages: write` and authenticates with GitHub's temporary `GITHUB_TOKEN`.
Third-party actions are pinned to full commit SHAs. Trivy's cache stays outside
the build context, and `.dockerignore` also excludes `.cache`, `.git` and `.env`.
Main-branch runs are not cancelled by newer pushes, so each commit can publish.

After the first successful publication, the package must be made public in its
GitHub package settings. Verify the final commit using the official course marker:

```bash
python3 mark_m3.py --repo https://github.com/itsuserisblessofgod/westeros-travel-guide
```

The marker is supplied by `inf345/inf345-week6-lab`. Its `--offline` option checks
files only; it does not prove that the image is public or runs successfully.

## GitOps deployment (M5)

Argo CD follows `main` and deploys the plain YAML files in `k8s/` into the
`default` namespace. Its Application is defined in `argocd/application.yaml`.
Automated sync applies changes from Git, `selfHeal` repairs manual changes,
and `prune` removes tracked resources that have been removed from Git.
The `app-secret` Secret is created separately on the cluster.

CI tests, builds, scans, and publishes the image. To deploy a published version,
change the full commit SHA in `k8s/deployment.yaml` and merge the change into
`main`. Keep each image bump in its own commit so it can be reverted independently.

The `M5 check` pull-request workflow runs the official marker against the pushed
commit in a temporary kind cluster on the GitHub runner. Check its output for
`SCORE: 100/100` before merging.

## Rollback

Argo CD deploys the `k8s/` folder from the `main` branch. To restore the previous
image, revert the image-bump commit and merge the revert into `main`.
Start from an up-to-date `main`, then create a rollback branch:

```bash
git switch main
git pull --ff-only
git switch -c rollback-image
git log --oneline -- k8s/deployment.yaml
git revert <image-bump-commit-sha>
git push -u origin rollback-image
```

Open a pull request from `rollback-image` to `main` and merge it. For a dedicated
image-bump PR merged with a merge commit, use `git revert -m 1 <merge-commit-sha>`.
For its individual image-bump commit or a squashed image-bump commit, use
`git revert <commit-sha>`.

Argo CD normally detects the change within three minutes. To request an immediate
refresh and inspect the result:

```bash
kubectl -n argocd annotate application westeros-travel-guide argocd.argoproj.io/refresh=normal --overwrite
kubectl -n argocd get application westeros-travel-guide
kubectl get deployment mine -o jsonpath='{.spec.template.spec.containers[0].image}'
```

Wait for `Synced` and `Healthy`, and confirm that the image has the previous SHA.
A `kubectl rollout undo` would be overwritten by self-healing while Git still
specifies the newer image. Reverting in Git preserves the deployment and rollback
history.
