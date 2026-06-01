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
