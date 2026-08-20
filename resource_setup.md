# Setup Guide

This guide covers everything needed to get all four comparison platforms running and connected before executing the loaders and benchmarks. Follow it top to bottom for a fresh environment.

**Time estimate:** ~30–45 minutes for all four platforms, most of it waiting on cloud provisioning.

---

## 0. Prerequisites

- Python 3.10+
- Docker (for the self-hosted Neo4j comparison instance)
- A free/trial account with each cloud platform below (no credit card required for any of them)

### Clone and set up the Python environment

```bash
git clone <this-repo-url>
cd <repo-folder>

python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Create your `.env` file

```bash
cp .env.example .env
```

You'll fill in each value as you complete the setup steps below. **Never commit `.env` — it's already listed in `.gitignore`.**

---

## 1. CognoDB Cloud

1. Go to [console.cognodb.com/signup](https://console.cognodb.com/signup) and create a free account (no credit card).
2. From the console, create a free (**c0**) instance and pick a region. Provisioning takes under a minute.
3. **Copy the generated password immediately** — it is shown exactly once. If missed, reset it from the instance's settings page.
4. Note your connection URI, shown in the form:
   ```
   bolt+s://<instance-id>.databases.cognodb.cloud
   ```

**Add to `.env`:**
```
COGNODB_URI=bolt+s://<your-instance-id>.databases.cognodb.cloud
COGNODB_USER=cognodb
COGNODB_PASSWORD=<your saved password>
```

**Verify:**
```bash
python3 scripts/test_cognodb.py
```
Expected output: `Hello CognoDB`

**Advertised free tier specs (document these — required for fairness):**
`0.5 vCPU (burstable), 256 MB RAM, 1 GB disk`

---

## 2. Memgraph Cloud

1. Go to [memgraph.com/cloud](https://memgraph.com/cloud) and sign up. Confirm the current free-tier terms on the signup page itself, since cloud tier offerings change.
2. Create a project, then create a new instance on the smallest/free tier available.
3. Note the host, port (default Bolt port `7687`), and the username/password you set during creation.
4. Memgraph Cloud uses a **self-signed certificate** — connections must use the `bolt+ssc://` URI scheme (encrypted, but skips strict CA verification), not `bolt+s://`.

**Add to `.env`:**
```
MEMGRAPH_HOST=<your-instance-host>
MEMGRAPH_PORT=7687
MEMGRAPH_USERNAME=<your username>
MEMGRAPH_PASSWORD=<your password>
```

**Verify:**
```bash
python3 scripts/test_memgraph.py
```
Expected output: confirmation message printed from a created test node.

**Document your instance's advertised specs** (vCPU/RAM/storage) from the Memgraph Cloud console for the fairness table.

> **Caveat to note in your README:** the `gqlalchemy` client (used for loading) and the raw `neo4j` driver (used for benchmarking) handle Memgraph's self-signed certificate differently by default — `gqlalchemy`'s `encrypted=True` works out of the box, while the `neo4j` driver requires the explicit `bolt+ssc://` scheme.

---

## 3. ArangoDB Oasis

1. Go to [dashboard.arangodb.cloud](https://dashboard.arangodb.cloud) and sign up.
2. Confirm the current free trial terms on the signup page — Oasis is typically **trial-credit based** rather than a perpetual free tier. Record the credit amount and expiry for your README's fairness notes.
3. Click **Create Deployment**, choose the smallest available tier, pick a region close to your other instances, and create it. This can take a few minutes to provision.
4. From the deployment's **Connect** tab, copy:
   - The endpoint URL (e.g. `https://<deployment-id>.arangodb.cloud:18529`)
   - The root username/password (set at creation)
   - The **base64-encoded CA certificate** shown in the sample connection code

**Add to `.env`:**
```
ARANGO_HOST=https://<your-deployment-id>.arangodb.cloud:18529
ARANGO_USER=root
ARANGO_PASSWORD=<your password>
ARANGO_DB=_system
ARANGO_CA_B64=<the long base64 string from the dashboard>
```

**Verify:**
```bash
python3 scripts/test_arango.py
```
Expected output: the connected server version, plus confirmation of a test document insert.

> Note: this creates `cert_file.crt` in your project root (the decoded CA certificate). It's already listed in `.gitignore` — never commit it.

**Document your deployment's advertised specs** for the fairness table.

---

## 4. Local Neo4j (Docker, resource-capped)

This instance is capped to match CognoDB's free tier (0.5 vCPU / 256 MB RAM), for a direct "managed free tier vs. self-hosted at identical specs" comparison point.

**Install Docker** (skip if already installed):
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
```

**Run the container:**
```bash
docker run -d \
  --name neo4j-benchmark \
  --cpus="0.5" \
  --memory="256m" \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/<choose-a-password> \
  -v neo4j_data:/data \
  neo4j:5-community
```

Wait ~20–30 seconds, then confirm it's up:
```bash
docker ps
docker logs neo4j-benchmark
```
Look for `Started.` in the logs.

**Add to `.env`:**
```
LOCAL_NEO4J_URI=bolt://localhost:7687
LOCAL_NEO4J_USER=neo4j
LOCAL_NEO4J_PASSWORD=<the password you set above>
```

**Verify:**
```bash
python3 scripts/test_neo4j_local.py
```

> **Known limitation to note in your README:** Docker's `--cpus`/`--memory` flags cap CPU and RAM cleanly, but do **not** cap disk usage at the volume level (that requires filesystem-level quotas, e.g. XFS project quotas, which is out of scope here). Disk parity is instead maintained by keeping the dataset small enough to stay well under 1 GB regardless of platform — state this explicitly rather than implying a hard disk cap exists.

**If you reset the container and hit an `AuthError` on reconnect:** Neo4j's `NEO4J_AUTH` env var only sets the password on the *first-ever* startup of a fresh volume. If you're reusing an old `neo4j_data` volume, wipe it first:
```bash
docker stop neo4j-benchmark && docker rm neo4j-benchmark
docker volume rm neo4j_data
```
Then re-run the `docker run` command above.

---

## 5. Confirm everything is connected

Run all four connection tests in sequence:
```bash
python3 scripts/test_cognodb.py
python3 scripts/test_memgraph.py
python3 scripts/test_arango.py
python3 scripts/test_neo4j_local.py
```

All four should print a success message with no errors. If any fail, see the **Troubleshooting** section below before moving on to data loading.

---

## 6. Resource specs summary (fill this in as you go)

Document each platform's actual advertised tier here — this table belongs in your main `README.md`'s methodology section too:

| Platform | vCPU | RAM | Storage | Tier type |
|---|---|---|---|---|
| CognoDB | 0.5 (burstable) | 256 MB | 1 GB | Free |
| Memgraph Cloud | *fill in* | *fill in* | *fill in* | *fill in* |
| ArangoDB Oasis | *fill in* | *fill in* | *fill in* | Trial credits |
| Neo4j (local, Docker) | 0.5 (capped) | 256 MB (capped) | not disk-capped — see note above | Self-hosted |

---

## Troubleshooting

**`ModuleNotFoundError`** — your venv isn't active, or dependencies weren't installed. Run `source venv/bin/activate` then `pip install -r requirements.txt` again.

**`SSLCertVerificationError: self-signed certificate` (Memgraph)** — you're using `bolt+s://` instead of `bolt+ssc://`. See section 2 above.

**`neo4j.exceptions.AuthError`** — credentials don't match what's actually stored.
- *CognoDB/Memgraph/ArangoDB*: the password was shown once at creation; if lost, reset it from that platform's console.
- *Local Neo4j*: see the volume-wipe steps in section 4.

**Connection timeout on a freshly created cloud instance** — cloud instances (CognoDB, Memgraph, ArangoDB) can take 30–90 seconds after creation before they're fully responsive. Wait and retry.

**ArangoDB `verify_override` errors** — confirm `cert_file.crt` exists in your project root and `ARANGO_CA_B64` in `.env` is the complete, unbroken base64 string (copy-paste can sometimes truncate very long values).

---

## Next steps

Once all four platforms are connected, proceed to loading the dataset — see `README.md` → **Running the Benchmark** for the full loader and benchmark script sequence.
