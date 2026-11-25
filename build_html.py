#!/usr/bin/env python3
"""Build flutter-engineering-standards.html from the Markdown source.

Usage: python3 context/docs/standards/build_html.py
Edit the .md file, then re-run this script. No third-party packages needed.
"""

import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "flutter-engineering-standards.md"
OUT = HERE / "flutter-engineering-standards.html"

RULE_WORDS = {"MUST", "MUST NOT", "SHOULD", "AVOID"}


def slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text or "section"


def inline(text: str) -> str:
    codes: list[str] = []

    def stash(m: re.Match) -> str:
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)

    def bold(m: re.Match) -> str:
        inner = m.group(1)
        if inner in RULE_WORDS:
            cls = inner.split()[0].lower() + ("-not" if inner == "MUST NOT" else "")
            return f'<span class="rule rule-{cls}">{inner}</span>'
        return f"<strong>{inner}</strong>"

    text = re.sub(r"\*\*(.+?)\*\*", bold, text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>',
        text,
    )
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


FRAMEWORKS = ("getx", "provider", "riverpod", "bloc", "go_router")


def render_code(lang: str, code: str) -> str:
    return (
        f'<div class="code"><div class="code-bar"><span>{lang}</span>'
        f'<button class="copy" type="button" aria-label="Copy code">Copy</button></div>'
        f'<pre><code class="lang-{lang}">{html.escape(code)}</code></pre></div>'
    )


def render_tabs(group: int, tabs: list[tuple[str, str, str]]) -> str:
    buttons, panels = [], []
    for n, (label, lang, code) in enumerate(tabs):
        fw = " ".join(k for k in FRAMEWORKS if k in label.lower()) or slug(label)
        tid, pid = f"t{group}-{n}", f"p{group}-{n}"
        on = n == 0
        buttons.append(
            f'<button class="tab" role="tab" type="button" id="{tid}" aria-controls="{pid}" '
            f'aria-selected="{str(on).lower()}" tabindex="{0 if on else -1}" data-fw="{fw}">{html.escape(label)}</button>'
        )
        panels.append(
            f'<div class="tab-panel" role="tabpanel" id="{pid}" aria-labelledby="{tid}" '
            f'data-label="{html.escape(label)}"{"" if on else " hidden"}>{render_code(lang, code)}</div>'
        )
    return (
        '<div class="tabs" data-tabs><div class="tab-list" role="tablist" aria-label="Code example by approach">'
        + "".join(buttons) + "</div>" + "".join(panels) + "</div>"
    )


def render_table(rows: list[str]) -> str:
    def cells(row: str) -> list[str]:
        return [c.strip() for c in row.strip().strip("|").split("|")]

    head = cells(rows[0])
    body = [cells(r) for r in rows[2:]]
    out = ['<div class="table-wrap"><table><thead><tr>']
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def audience_badges(text: str) -> tuple[str, list[str]]:
    raw = re.sub(r"\*\*Audience:\*\*", "", text).strip()
    parts = [p.strip() for p in re.split(r",\s*|\s+and\s+(?![^()]*\))", raw) if p.strip()]
    keys: list[str] = []
    out = []
    for part in parts:
        m = re.match(r"^([^()]+?)\s*(?:\((.*)\))?$", part)
        name, note = (m.group(1), m.group(2)) if m else (part, None)
        key = name.split()[0].lower()
        keys.append(key)
        out.append(f'<span class="badge badge-{key}">{html.escape(name)}</span>')
        if note:
            out.append(f'<span class="badge-note">{inline(note)}</span>')
    if "non-technical" in raw.lower() and "non-technical" not in keys:
        keys.append("non-technical")
    return f'<p class="audience"><span class="audience-label">For</span>{"".join(out)}</p>', keys


def convert(md: str):
    lines = md.splitlines()
    i = 0
    header_parts: list[str] = []
    sections: list[dict] = []
    cur: list[str] | None = None
    title = ""
    checklist_n = 0
    tab_group = 0

    def emit(s: str) -> None:
        (cur if cur is not None else header_parts).append(s)

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if not s or s == "---":
            i += 1
            continue

        if s == "<!-- tabs -->":
            tab_group += 1
            i += 1
            tabs = []
            while i < len(lines) and lines[i].strip() != "<!-- /tabs -->":
                label = re.match(r"^\*\*(.+?)\*\*$", lines[i].strip())
                if not label:
                    i += 1
                    continue
                i += 1
                while not lines[i].strip().startswith("```"):
                    i += 1
                lang = lines[i].strip()[3:].strip() or "text"
                i += 1
                buf = []
                while not lines[i].strip().startswith("```"):
                    buf.append(lines[i])
                    i += 1
                i += 1
                tabs.append((label.group(1), lang, "\n".join(buf)))
            i += 1
            emit(render_tabs(tab_group, tabs))
            continue

        if s.startswith("```"):
            lang = s[3:].strip() or "text"
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            code = html.escape("\n".join(buf))
            emit(
                f'<div class="code"><div class="code-bar"><span>{lang}</span>'
                f'<button class="copy" type="button" aria-label="Copy code">Copy</button></div>'
                f"<pre><code class=\"lang-{lang}\">{code}</code></pre></div>"
            )
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            level, text = len(m.group(1)), m.group(2)
            if level == 1:
                title = text
            elif level == 2:
                sid = slug(text)
                cur = []
                sections.append({"id": sid, "title": text, "body": cur, "aud": []})
                num = re.match(r"^(\d+)\.\s+(.*)$", text)
                label = (
                    f'<span class="num">{num.group(1)}</span>{inline(num.group(2))}'
                    if num
                    else inline(text)
                )
                emit(f'<h2 id="{sid}"><a class="anchor" href="#{sid}">{label}</a></h2>')
            else:
                sid = slug((sections[-1]["id"] + "-" if sections else "") + text)
                emit(f'<h{level} id="{sid}">{inline(text)}</h{level}>')
            i += 1
            continue

        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            emit(render_table(rows))
            continue

        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            text = " ".join(buf)
            cls = "callout plain" if text.startswith("**In plain words:**") else "callout"
            text = text.replace("**In plain words:**", "").strip()
            label = '<span class="callout-label">In plain words</span>' if "plain" in cls else ""
            emit(f'<aside class="{cls}">{label}<p>{inline(text)}</p></aside>')
            continue

        if re.match(r"^- \[[ x]\] ", s):
            checklist_n += 1
            items = []
            while i < len(lines) and re.match(r"^- \[[ x]\] ", lines[i].strip()):
                items.append(lines[i].strip()[6:])
                i += 1
            lis = "".join(
                f'<li><label><input type="checkbox" data-key="c{checklist_n}-{n}">'
                f"<span>{inline(t)}</span></label></li>"
                for n, t in enumerate(items)
            )
            emit(
                f'<div class="checklist" data-list="c{checklist_n}"><ul>{lis}</ul>'
                f'<div class="checklist-foot"><span class="progress-text"></span>'
                f'<button type="button" class="reset">Reset</button></div></div>'
            )
            continue

        if re.match(r"^(- |\d+\. )", s):
            ordered = bool(re.match(r"^\d+\. ", s))
            pat = r"^\d+\. " if ordered else r"^- "
            items = []
            while i < len(lines) and re.match(pat, lines[i].strip()):
                items.append(re.sub(pat, "", lines[i].strip(), count=1))
                i += 1
            tag = "ol" if ordered else "ul"
            cls = ' class="golden"' if ordered and sections and sections[-1]["id"].endswith("golden-rules") else ""
            emit(f"<{tag}{cls}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>")
            continue

        buf = []
        while i < len(lines):
            t = lines[i].strip()
            if not t or re.match(r"^(#|```|\||>|- |\d+\. |---$)", t):
                break
            buf.append(t)
            i += 1
        text = " ".join(buf)
        if text.startswith("**Audience:**") and sections:
            badge_html, keys = audience_badges(text)
            sections[-1]["aud"] = keys
            emit(badge_html)
        else:
            emit(f"<p>{inline(text)}</p>")

    return title, header_parts, sections


def build() -> None:
    title, header_parts, sections = convert(SRC.read_text(encoding="utf-8"))
    subtitle = header_parts[0] if header_parts else ""
    meta = header_parts[1] if len(header_parts) > 1 else ""

    toc = []
    body = []
    tab_sections: list[str] = []
    for sec in sections:
        aud = " ".join(sec["aud"]) or "everyone"
        num = re.match(r"^(\d+)\.\s+(.*)$", sec["title"])
        label = (
            f'<span class="toc-num">{num.group(1)}</span>{inline(num.group(2))}'
            if num
            else f'<span class="toc-num">·</span>{inline(sec["title"])}'
        )
        has_tabs = any("data-tabs" in part for part in sec["body"])
        badge = '<span class="toc-fw" aria-hidden="true"></span>' if has_tabs else ""
        if has_tabs and num:
            tab_sections.append(f'<a href="#{sec["id"]}">{num.group(1)}</a>')
        toc.append(f'<li data-aud="{aud}"><a href="#{sec["id"]}">{label}{badge}</a></li>')
        body.append(
            f'<section class="doc-section" id="sec-{sec["id"]}" data-aud="{aud}">'
            + "".join(sec["body"])
            + "</section>"
        )

    page = TEMPLATE
    for key, value in {
        "{{TITLE}}": html.escape(title),
        "{{SUBTITLE}}": subtitle,
        "{{META}}": meta,
        "{{TOC}}": "".join(toc),
        "{{BODY}}": "".join(body),
        "{{FW_SECTIONS}}": (", ".join(tab_sections[:-1]) + " and " + tab_sections[-1]) if len(tab_sections) > 1 else "".join(tab_sections),
    }.items():
        page = page.replace(key, value)
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} ({len(sections)} sections)")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flutter Engineering Standards</title>
<meta name="description" content="A practical guide to clean, fast, safe Flutter apps for every role on the team.">
<style>
:root {
  --bg: #f7f7f5;
  --surface: #ffffff;
  --surface-2: #f0f1ee;
  --ink: #1d2125;
  --ink-2: #4a5158;
  --ink-3: #6f767d;
  --line: #e2e3df;
  --accent: #1f5bd8;
  --accent-soft: #e7eefc;
  --must: #b42318;
  --must-soft: #fdecea;
  --should: #1f5bd8;
  --should-soft: #e7eefc;
  --avoid: #a15c00;
  --avoid-soft: #fdf1df;
  --plain: #0f7b5f;
  --plain-soft: #e5f4ef;
  --code-bg: #1e232a;
  --code-ink: #e6e8eb;
  --code-bar: #2a3039;
  --mark: #ffe58a;
  --shadow: 0 1px 2px rgba(20, 24, 28, .06), 0 4px 16px rgba(20, 24, 28, .05);
  --radius: 12px;
  --sidebar: 288px;
  --top: 60px;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #121416; --surface: #1a1d20; --surface-2: #22262a; --ink: #e8eaec; --ink-2: #b7bcc1;
    --ink-3: #8c939a; --line: #2d3236; --accent: #7aa5ff; --accent-soft: #1f2b44;
    --must: #ff8a80; --must-soft: #3a1f1d; --should: #7aa5ff; --should-soft: #1f2b44;
    --avoid: #f0b45a; --avoid-soft: #3a2c17; --plain: #5fd1ae; --plain-soft: #143229;
    --code-bg: #0d0f11; --code-bar: #1a1d21; --mark: #6b5a12;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 4px 16px rgba(0,0,0,.3); color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #121416; --surface: #1a1d20; --surface-2: #22262a; --ink: #e8eaec; --ink-2: #b7bcc1;
  --ink-3: #8c939a; --line: #2d3236; --accent: #7aa5ff; --accent-soft: #1f2b44;
  --must: #ff8a80; --must-soft: #3a1f1d; --should: #7aa5ff; --should-soft: #1f2b44;
  --avoid: #f0b45a; --avoid-soft: #3a2c17; --plain: #5fd1ae; --plain-soft: #143229;
  --code-bg: #0d0f11; --code-bar: #1a1d21; --mark: #6b5a12;
  --shadow: 0 1px 2px rgba(0,0,0,.4), 0 4px 16px rgba(0,0,0,.3); color-scheme: dark;
}
* { box-sizing: border-box; }
html { scroll-padding-top: calc(var(--top) + 16px); -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 16px/1.65 system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans Myanmar", sans-serif;
  overflow-x: hidden;
}
a { color: var(--accent); }
code { font-family: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace; font-size: .88em; }
:not(pre) > code { background: var(--surface-2); border: 1px solid var(--line); padding: .08em .38em; border-radius: 6px; overflow-wrap: anywhere; }

/* Top bar */
.topbar {
  position: fixed; inset: 0 0 auto 0; height: var(--top); z-index: 30;
  display: flex; align-items: center; gap: 12px; padding: 0 16px;
  background: color-mix(in srgb, var(--surface) 88%, transparent);
  backdrop-filter: saturate(1.4) blur(10px); border-bottom: 1px solid var(--line);
}
.brand { font-weight: 700; letter-spacing: -.01em; white-space: nowrap; display: flex; align-items: center; gap: 8px; }
.brand-mark { width: 26px; height: 26px; border-radius: 7px; background: var(--accent); display: grid; place-items: center; color: var(--surface); font-size: 14px; }
.search { flex: 1; max-width: 420px; margin-left: auto; position: relative; }
.search input {
  width: 100%; height: 38px; border-radius: 10px; border: 1px solid var(--line); background: var(--surface-2);
  color: var(--ink); padding: 0 12px 0 34px; font: inherit; font-size: 14px;
}
.search input:focus { outline: 2px solid var(--accent); outline-offset: 1px; background: var(--surface); }
.search svg { position: absolute; left: 10px; top: 11px; width: 16px; height: 16px; color: var(--ink-3); }
.icon-btn {
  width: 38px; height: 38px; display: grid; place-items: center; border-radius: 10px; border: 1px solid var(--line);
  background: var(--surface); color: var(--ink); cursor: pointer; flex: none;
}
.icon-btn:hover { background: var(--surface-2); }
.icon-btn svg { width: 18px; height: 18px; }
#menuBtn { display: none; }
.progress { position: absolute; left: 0; bottom: -1px; height: 2px; background: var(--accent); width: 0; }

/* Layout */
.layout { display: grid; grid-template-columns: var(--sidebar) minmax(0, 1fr); padding-top: var(--top); }
.sidebar {
  position: sticky; top: var(--top); height: calc(100vh - var(--top)); overflow-y: auto;
  padding: 20px 14px 40px; border-right: 1px solid var(--line); background: var(--bg);
}
.side-label { font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: var(--ink-3); margin: 6px 8px 10px; font-weight: 600; }
.roles { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 4px 20px; }
.role {
  border: 1px solid var(--line); background: var(--surface); color: var(--ink-2); border-radius: 999px;
  padding: 5px 11px; font: inherit; font-size: 13px; cursor: pointer;
}
.role[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: var(--surface); }
.toc { list-style: none; margin: 0; padding: 0; }
.toc li a {
  display: flex; gap: 10px; align-items: baseline; padding: 6px 10px; border-radius: 8px;
  color: var(--ink-2); text-decoration: none; font-size: 14px; line-height: 1.4;
}
.toc li a:hover { background: var(--surface-2); color: var(--ink); }
.toc li a.active { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
.toc li.dim a { opacity: .38; }
.toc-num { font-variant-numeric: tabular-nums; color: var(--ink-3); min-width: 1.4em; font-size: 12px; }
.toc li a.active .toc-num { color: var(--accent); }

main { min-width: 0; padding: 32px 40px 96px; }
.content { max-width: 860px; margin: 0 auto; }

/* Hero */
.hero { padding: 28px 0 24px; border-bottom: 1px solid var(--line); margin-bottom: 28px; }
.hero h1 { font-size: clamp(30px, 5vw, 44px); line-height: 1.1; letter-spacing: -.025em; margin: 0 0 14px; }
.hero .lead p { font-size: clamp(17px, 2.2vw, 20px); color: var(--ink-2); margin: 0 0 14px; max-width: 46ch; }
.hero .meta p { font-size: 13px; color: var(--ink-3); margin: 0; }
.legend { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; font-size: 13px; color: var(--ink-3); align-items: center; }

/* Sections */
.doc-section {
  background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 28px 32px; margin: 0 0 20px; box-shadow: var(--shadow); transition: opacity .2s;
}
.doc-section.dim { opacity: .35; }
.doc-section.dim:hover { opacity: .8; }
.doc-section.hidden { display: none; }
h2 { font-size: clamp(22px, 3vw, 27px); letter-spacing: -.015em; line-height: 1.25; margin: 0 0 10px; }
h2 .anchor { color: inherit; text-decoration: none; display: flex; gap: 12px; align-items: baseline; }
h2 .num {
  font-size: .62em; font-weight: 700; color: var(--accent); background: var(--accent-soft);
  border-radius: 8px; padding: 2px 9px; font-variant-numeric: tabular-nums; flex: none;
}
h3 { font-size: 18px; margin: 28px 0 8px; letter-spacing: -.01em; }
h4 { font-size: 16px; margin: 20px 0 6px; }
p, li { color: var(--ink); }
ul, ol { padding-left: 1.3em; }
li { margin: 5px 0; }
li::marker { color: var(--ink-3); }

.audience { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin: 0 0 18px; }
.audience-label { font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: var(--ink-3); margin-right: 4px; font-weight: 600; }
.badge { font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 999px; background: var(--surface-2); color: var(--ink-2); border: 1px solid var(--line); }
.badge-everyone { background: var(--plain-soft); color: var(--plain); border-color: transparent; }
.badge-beginner { background: var(--avoid-soft); color: var(--avoid); border-color: transparent; }
.badge-junior { background: var(--should-soft); color: var(--should); border-color: transparent; }
.badge-senior { background: var(--must-soft); color: var(--must); border-color: transparent; }
.badge-note { font-size: 12px; color: var(--ink-3); }

.rule { font-size: .74em; font-weight: 800; letter-spacing: .04em; padding: 2px 7px; border-radius: 6px; vertical-align: .1em; white-space: nowrap; }
.rule-must, .rule-must-not { background: var(--must-soft); color: var(--must); }
.rule-should { background: var(--should-soft); color: var(--should); }
.rule-avoid { background: var(--avoid-soft); color: var(--avoid); }

.callout { border-radius: 10px; padding: 16px 18px; margin: 18px 0; background: var(--surface-2); border-left: 4px solid var(--line); }
.callout p { margin: 0; }
.callout.plain { background: var(--plain-soft); border-left-color: var(--plain); }
.callout-label { display: block; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--plain); margin-bottom: 6px; }

ol.golden { list-style: none; padding: 0; counter-reset: g; display: grid; gap: 10px; }
ol.golden li { counter-increment: g; position: relative; padding: 12px 14px 12px 54px; background: var(--surface-2); border-radius: 10px; margin: 0; }
ol.golden li::before {
  content: counter(g); position: absolute; left: 14px; top: 12px; width: 28px; height: 28px; border-radius: 50%;
  background: var(--accent); color: var(--surface); display: grid; place-items: center; font-weight: 700; font-size: 14px;
}

.table-wrap { overflow-x: auto; margin: 16px 0; border: 1px solid var(--line); border-radius: 10px; -webkit-overflow-scrolling: touch; }
table { border-collapse: collapse; width: 100%; font-size: 14.5px; }
th, td { text-align: left; padding: 10px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { background: var(--surface-2); font-weight: 600; color: var(--ink-2); font-size: 13px; white-space: nowrap; }
tr:last-child td { border-bottom: 0; }
td { min-width: 110px; }
td:first-child { min-width: 0; }

.code { margin: 16px 0; border-radius: 10px; overflow: hidden; background: var(--code-bg); }
.code-bar { display: flex; justify-content: space-between; align-items: center; padding: 6px 10px 6px 14px; background: var(--code-bar); color: #9aa3ad; font-size: 12px; font-family: ui-monospace, Menlo, monospace; }
.copy { background: transparent; color: #c5ccd3; border: 1px solid #3a424c; border-radius: 6px; padding: 3px 10px; font: inherit; cursor: pointer; }
.copy:hover { background: #343b45; }
pre { margin: 0; padding: 14px 16px; overflow-x: auto; color: var(--code-ink); font-size: 13.5px; line-height: 1.55; -webkit-overflow-scrolling: touch; }
pre code { font-size: inherit; }
.tok-k { color: #ff9eb6; } .tok-s { color: #a5d6a7; } .tok-c { color: #7f8b97; font-style: italic; } .tok-t { color: #8ec5ff; } .tok-a { color: #ffcc80; }

.tabs { margin: 16px 0; border-radius: 10px; }
.tabs.flash { animation: fwflash 1.1s ease-out; }
@keyframes fwflash { from { box-shadow: 0 0 0 4px var(--accent); } to { box-shadow: 0 0 0 0 transparent; } }
.fw-note { font-size: 12.5px; line-height: 1.5; color: var(--ink-3); margin: -10px 8px 22px; }
.fw-note strong { color: var(--accent); }
.fw-note a { font-weight: 600; }
.toc-fw {
  margin-left: auto; font-size: 11px; font-weight: 600; padding: 1px 8px; border-radius: 999px;
  background: var(--accent-soft); color: var(--accent); white-space: nowrap; align-self: center;
}
th.fw-col { color: var(--accent); background: var(--accent-soft); }
td.fw-col { background: color-mix(in srgb, var(--accent-soft) 55%, transparent); }
.tab-list { display: flex; gap: 4px; overflow-x: auto; border-bottom: 1px solid var(--line); -webkit-overflow-scrolling: touch; }
.tab {
  border: 0; background: none; color: var(--ink-2); font: inherit; font-size: 14px; font-weight: 600;
  padding: 9px 14px; border-bottom: 2px solid transparent; margin-bottom: -1px; cursor: pointer; white-space: nowrap;
}
.tab:hover { color: var(--ink); }
.tab[aria-selected="true"] { color: var(--accent); border-bottom-color: var(--accent); }
.tab:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; border-radius: 6px 6px 0 0; }
.tab-panel .code { margin-top: 10px; }
.checklist { border: 1px solid var(--line); border-radius: 10px; margin: 12px 0 20px; overflow: hidden; }
.checklist ul { list-style: none; margin: 0; padding: 6px; }
.checklist li { margin: 0; }
.checklist label { display: flex; gap: 12px; align-items: flex-start; padding: 9px 10px; border-radius: 8px; cursor: pointer; }
.checklist label:hover { background: var(--surface-2); }
.checklist input { width: 18px; height: 18px; margin-top: 3px; accent-color: var(--accent); flex: none; }
.checklist input:checked + span { color: var(--ink-3); text-decoration: line-through; }
.checklist-foot { display: flex; justify-content: space-between; align-items: center; padding: 8px 16px; background: var(--surface-2); border-top: 1px solid var(--line); font-size: 13px; color: var(--ink-3); }
.reset { background: none; border: 0; color: var(--accent); font: inherit; cursor: pointer; padding: 4px; }

mark { background: var(--mark); color: inherit; border-radius: 3px; padding: 0 1px; }
.empty { display: none; text-align: center; color: var(--ink-3); padding: 48px 16px; }
.empty.show { display: block; }
.to-top {
  position: fixed; right: 18px; bottom: 18px; z-index: 25; opacity: 0; pointer-events: none; transition: opacity .2s;
  box-shadow: var(--shadow);
}
.to-top.show { opacity: 1; pointer-events: auto; }
.scrim { display: none; }
footer { text-align: center; color: var(--ink-3); font-size: 13px; padding: 20px 0 0; }

@media (max-width: 1000px) {
  :root { --sidebar: 0px; }
  .layout { grid-template-columns: minmax(0, 1fr); }
  #menuBtn { display: grid; }
  .sidebar {
    position: fixed; top: var(--top); left: 0; bottom: 0; width: min(86vw, 320px); height: auto; z-index: 40;
    transform: translateX(-100%); transition: transform .25s ease; background: var(--surface); box-shadow: var(--shadow);
  }
  body.nav-open .sidebar { transform: none; }
  body.nav-open .scrim { display: block; position: fixed; inset: var(--top) 0 0 0; background: rgba(0,0,0,.35); z-index: 35; }
  main { padding: 20px 16px 80px; }
}
@media (max-width: 600px) {
  .brand-text { display: none; }
  .doc-section { padding: 20px 16px; border-radius: 10px; }
  .hero { padding-top: 12px; }
  table { font-size: 13.5px; }
  th, td { padding: 8px 10px; }
  td, td:first-child { min-width: 112px; }
  pre { font-size: 12.5px; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; scroll-behavior: auto !important; } }
@media print {
  .topbar, .sidebar, .to-top, .copy, .reset, .tab-list { display: none !important; }
  .tab-panel[hidden] { display: block !important; }
  .tab-panel::before { content: attr(data-label); display: block; font-weight: 700; margin-top: 12px; }
  .layout { display: block; padding: 0; }
  main { padding: 0; }
  .doc-section { box-shadow: none; break-inside: auto; opacity: 1 !important; display: block !important; }
  pre { white-space: pre-wrap; }
}
</style>
</head>
<body>
<header class="topbar">
  <button class="icon-btn" id="menuBtn" type="button" aria-label="Open contents" aria-expanded="false">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
  </button>
  <div class="brand"><span class="brand-mark" aria-hidden="true">F</span><span class="brand-text">Flutter Standards</span></div>
  <label class="search">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
    <input id="search" type="search" placeholder="Search rules, e.g. dispose, token, const" aria-label="Search the guide" autocomplete="off">
  </label>
  <button class="icon-btn" id="themeBtn" type="button" aria-label="Toggle dark mode">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
  </button>
  <div class="progress" id="progress"></div>
</header>
<div class="scrim" id="scrim"></div>
<div class="layout">
  <nav class="sidebar" id="sidebar" aria-label="Contents">
    <div class="side-label">I am</div>
    <div class="roles" role="group" aria-label="Highlight sections for a role">
      <button class="role" type="button" data-role="all" aria-pressed="true">Anyone</button>
      <button class="role" type="button" data-role="non-technical" aria-pressed="false">Non-technical</button>
      <button class="role" type="button" data-role="beginner" aria-pressed="false">Beginner</button>
      <button class="role" type="button" data-role="junior" aria-pressed="false">Junior</button>
      <button class="role" type="button" data-role="senior" aria-pressed="false">Senior</button>
    </div>
    <div class="side-label">Code examples in</div>
    <div class="roles" role="group" aria-label="Show code examples for">
      <button class="role fw" type="button" data-fw="getx" aria-pressed="true">GetX</button>
      <button class="role fw" type="button" data-fw="provider" aria-pressed="false">Provider</button>
      <button class="role fw" type="button" data-fw="riverpod" aria-pressed="false">Riverpod</button>
      <button class="role fw" type="button" data-fw="bloc" aria-pressed="false">Bloc</button>
    </div>
    <p class="fw-note" aria-live="polite">Code in sections {{FW_SECTIONS}} is shown in <strong id="fwName">GetX</strong>. All other sections apply to every approach.</p>
    <div class="side-label">Contents</div>
    <ol class="toc" id="toc">{{TOC}}</ol>
  </nav>
  <main>
    <div class="content">
      <div class="hero">
        <h1>{{TITLE}}</h1>
        <div class="lead">{{SUBTITLE}}</div>
        <div class="meta">{{META}}</div>
        <div class="legend">Rule words:
          <span class="rule rule-must">MUST</span>
          <span class="rule rule-should">SHOULD</span>
          <span class="rule rule-avoid">AVOID</span>
        </div>
      </div>
      <div id="sections">{{BODY}}</div>
      <p class="empty" id="empty">No section matches your search.</p>
      <footer>Generated from flutter-engineering-standards.md. Edit the Markdown, then run build_html.py.</footer>
    </div>
  </main>
</div>
<button class="icon-btn to-top" id="toTop" type="button" aria-label="Back to top">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
</button>
<script>
(function () {
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
    del(k) { try { localStorage.removeItem(k); } catch (e) {} },
  };
  const root = document.documentElement;
  const NS = 'flutter-standards:';

  // Theme
  const saved = store.get(NS + 'theme');
  if (saved) root.dataset.theme = saved;
  document.getElementById('themeBtn').addEventListener('click', () => {
    const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    store.set(NS + 'theme', root.dataset.theme);
  });

  // Mobile nav
  const body = document.body, menuBtn = document.getElementById('menuBtn');
  const setNav = (open) => { body.classList.toggle('nav-open', open); menuBtn.setAttribute('aria-expanded', String(open)); };
  menuBtn.addEventListener('click', () => setNav(!body.classList.contains('nav-open')));
  document.getElementById('scrim').addEventListener('click', () => setNav(false));
  document.querySelectorAll('.toc a').forEach(a => a.addEventListener('click', () => setNav(false)));
  addEventListener('keydown', e => { if (e.key === 'Escape') setNav(false); });

  // Role filter
  const sections = [...document.querySelectorAll('.doc-section')];
  const tocItems = [...document.querySelectorAll('.toc li')];
  const matches = (aud, role) => {
    if (role === 'all') return true;
    const a = aud.split(' ');
    if (a.includes('everyone')) return true;
    if (role === 'non-technical') return a.includes('non-technical');
    return a.includes(role);
  };
  const applyRole = (role) => {
    document.querySelectorAll('.role[data-role]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.role === role)));
    sections.forEach(s => s.classList.toggle('dim', !matches(s.dataset.aud, role)));
    tocItems.forEach(li => li.classList.toggle('dim', !matches(li.dataset.aud, role)));
    store.set(NS + 'role', role);
  };
  document.querySelectorAll('.role[data-role]').forEach(b => b.addEventListener('click', () => applyRole(b.dataset.role)));
  applyRole(store.get(NS + 'role') || 'all');

  // Framework tabs: one choice switches every example on the page
  const FW_LABEL = { getx: 'GetX', provider: 'Provider', riverpod: 'Riverpod', bloc: 'Bloc' };
  const fwTables = [...document.querySelectorAll('table')].filter(tb => {
    const h = tb.querySelector('thead') ? tb.querySelector('thead').textContent.toLowerCase() : '';
    return h.includes('getx') && h.includes('riverpod');
  });
  const applyFw = (fw, flash) => {
    const name = FW_LABEL[fw] || fw;
    const label = document.getElementById('fwName');
    if (label) label.textContent = name;
    document.querySelectorAll('.toc-fw').forEach(b => (b.textContent = name));
    fwTables.forEach(tb => {
      const col = [...tb.querySelectorAll('thead th')].findIndex(th => th.textContent.toLowerCase().includes(fw));
      tb.querySelectorAll('tr').forEach(tr => [...tr.children].forEach((c, n) => c.classList.toggle('fw-col', n === col)));
    });
    if (flash && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.querySelectorAll('[data-tabs]').forEach(g => {
        g.classList.remove('flash'); void g.offsetWidth; g.classList.add('flash');
      });
    }
    document.querySelectorAll('[data-tabs]').forEach(group => {
      const tabs = [...group.querySelectorAll('.tab')];
      const pick = tabs.find(t => t.dataset.fw.split(' ').includes(fw)) || tabs[0];
      tabs.forEach(t => {
        const on = t === pick;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
      });
    });
    document.querySelectorAll('.fw').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.fw === fw)));
    store.set(NS + 'fw', fw);
  };
  let currentFw = store.get(NS + 'fw') || 'getx';
  document.querySelectorAll('.fw').forEach(b => b.addEventListener('click', () => applyFw(currentFw = b.dataset.fw, true)));
  document.querySelectorAll('[data-tabs]').forEach(group => {
    const tabs = [...group.querySelectorAll('.tab')];
    tabs.forEach((t, n) => {
      t.addEventListener('click', () => {
        const keys = t.dataset.fw.split(' ');
        if (!keys.includes(currentFw)) currentFw = keys[0];
        applyFw(currentFw);
      });
      t.addEventListener('keydown', e => {
        const step = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!step) return;
        const next = tabs[(n + step + tabs.length) % tabs.length];
        next.click();
        next.focus();
      });
    });
  });
  applyFw(currentFw);

  // Light syntax colouring for Dart / YAML / bash
  const KW = /\b(abstract|interface|final|class|sealed|extends|implements|const|return|async|await|try|on|catch|throw|switch|case|if|else|for|in|new|void|static|factory|required|late|import|enum|override|super|this|true|false|null|Future|String|int|double|bool|List|Map|dynamic)\b/g;
  document.querySelectorAll('pre code').forEach(code => {
    const lang = code.className.replace('lang-', '');
    if (!['dart', 'yaml', 'bash'].includes(lang)) return;
    const src = code.textContent;
    const out = [];
    const re = lang === 'dart'
      ? /(\/\/[^\n]*)|('(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*")|(@\w+)|(\b[A-Z][A-Za-z0-9_]*\b)/g
      : /(#[^\n]*)|('(?:[^'\n])*'|"(?:[^"\n])*")|((?<![\w])--?[\w-]+)|(\b(?:flutter|dart|include|analyzer|linter|rules|errors|exclude|language)\b)/g;
    let last = 0, m;
    const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const plain = s => lang === 'dart' ? esc(s).replace(KW, '<span class="tok-k">$1</span>') : esc(s);
    while ((m = re.exec(src))) {
      out.push(plain(src.slice(last, m.index)));
      const cls = m[1] ? 'tok-c' : m[2] ? 'tok-s' : m[3] ? 'tok-a' : 'tok-t';
      out.push('<span class="' + cls + '">' + esc(m[0]) + '</span>');
      last = re.lastIndex;
    }
    out.push(plain(src.slice(last)));
    code.innerHTML = out.join('');
  });

  // Copy buttons
  document.querySelectorAll('.copy').forEach(btn => btn.addEventListener('click', async () => {
    const text = btn.closest('.code').querySelector('pre').innerText;
    try { await navigator.clipboard.writeText(text); btn.textContent = 'Copied'; }
    catch (e) { btn.textContent = 'Select & copy'; }
    setTimeout(() => (btn.textContent = 'Copy'), 1500);
  }));

  // Checklists with saved progress
  document.querySelectorAll('.checklist').forEach(list => {
    const boxes = [...list.querySelectorAll('input')];
    const label = list.querySelector('.progress-text');
    const update = () => { label.textContent = boxes.filter(b => b.checked).length + ' of ' + boxes.length + ' done'; };
    boxes.forEach(b => {
      b.checked = store.get(NS + b.dataset.key) === '1';
      b.addEventListener('change', () => { b.checked ? store.set(NS + b.dataset.key, '1') : store.del(NS + b.dataset.key); update(); });
    });
    list.querySelector('.reset').addEventListener('click', () => { boxes.forEach(b => { b.checked = false; store.del(NS + b.dataset.key); }); update(); });
    update();
  });

  // Search with highlight
  const input = document.getElementById('search'), empty = document.getElementById('empty');
  let timer;
  // Only text nodes are touched, so checkbox and button listeners survive.
  const clearMarks = () => document.querySelectorAll('#sections mark').forEach(m => {
    const parent = m.parentNode;
    m.replaceWith(document.createTextNode(m.textContent));
    parent.normalize();
  });
  const mark = (node, q) => {
    const needle = q.toLowerCase();
    const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, {
      acceptNode: n => n.parentElement.closest('pre, button, mark') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT,
    });
    const hits = [];
    while (walker.nextNode()) if (walker.currentNode.nodeValue.toLowerCase().includes(needle)) hits.push(walker.currentNode);
    hits.forEach(t => {
      const text = t.nodeValue, lower = text.toLowerCase(), frag = document.createDocumentFragment();
      let from = 0, at;
      while ((at = lower.indexOf(needle, from)) !== -1) {
        frag.append(text.slice(from, at));
        const m = document.createElement('mark');
        m.textContent = text.slice(at, at + needle.length);
        frag.append(m);
        from = at + needle.length;
      }
      frag.append(text.slice(from));
      t.replaceWith(frag);
    });
  };
  input.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      const q = input.value.trim();
      clearMarks();
      if (!q) { sections.forEach(s => s.classList.remove('hidden')); empty.classList.remove('show'); return; }
      let shown = 0;
      sections.forEach(s => {
        const hit = s.textContent.toLowerCase().includes(q.toLowerCase());
        s.classList.toggle('hidden', !hit);
        if (hit) { shown++; mark(s, q); }
      });
      empty.classList.toggle('show', shown === 0);
    }, 160);
  });

  // Active TOC + progress + back-to-top
  const links = new Map([...document.querySelectorAll('.toc a')].map(a => [a.getAttribute('href').slice(1), a]));
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const id = e.target.querySelector('h2')?.id;
      links.forEach(a => a.classList.remove('active'));
      const a = links.get(id);
      if (a) { a.classList.add('active'); a.scrollIntoView({ block: 'nearest' }); }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  sections.forEach(s => obs.observe(s));
  const progress = document.getElementById('progress'), toTop = document.getElementById('toTop');
  const onScroll = () => {
    const h = document.documentElement.scrollHeight - innerHeight;
    progress.style.width = (h > 0 ? (scrollY / h) * 100 : 0) + '%';
    toTop.classList.toggle('show', scrollY > 800);
  };
  addEventListener('scroll', onScroll, { passive: true });
  toTop.addEventListener('click', () => scrollTo({ top: 0, behavior: 'smooth' }));
  onScroll();
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
