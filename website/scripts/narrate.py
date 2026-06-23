#!/usr/bin/env python3
"""Render per-stage narration MP3s with edge-tts (free Microsoft neural voices).

Reads the canonical spoken script from ``src/data/narration.json`` (id -> text)
and writes ``public/anim/<id>.mp3`` — one clip per stage, dropped next to the
Manim ``.mp4``s so GitHub Pages serves them as plain static assets. The browser
never calls a TTS service; we pre-render here, exactly like the video clips.

    pip install edge-tts
    python scripts/narrate.py                       # render every stage
    python scripts/narrate.py ctc wfst              # render only these ids
    python scripts/narrate.py --voice en-US-EmmaMultilingualNeural
    python scripts/narrate.py --rate +0%            # default pace

Browse the voices with:  edge-tts --list-voices | grep en-
Good natural US female options: AvaMultilingual (default), Emma, Jenny, Aria.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

try:
    import edge_tts
except ModuleNotFoundError:
    sys.exit("edge-tts is not installed. Run:  pip install edge-tts")

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "src" / "data" / "narration.json"
OUT = ROOT / "public" / "anim"

DEFAULT_VOICE = "en-US-AvaMultilingualNeural"
DEFAULT_RATE = "+10%"  # a little brisker than default — the site can speed it further
DEFAULT_PITCH = "+0Hz"

_SENT_END = re.compile(r"[.!?]")


def _norm(s: str) -> str:
    """Lowercased, alphanumerics only — for matching display words to spoken ones."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def build_cues(text: str, timings: list[dict]) -> list[dict]:
    """Pair the punctuated source words with the voice's per-word timings and
    group them into sentence cues — so the subtitles can show one grammatical
    sentence at a time, with punctuation, the spoken word lit in step.

    The voice emits one timing per spoken token (no punctuation); the source has
    the same words *with* punctuation. We walk both, consuming timing tokens
    until they cover each display word, so splits/joins stay aligned.
    """
    display = text.split()
    wi, n, last_t = 0, len(timings), 0.0
    timed: list[dict] = []
    for tok in display:
        target = _norm(tok)
        if not target:  # pure punctuation — inherit the last time
            timed.append({"w": tok, "t": round(last_t, 3)})
            continue
        start_t, acc = None, ""
        while wi < n:
            if start_t is None:
                start_t = timings[wi]["t"]
            acc += _norm(timings[wi]["text"])
            wi += 1
            if len(acc) >= len(target):
                break
        last_t = start_t if start_t is not None else last_t
        timed.append({"w": tok, "t": round(last_t, 3)})

    cues, cur = [], []
    for item in timed:
        cur.append(item)
        if _SENT_END.search(item["w"]):
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)

    out = [{"t": c[0]["t"], "words": c} for c in cues]
    for i, cue in enumerate(out):
        cue["end"] = out[i + 1]["t"] if i + 1 < len(out) else None
    return out


async def render(stage_id: str, text: str, voice: str, rate: str, pitch: str) -> None:
    """Write <id>.mp3 and a <id>.captions.json track of sentence cues.

    We stream rather than ``save()`` so we can capture the WordBoundary events
    the voice emits — each gives a word and its start offset (in 100-nanosecond
    units). Those are folded into punctuated sentence cues the site shows one at
    a time, with the spoken word lit in step.
    """
    dest = OUT / f"{stage_id}.mp3"
    caps_dest = OUT / f"{stage_id}.captions.json"
    # boundary="WordBoundary" is required — the default is SentenceBoundary, which
    # gives no per-word timings to drive the subtitle highlight.
    comm = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    timings: list[dict] = []
    with open(dest, "wb") as audio_file:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                timings.append({"t": round(chunk["offset"] / 1e7, 3), "text": chunk["text"]})

    cues = build_cues(text, timings)
    caps_dest.write_text(json.dumps({"cues": cues}, ensure_ascii=False), encoding="utf-8")
    print(f"  ✓ {dest.relative_to(ROOT)}  ({len(text)} chars, {len(cues)} cues)")


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="stage ids to render (default: all in narration.json)")
    ap.add_argument("--voice", default=DEFAULT_VOICE, help=f"edge-tts voice (default: {DEFAULT_VOICE})")
    ap.add_argument("--rate", default=DEFAULT_RATE, help=f"speech rate, e.g. -4%% (default: {DEFAULT_RATE})")
    ap.add_argument("--pitch", default=DEFAULT_PITCH, help=f"pitch, e.g. +0Hz (default: {DEFAULT_PITCH})")
    args = ap.parse_args()

    script: dict[str, str] = json.loads(SCRIPT.read_text(encoding="utf-8"))
    ids = args.ids or list(script.keys())
    unknown = [i for i in ids if i not in script]
    if unknown:
        sys.exit(f"unknown stage id(s): {', '.join(unknown)}\nknown: {', '.join(script)}")

    OUT.mkdir(parents=True, exist_ok=True)
    print(f"voice: {args.voice}   rate: {args.rate}   pitch: {args.pitch}")
    for stage_id in ids:
        await render(stage_id, script[stage_id], args.voice, args.rate, args.pitch)
    print(f"done — {len(ids)} clip(s) → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())
