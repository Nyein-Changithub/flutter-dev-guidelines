# Flutter Dev Guidelines

The full guide, **Flutter Engineering Standards**, is a practical guide to building Flutter apps that are clean, fast, safe and easy to change, written for every role on a team: product owners, QA, beginners, junior and senior developers.

The rules work with any state-management approach. Code examples for state, dependency injection and navigation are shown for **GetX**, **Provider**, **Riverpod** and **Bloc**, with **go_router** for navigation outside GetX.

## What's inside

- **10 golden rules**: the one-page summary
- **18 sections**: project structure, naming and lint, architecture and design patterns, state management (with a guide to choosing between GetX, Provider, Riverpod and Bloc), dependency injection, navigation, networking, models, UI and design system, performance, security, error handling, environments, testing, Git and CI, documentation
- **Plain-language explanations** for non-technical readers
- **MUST / SHOULD / AVOID** rules with good and bad Dart examples
- **A glossary** of common terms

## How to read it

| File | Use it for |
|---|---|
| [`flutter-engineering-standards.html`](flutter-engineering-standards.html) | Reading in a browser: role filter, GetX / Provider / Riverpod / Bloc code switch, search, dark mode, saved checklists, copy buttons. Works on phones. |
| [`flutter-engineering-standards.md`](flutter-engineering-standards.md) | Reading on GitHub, or editing the guide |

Open the HTML file directly in any browser; it needs no internet connection or installation.

## Editing the guide

The Markdown file is the source. The HTML page is generated from it, so don't edit the HTML by hand.

```bash
# 1. Edit flutter-engineering-standards.md
# 2. Rebuild the HTML (needs Python 3 only, no packages)
python3 build_html.py
# 3. Commit both files
```

## Files

```text
.
├── README.md                          # This file
├── flutter-engineering-standards.md   # Source of the guide
├── flutter-engineering-standards.html # Generated, interactive page
└── build_html.py                      # Converts the .md into the .html
```
