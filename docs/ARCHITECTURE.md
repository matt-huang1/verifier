# Architecture

> **Status: scaffold.** Fill in as the core takes shape (step C). Do not describe
> structure that doesn't exist yet.

## Core principle

The model proposes; deterministic code judges. See
[decisions/0001](decisions/0001-deterministic-verification-not-llm-judging.md).

## Shape (intended)

A surface-agnostic core — `verify(claim, url, quote) -> Verdict` — with the CLI and the
MCP tool as thin adapters over it. See
[decisions/0002](decisions/0002-cli-before-mcp.md).

## Module map

_To be written once modules exist._
