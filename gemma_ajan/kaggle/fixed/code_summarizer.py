"""Kodla yapılan konuşma sıkıştırması (ADK BaseEventsSummarizer uygulaması).

ADK'nın varsayılanı modelin kendisine özet yazdırır: özet kayıplı ve doğrulanamaz. Burada
özet koddan çıkar: her olay için çağrı adı, kısaltılmış argüman, sonucun başı ve uzunluğu.
Tahmin yok, model çağrısı yok, aynı girdi her zaman aynı özeti verir.

Girdi token'ı sayılır (ceil(karakter/3)); özet MAX_SUMMARY_TOKENS'ı aşmaz.
"""
import json
import math

from google.adk.apps.base_events_summarizer import BaseEventsSummarizer
from google.adk.events import Event
from google.adk.events.event_actions import EventActions
from google.adk.events.event_actions import EventCompaction  # noqa: F401  (sürüm farkı için)
from google.genai import types

MAX_SUMMARY_TOKENS = 1200
RESULT_HEAD_CHARS = 240
ARG_CHARS = 160


def _tok(s):
    return math.ceil(len(s) / 3)


def _short(v, n):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)
    return s if len(s) <= n else s[:n] + f"…(+{len(s) - n})"


def digest_line(ev):
    """Tek bir olayı tek satıra indirger. Çağrı, sonuç, metin ayrı ayrı."""
    out = []
    if not ev.content or not ev.content.parts:
        return out
    for p in ev.content.parts:
        fc = getattr(p, "function_call", None)
        fr = getattr(p, "function_response", None)
        if fc:
            out.append(f"CALL {fc.name} {_short(dict(fc.args or {}), ARG_CHARS)}")
        elif fr:
            resp = fr.response or {}
            body = resp.get("stdout") or resp.get("content") or resp.get("error") or resp.get("raw") or json.dumps(resp, ensure_ascii=False, default=str)
            body = str(body).replace("\n", " | ")
            out.append(f"RESULT {fr.name} ({len(str(body))} chars): {_short(body, RESULT_HEAD_CHARS)}")
        elif getattr(p, "text", None):
            txt = p.text.replace("\n", " ").strip()
            if txt:
                out.append(f"{ev.author} TEXT: {_short(txt, RESULT_HEAD_CHARS)}")
    return out


def build_digest(events):
    lines = []
    for ev in events:
        lines.extend(digest_line(ev))
    head = f"[KOD ÖZETİ: {len(events)} olay sıkıştırıldı; ayrıntı yok, yalnız bu satırlar]"
    text = head + "\n" + "\n".join(lines)
    limit = MAX_SUMMARY_TOKENS * 3
    if len(text) > limit:
        keep = limit - len(head) - 60
        text = head + "\n" + text[len(head) + 1:len(head) + 1 + keep] + "\n...[özet kırpıldı]"
    return text


class CodeEventsSummarizer(BaseEventsSummarizer):
    """Olay listesini koddan özetleyen sıkıştırıcı."""

    async def maybe_summarize_events(self, *, events):
        if not events:
            return None
        content = types.Content(role="model", parts=[types.Part(text=build_digest(events))])
        compaction = EventCompaction(
            start_timestamp=events[0].timestamp,
            end_timestamp=events[-1].timestamp,
            compacted_content=content,
        )
        return Event(author="user", actions=EventActions(compaction=compaction), invocation_id=Event.new_id())
