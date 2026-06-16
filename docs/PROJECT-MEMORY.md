> Mémoire projet synchronisée Mac↔PC via Git. MAJ 2026-06-16.

# Hermes Agent — Fork Alexis

## But

Fork local du projet open-source Hermes Agent, adapté pour le bot Alexis IA (support tickets casino). Sert de gateway IA entre le bot Discord Alexis et ChatGPT Pro (compte Bilel). Deux instances tournent en prod sur VPS1 : une pour les tickets/coach/admin, une pour le monitor (modèle cheap).

## Stack

- **Langage** : Python (hermes_agent.egg-info, setup.py, pyproject)
- **Framework** : Hermes Agent (ACP adapter, gateway OpenAI-compatible)
- **Config principale** : `cli-config.yaml` (pattern : `cli-config.yaml.example`)
- **Skills** : `skills/` (GSC, etc.)
- **Upstream LLM** : `https://chatgpt.com/backend-api/codex` (ChatGPT Pro Bilel), credential_pool OAuth multi-creds
- **Discord bot dédié** : App ID `1498873968340500591` (bot Hermes gateway, séparé du bot Alexis)
- **Remote** : `https://github.com/ElFamosoBilel/hermes-agent.git`

## Branche / état git

- **Branche** : `main`
- **Commits récents** : `Make Alexis ticket coach evidence-driven`, `Add Alexis ticket coach adaptation`, `chore(release): map Subway2023 for PR #14639 salvage`
- **Fichier clé** : `ALEXIS_FORK.md` — explique les adaptations spécifiques au fork Alexis
- **AGENTS.md** : 439 lignes, contient le DOD et les règles du projet

## Déploiement

- **VPS1** `161.97.182.7`
- **Systemd** : `hermes-gateway` (port 8642, modèle `hermes-agent`, tickets/coach/admin) + `hermes-gateway-alexisfast` (port 8643, modèle `gpt-5.3-codex-spark`, monitor/reflect cheap)
- **Config VPS** : `~/projects/melchior/` (contexte projet Melchior), path Hermes sur VPS2 (legacy, migré sur VPS1)
- **Restart après changement** : `systemctl restart hermes-gateway hermes-gateway-alexisfast`
- **Secrets** : dans `.env` sur VPS1, jamais ici

## Patterns & gotchas

- **SOUL.md bypass** : fichier `SOUL.md` anti-moralizing valide (2026-05-08). NE PAS utiliser `--ignore-rules`. Débloque facture/cyber.
- **Scanner anti-prompt-injection interne Hermes** : Hermes a un scanner interne qui peut bloquer certaines formulations légitimes (découvert 2026-05-08). Certaines formulations multi-action bloquées par le filtre Fable au niveau provider.
- **Credential pool** : `credential_pool` avec rotation OAuth multi-creds. JAMAIS 2 process qui partagent le même `codex-auth.json` (race condition refresh_token = invalidation). Le bot Alexis et Hermes partagent le même compte ChatGPT — quota fenêtre unique 5h+hebdo.
- **Hermes direct (pas skillclaw)** : depuis 2026-05-18, Hermes appelle `codex.raphcvr.me` en direct. `skillclaw` et `watchdog` désactivés.
- **EnvironmentFile drop-in** : fix 401 via `auth.json` pool + EnvironmentFile drop-in.
- **`auxiliary.compression`** : activé (option Hermes).
- **raphcvr** : provider défini mais PAS défaut. `fallback_providers: []` vide → panne Hermes = erreur dure, SPOF, recovery manuelle.
- **GSC skill** : `skills/gsc/` (CLI `gsc`, venv 3.12, creds `/root/.config/hermes/gsc-sa.json` sur VPS1).
- **Pas de mémoire** : config.yaml prod = PAS de mémoire activée (vérifié 2026-06-02).

## Backlog

- Activer failover automatique si ChatGPT Pro down
- Exposer les headers `x-codex-*` (quota 5h/hebdo) pour le dashboard Alexis
- Documenter le flow de rotation credential_pool
