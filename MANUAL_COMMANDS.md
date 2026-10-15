# ═══════════════════════════════════════════════════════════════
# COMANDOS FINALES PARA EJECUTAR LOCALMENTE (requieren gh/vercel CLI)
# ═�══════════════════════════════════════════════════════════════

# 1. AUTENTICACIÓN PREVIA
gh auth login
vercel login

# 2. BRANCH PROTECTION — 8 FLAGSHIPS
REPOS=("ManosAbiertas" "linguaforge" "belentani.es" "Cruzando-el-charco" "secure-t" "open-school" "judas-experience-web" "Belentani.cv-ai")
for REPO in "${REPOS[@]}"; do
  echo "🔒 Protegiendo main en belentani7/$REPO..."
  gh api -X PUT "/repos/belentani7/$REPO/branches/main/protection"     -H "Accept: application/vnd.github.v3+json"     -f required_status_checks[strict]=true     -f required_status_checks[contexts][]="build"     -f required_status_checks[contexts][]="typecheck"     -f required_status_checks[contexts][]="test"     -f required_status_checks[contexts][]="lint"     -f enforce_admins=true     -f required_pull_request_reviews[required_approving_review_count]=1     -f required_pull_request_reviews[dismiss_stale_reviews]=true     -f required_pull_request_reviews[require_code_owner_reviews]=true
done

# 3. VERCEL → MAIN BRANCH (5 proyectos desplegando desde Dependabot)
PROJECTS=("manos-abiertas" "belentani-es" "linguaforge" "cruzando-el-charco" "secure-t" "open-school" "judas-experience-web" "belentani-cv-ai")
for P in "${PROJECTS[@]}"; do
  echo "🔧 Configurando $P → main..."
  vercel project update "$P" --production-branch main
done

# 4. DESACTIVAR GITHUB PAGES EN belentani.es (conflicto DNS 404)
gh api -X DELETE /repos/belentani7/belentani.es/pages

# 5. PURGAR ZIP DE HISTORIAL (open-school) — OPCIÓN A: BFG (recomendado, purga historia completa)
# git clone --mirror https://github.com/belentani7/open-school.git
# cd open-school.git
# java -jar bfg.jar --delete-files "open-school-secure-t-coupling.zip"
# git reflog expire --expire=now --all && git gc --prune=now --aggressive
# git push --force

# OPCIÓN B: GitHub API (solo elimina de HEAD, historia permanece)
FILE_SHA=$(gh api /repos/belentani7/open-school/contents/open-school-secure-t-coupling.zip --jq '.sha')
gh api -X DELETE /repos/belentani7/open-school/contents/open-school-secure-t-coupling.zip \
  -f message="security: remove sensitive coupled zip artifact from history" \
  -f sha="$FILE_SHA" \
  -f branch="main"

# 6. VERIFICAR PRs CREADAS Y MERGEAR TRAS CI VERDE
# Belentani.cv-ai #32, lingua-aberta #15, judas-experience-web #21, open-school #16, belentani.es #20, ManosAbiertas #19

# 7. CONFIGURAR VERCEL KV PARA Belentani.cv-ai (rate limiting)
# En Vercel Dashboard → Project → Storage → Create KV Database
# Luego: vercel env add KV_REST_API_URL, KV_REST_API_TOKEN, KV_REST_API_READ_ONLY_TOKEN

# 8. INSTALAR HERRAMIENTAS FALTANTES
# Docker Desktop
# uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# Polars/DuckDB: pip install polars duckdb pyarrow
# gcloud: https://cloud.google.com/sdk/docs/install
# BFG Repo-Cleaner: https://rtyley.github.io/bfg-repo-cleaner/

# ════════════════════════════════════════════════════════════════
# RESUMEN DE PRs CREADAS (draft, listas para review tras CI verde)
# ═══════════════════════════════════════════════════════════════
# 1. Belentani.cv-ai #32  — fix(security): AI endpoint hardening (Zod + rate-limit + secure errors)
# 2. lingua-aberta #15      — fix(security): CI + docker-compose + synthetic data
# 3. judas-experience-web #21 — fix(threejs): vendor/ → npm three@0.185.0
# 4. open-school #16        — fix(security): .gitignore + CI pnpm + ZIP removal note
# 5. belentani.es #20       — fix(ci): comprehensive pipeline (typecheck, lint, test, lighthouse)
# 6. ManosAbiertas #19      — fix(security): remove db:push --accept-data-loss + comprehensive CI
# 7. belentani-design-system feat/design-system-v2 — @belentani/ui package (Button, Card, tokens.css)
# 8. belentani-python-template (duck) — Canonical FastAPI+Pydantic+SQLModel+uv+Ruff template

# ═══════════════════════════════════════════════════════════════
# PRÓXIMOS PASOS (30 días para verde total)
# ═══════════════════════════════════════════════════════════════
# Semana 1: Mergear PRs tras CI verde, branch protection, Vercel fix
# Semana 2: Design System @belentani/ui → integrar en 4 flagships
# Semana 3: Python template → migrar open-school backend, secure-t API
# Semana 4: Starlight docs portal, Lighthouse 95+, axe-core 0 violations
# Mes 2: MCP servers, observabilidad, portfolio verde en belentani.es
