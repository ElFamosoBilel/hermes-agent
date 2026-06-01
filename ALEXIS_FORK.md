# Alexis Hermes Agent Fork

This fork adapts NousResearch Hermes Agent for one job: a private ticket coach
for the Alexis Discord bot.

## Target

The agent is admin-facing only. It helps Bilel inspect a ticket and ask:

- why Alexis IA replied;
- why Alexis IA stayed silent;
- whether a staff answer, prior bot answer, reaction, or takeover state was
  ignored;
- what rule should be added before the public bot answers a similar ticket.

It does not send messages to customers by default. Customer-facing actions stay
behind the existing Alexis bot approval/validation paths.

## Hermes Surfaces Reused

- `plugins/platforms/discord`: already supports Discord bot access,
  `DISCORD_ALLOWED_USERS`, role checks, slash commands, threads and reactions.
- `tools/memory_tool.py`: persistent operator-curated memory.
- `tools/session_search_tool.py`: session recall for previous audits.
- `skills/`: the Alexis-specific ticket-coach prompt lives in
  `skills/customer-support/alexis-ticket-coach/SKILL.md`.

## Alexis Runtime Contract

Expected env for the Alexis deployment:

```bash
ALEXIS_BOT_ROOT=/opt/alexis-bot
ALEXIS_DATA_DIR=/opt/alexis-bot/data-prod
DISCORD_ALLOWED_USERS=<bilel_discord_id>
DISCORD_HOME_CHANNEL=<private_admin_channel_id>
```

Read-only inputs:

- `$ALEXIS_DATA_DIR/tickets.json`
- `$ALEXIS_DATA_DIR/ai-usage.jsonl`
- `$ALEXIS_DATA_DIR/ai-feedback.jsonl`
- `$ALEXIS_DATA_DIR/ai-memory.jsonl`
- `$ALEXIS_DATA_DIR/ai-takeover.json`
- `$ALEXIS_DATA_DIR/transcripts/*.txt`

Write targets:

- Hermes memory/session state;
- later, explicit manager-approved lessons into Alexis memory.

## First Integration Step

The live Alexis dashboard now exposes the first version of this pattern as
`Coach IA`: it reads the same logs/transcripts and lets Bilel ask the agent
ticket-specific questions without sending anything into Discord.

The fork is reserved for the fuller Hermes-native version: Discord DM/admin
channel interface, durable Hermes memory, slash commands, and replay tools.

## Local Setup

Install the fork locally:

```bash
cd /Users/bilelgoat/Desktop/Projets/hermes-agent-alexis
./setup-hermes.sh
```

Enable Hermes API server for the Alexis dashboard/backend bridge:

```bash
touch ~/.hermes/.env
chmod 600 ~/.hermes/.env
HERMES_API_KEY="$(openssl rand -hex 24)"
cat >> ~/.hermes/.env <<'EOF'
API_SERVER_ENABLED=true
API_SERVER_HOST=127.0.0.1
API_SERVER_PORT=8642
API_SERVER_MODEL_NAME=hermes-agent
ALEXIS_BOT_ROOT=/Users/bilelgoat/Desktop/Projets/alexis-bot
ALEXIS_DATA_DIR=/Users/bilelgoat/Desktop/Projets/alexis-bot/data-prod
EOF
printf 'API_SERVER_KEY=%s\n' "$HERMES_API_KEY" >> ~/.hermes/.env

hermes gateway run
```

Then point Alexis at it:

```bash
# Admin coach only
ALEXIS_COACH_AI_PROVIDER=hermes
ALEXIS_HERMES_BASE_URL=http://127.0.0.1:8642/v1
ALEXIS_HERMES_API_KEY=<same value as API_SERVER_KEY>

# Later, only after shadow/testing, customer replies through existing Alexis gates
# ALEXIS_AI_PROVIDER=hermes
```

Ticket evidence smoke check:

```bash
python skills/customer-support/alexis-ticket-coach/scripts/inspect_ticket.py \
  --data-dir /Users/bilelgoat/Desktop/Projets/alexis-bot/data-prod \
  --ticket 0090
```

## Customer Response Decision

Hermes is interesting for customer responses only as an LLM/backend behind
Alexis' existing responder. Do not run Hermes' Discord gateway as a second bot
inside public ticket channels: it would need to reimplement ticket status,
owner checks, history gates, takeover logic, rate limits, and manager validation.
