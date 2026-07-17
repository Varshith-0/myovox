#!/usr/bin/env python3
r"""Generate the Technical page's markdown from myovox.tex.

    python scripts/tex2md.py        # from website/

The report's glossary is a link graph: \glref{label}{text} in the body jumps to
\glentry{label}{term}. Markdown has no such macro, so every jump target becomes a
heading whose slug the page derives from its own text, and every reference becomes
a normal markdown link to that slug. The two must agree exactly, which is why the
slug function here mirrors TechnicalPage.tsx character for character.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # website/
TEX = ROOT.parent / "myovox.tex"                       # the report source of truth
OUT = ROOT / "src" / "content" / "technical_report.md"

# unsrtnat numbers references in order of first citation.
CITE_ORDER = [
    "gowda2026emg2speech", "gaddy2020digital", "gaddy2021improved", "gaddy2022thesis",
    "benster2024mona", "mohapatra2025llms", "levy2025brain2qwerty", "zhang2026brain2qwerty2",
    "panayotov2015librispeech", "gowda2024geometry", "gowda2025geometric", "hannun2019tds",
    "graves2006ctc", "hsu2021hubert", "k2icefall", "gulati2020conformer", "chen2022wavlm",
    "oord2018cpc", "qwen2025", "dettmers2023qlora", "hu2022lora", "li2024dcond",
]
CITE_NUM = {k: i + 1 for i, k in enumerate(CITE_ORDER)}


def slugify(s: str) -> str:
    """Mirror of slugify() in TechnicalPage.tsx (applied to heading text content)."""
    s = s.lower()
    s = re.sub(r"[^0-9a-z_]+", "-", s)
    return s.strip("-")


def strip_md(s: str) -> str:
    """Heading text as the DOM will see it: markdown emphasis and links flattened."""
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = s.replace("**", "").replace("*", "").replace("`", "")
    return s


def caption_head(num: int, lead: str) -> str:
    """A table's caption heading: 'Table 3. The emg2speech General Corpus.'"""
    return f"Table {num}. {lead}."


def linkify_cites(md: str) -> str:
    """Point bare [n] citations in a hand-written table at the bibliography.

    Only a bracketed integer is a citation; the confidence intervals in Table 6
    ([-9.40, -5.90]) are not, and do not match.
    """
    return re.sub(r"\[(\d{1,2})\]", lambda m: f"[[{m.group(1)}](#ref-{m.group(1)})]", md)


# ---------------------------------------------------------------- inline macros

# TeX's ~ is a non-breaking space and is stripped late in inline(); a tilde that
# means "approximately" has to survive that pass, so it rides as a sentinel.
TILDE = ""

MATH = {
    r"$(S+I+D)/N$": "(S + I + D) / N",
    r"$(\text{blank},\text{scale})$": "(blank, scale)",
    r"$(2.0, 1.0)$": "(2.0, 1.0)",
    r"$P(\text{phone}\mid\text{unit})$": "P(phone | unit)",
    r"$\mathrm{vec}(E)$": "vec(E)",
    r"$H \circ L \circ G$": "H ∘ L ∘ G",
    r"$\glref{hlg}{\mathrm{HLG}} = H \circ L \circ G$": r"\glref{hlg}{HLG} = H ∘ L ∘ G",
    r"$\text{kernel}-1$": "kernel − 1",
    r"$39.02 \rightarrow 22.34$": "39.02 → 22.34",
    r"$\approx 0.92$": "≈ 0.92",
    r"$\tau=0.1$": "τ = 0.1",
    r"$[-6.22,\,-3.29]$": "[−6.22, −3.29]",
    r"$[-9.40,\,-5.90]$": "[−9.40, −5.90]",
    r"$=1.000$": "= 1.000",
    r"$-0.04$": "−0.04",
    r"$-4.7$": "−4.7",
    r"$-7.6$": "−7.6",
    r"$\rightarrow$": "→",
    r"$\downarrow$": "↓",
    r"$\Delta$": "Δ",
    r"$\sim$": TILDE,
    r"$\tau$": "τ",
    r"$L_2$": "L2",
    r"$n$": "*n*",
    r"$G$": "*G*",
    r"$H$": "*H*",
    r"$L$": "*L*",
    r"$^{\ast}$": "\\*",
    r"$^{\dagger}$": "†",
}
# The baseline loss appears inline in prose. Callers normalize whitespace before
# calling inline(), so this key must be written with the newline already collapsed.
MATH[
    "$0.8\\cdot\\mathrm{CTC}_{\\text{unit}} + 0.1\\cdot\\mathrm{CTC}_{\\text{phone}} + "
    "0.1\\cdot\\text{consistency}$"
] = "`0.8 · CTC_unit + 0.1 · CTC_phone + 0.1 · consistency`"


def braces(s: str, start: int):
    """Return (content, index-after) for a balanced {...} beginning at s[start]=='{'."""
    assert s[start] == "{", s[start:start + 40]
    depth, i = 0, start
    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1:i], i + 1
        i += 1
    raise ValueError("unbalanced brace")


def take_macro(s: str, name: str, nargs: int):
    """Yield (full_match_span, [args]) for each \\name{..}{..} in s, innermost-safe."""
    out = []
    for m in re.finditer(r"\\" + name + r"(?![a-zA-Z])", s):
        i = m.end()
        args = []
        try:
            for _ in range(nargs):
                while i < len(s) and s[i] == " ":
                    i += 1
                if i >= len(s) or s[i] != "{":
                    raise ValueError
                a, i = braces(s, i)
                args.append(a)
        except ValueError:
            continue
        out.append(((m.start(), i), args))
    return out


def sub_macro(s: str, name: str, nargs: int, fn):
    """Replace every \\name{...} with fn(args), right-to-left so spans stay valid."""
    for (a, b), args in reversed(take_macro(s, name, nargs)):
        s = s[:a] + fn(args) + s[b:]
    return s


class Converter:
    def __init__(self, gl_slug, sec_ref, faq_ref, tab_ref):
        self.gl_slug = gl_slug      # glossary label -> slug
        self.sec_ref = sec_ref      # sec label -> (number, slug)
        self.faq_ref = faq_ref      # faq label -> (Qn, slug)
        self.tab_ref = tab_ref      # tab label -> number
        self.plain = False          # inside a heading: emit link text only

    def inline(self, s: str) -> str:
        # Math first: it contains braces and backslashes the macro pass would eat.
        for k, v in sorted(MATH.items(), key=lambda kv: -len(kv[0])):
            s = s.replace(k, v)

        s = sub_macro(s, "glref", 2, lambda a: self.glref(a[0], a[1]))
        for macro, label in (("wer", "WER"), ("per", "PER"), ("cer", "CER")):
            s = re.sub(r"\\" + macro + r"\{\}", lambda _m, mc=macro, lb=label: self.glref(mc, lb), s)
            s = re.sub(r"\\" + macro + r"(?![a-zA-Z])", lambda _m, mc=macro, lb=label: self.glref(mc, lb), s)

        s = sub_macro(s, "href", 2, lambda a: f"[{self.inline(a[1])}]({a[0]})")
        s = sub_macro(s, "textnormal", 1, lambda a: self.inline(a[0]))
        s = sub_macro(s, "textbf", 1, lambda a: f"**{self.inline(a[0])}**")
        s = sub_macro(s, "emph", 1, lambda a: f"*{self.inline(a[0])}*")
        s = sub_macro(s, "texttt", 1, lambda a: f"`{self.inline(a[0])}`")
        s = sub_macro(s, "text", 1, lambda a: self.inline(a[0]))
        s = sub_macro(s, "mathcal", 1, lambda a: a[0])
        s = sub_macro(s, "mathrm", 1, lambda a: a[0])

        s = sub_macro(s, "citep", 1, lambda a: self.cite(a[0]))
        s = sub_macro(s, "citet", 1, lambda a: self.cite(a[0]))

        # Section~\ref / Table~\ref / bare \ref{faq:..}
        s = re.sub(r"Sections~\\ref\{([^}]*)\} and~\\ref\{([^}]*)\}",
                   lambda m: f"Sections {self.secref(m.group(1))} and {self.secref(m.group(2))}", s)
        s = re.sub(r"Section~\\ref\{([^}]*)\}", lambda m: self.secref(m.group(1), "Section "), s)
        s = re.sub(r"Tables?~\\ref\{([^}]*)\}", lambda m: self.tabref(m.group(1)), s)
        s = re.sub(r"\\ref\{(faq:[^}]*)\}", lambda m: self.faqref(m.group(1)), s)
        s = re.sub(r"\\ref\{(sec:[^}]*)\}", lambda m: self.secref(m.group(1)), s)

        s = s.replace(r"\S", "§")
        s = s.replace(r"\yes", "✓").replace(r"\no", "–")
        s = s.replace(r"\checkmark", "✓")
        s = s.replace(r"\ldots", "…")
        s = s.replace(r"\dagger", "†").replace(r"\ast", "*")
        s = s.replace(r"\circ", "∘").replace(r"\cdot", "·")
        s = s.replace(r"\rightarrow", "→").replace(r"\sim", TILDE)
        s = s.replace(r"\approx", "≈").replace(r"\mid", "|")
        s = s.replace(r"\tau", "τ").replace(r"\Delta", "Δ")
        s = s.replace(r"\faGithub", "").replace(r"\faGlobe", "")

        s = s.replace("``", "“").replace("''", "”")
        s = s.replace(r"{,}", ",")
        s = s.replace(r"\,", " ").replace(r"\ ", " ")
        s = s.replace(r"\%", "%").replace(r"\&", "&").replace(r"\$", "$")
        s = s.replace(r"\{", "{").replace(r"\}", "}")
        s = s.replace(r"\emdash", "—")
        s = re.sub(r"(?<![-\\])---(?!-)", "—", s)
        s = re.sub(r"(?<![-\\])--(?!-)", "–", s)
        s = s.replace("~", " ")          # TeX non-breaking space
        s = s.replace(TILDE, "~")        # a real "approximately" tilde
        s = re.sub(r"[ \t]+", " ", s)
        return s.strip()

    def glref(self, label, text):
        text = self.inline(text) if "\\" in text or "$" in text else text
        if self.plain:
            return text
        if label not in self.gl_slug:
            raise KeyError(f"glref to unknown glossary label: {label}")
        return f"[{text}](#{self.gl_slug[label]})"

    def cite(self, keys):
        # hyperref makes every \citep a link to its bibliography entry; the
        # brackets stay literal text and each number links on its own.
        nums = [CITE_NUM[k.strip()] for k in keys.split(",")]
        if self.plain:
            return "[" + ", ".join(str(n) for n in nums) + "]"
        return "[" + ", ".join(f"[{n}](#ref-{n})" for n in nums) + "]"

    def secref(self, label, prefix=""):
        num, slug = self.sec_ref[label]
        if self.plain:
            return f"{prefix}{num}"
        return f"[{prefix}{num}](#{slug})"

    def faqref(self, label):
        q, slug = self.faq_ref[label]
        return q if self.plain else f"[{q}](#{slug})"

    def tabref(self, label):
        num, slug = self.tab_ref[label]
        return f"Table {num}" if self.plain else f"[Table {num}](#{slug})"

    def heading(self, s: str) -> str:
        self.plain = True
        try:
            return self.inline(s)
        finally:
            self.plain = False


# ------------------------------------------------------------------ the tables
# Verified row-for-row against the compiled PDF. Captions are converted from the
# tex so their glossary links stay live; only the grids are written out here.
TABLES = {
    "tab:overview": """
| # | System | val WER | val PER | **TEST WER** | **TEST PER** |
|---|---|---|---|---|---|
| — | Gowda et al., Appendix D.4 (target) [1] | n/a | n/a | 51.17 | 38.19 |
| 1 | Causal TDS + dual-CTC, *corrected* decode | 53.12 | 45.31 | **40.63** | 39.02 |
| 2 | Bidirectional Conformer + WavLM-L9 distillation | 35.54 | 27.47 | **26.14** | 22.34 |
| 3 | Ensemble → *n*-best union → LIFT rerank | n/a | n/a | **18.53** | 20.90 † |
""",
    "tab:related": """
| System | Mode | Vocab | Aud. | WER ↓ | PER ↓ | CER ↓ |
|---|---|---|---|---|---|---|
| **Facial sEMG → text: Gaddy corpus** (8 ch, 1 kHz, ~19 h, 1 speaker) [2] | | | | | | |
| Gaddy & Klein 2020 [2] \\* | silent | open | ✓ | 68.0 | – | – |
| Gaddy & Klein 2021 [3] \\* | silent | open | ✓ | 42.2 | – | – |
| Gaddy 2022 [4] | silent | open | ✓ | 28.8 | – | – |
| Gaddy 2022 [4] | vocalized | open | ✓ | 23.3 | – | – |
| MONA LISA [5] | silent | open | ✓ | 12.2 | – | – |
| MONA LISA [5] | vocalized | open | ✓ | **3.7** | – | – |
| **Facial sEMG → text: emg2speech General Corpus** (31 ch, 5 kHz, 9,660 sentences, 1 speaker) [1] | | | | | | |
| Gowda et al. 2026, App. D.4 [1] | vocalized | open | ✓ | 51.17 | 38.19 | – |
| Myovox, corrected decode (§4) | vocalized | open | ✓ | 40.63 | 39.02 | – |
| Myovox, Conformer + distillation (§5) | vocalized | open | ✓ | 26.14 | 22.34 | – |
| Myovox, Conformer, EMG-only (§5) | vocalized | open | – | 26.10 | 23.71 | – |
| **Myovox, full pipeline (§6)** | vocalized | open | ✓ | **18.53** | 20.90 † | – |
| **Non-invasive brain → text** (typed sentences, healthy volunteers) | | | | | | |
| Brain2Qwerty v1, EEG [7] | typing | open | – | – | – | 67 |
| Brain2Qwerty v1, MEG [7] | typing | open | – | – | – | 32 |
| Brain2Qwerty v2, MEG [8] | typing | open | – | 39 | – | 31 |
""",
    "tab:data": """
| Property | Value |
|---|---|
| Sentences | 9,660 (9,541 unique) |
| Subject | single, healthy |
| Electromyography | 31-channel surface array, 5 kHz |
| Parallel audio | recorded simultaneously (per-sentence duration correlation = 1.000) |
| Train / val / test | 8,500 / 760 / 400, sequential |
""",
    "tab:baseline": """
| System | val WER | val PER | **TEST WER** | **TEST PER** |
|---|---|---|---|---|
| Gowda et al., Appendix D.4 [1] | n/a | n/a | 51.17 | 38.19 |
| TDS + dual-CTC, corrected decode (this work) | 53.12 | 45.31 | **40.63** | 39.02 |
""",
    "tab:acoustic": """
| System | val WER | val PER | **TEST WER** | **TEST PER** |
|---|---|---|---|---|
| Baseline (causal TDS, Section 4) | 53.12 | 45.31 | 40.63 | 39.02 |
| Bidirectional Conformer + WavLM-L9 distillation | 35.54 | 27.47 | **26.14** | 22.34 |
| Conformer, electromyography-only (no audio) | n/a | n/a | 26.10 | 23.71 |
""",
    "tab:final": """
| Metric | Value |
|---|---|
| **Test WER (LIFT)** | **18.53** |
| Test WER, excluding 6 duplicates | 18.75 |
| Union 1-best WER (no rerank) | 23.26 |
| *n*-best oracle WER | 9.30 |
| Greedy PER (acoustic ensemble) | 20.90 |
| Verbatim-recall (leakage audit) | 0 |
| Paired bootstrap vs. 26.14 acoustic | ΔWER −7.6, 95% CI [−9.40, −5.90] |
| Paired bootstrap vs. union 1-best (23.26) | ΔWER −4.7, 95% CI [−6.22, −3.29] |
""",
}

EQUATION = """```text
L =  0.8·CTC_unit + 0.1·CTC_phone + 0.1·cons.  +  0.5·L_L2 + 0.5·L_InfoNCE + 1.0·L_rec^CTC
     └─────── acoustic (as in the baseline) ───┘  └────── cross-modal distillation ───────┘
```"""

REFERENCES = """
1. Harshavardhana T. Gowda, Daniel C. Comstock, and Lee M. Miller. *emg2speech: Synthesizing speech
   from electromyography using self-supervised speech models.* ACL 2026.
   [arXiv:2510.23969](https://arxiv.org/abs/2510.23969). Baseline reproduced here (Appendix D.4,
   "emg2text").
2. David Gaddy and Dan Klein. *Digital voicing of silent speech.* EMNLP 2020, pages 5521–5530.
   Introduces the 8-channel, single-speaker silent/vocalized facial EMG corpus.
3. David Gaddy and Dan Klein. *An improved model for voicing silent speech.* ACL-IJCNLP 2021
   (Volume 2: Short Papers).
4. David Gaddy. *Voicing Silent Speech.* PhD thesis, University of California, Berkeley, 2022.
5. Tyler Benster, Guy Wilson, Reshef Elisha, Francis R. Willett, and Shaul Druckmann. *A cross-modal
   approach to silent speech with LLM-enhanced recognition.* 2024.
   [arXiv:2403.05583](https://arxiv.org/abs/2403.05583). MONA LISA.
6. Payal Mohapatra, Akash Pandey, Xiaoyan Zhang, and Qi Zhu. *Can LLMs understand unvoiced speech?
   Exploring EMG-to-text conversion with LLMs.* ACL 2025 (Volume 2: Short Papers), pages 703–712,
   Vienna, Austria.
7. Jarod Lévy, Mingfang Zhang, Svetlana Pinet, Jérémy Rapin, Hubert Banville, Stéphane d'Ascoli, and
   Jean-Rémi King. *Brain-to-text decoding: A non-invasive approach via typing.* Nature Neuroscience,
   2025. Brain2Qwerty v1. [arXiv:2502.17480](https://arxiv.org/abs/2502.17480).
8. Mingfang Zhang, Jarod Lévy, Cedric Rommel, Jérémy Rapin, Corentin Bel, Julie Bonnaire, Daniel
   Nieto, Pierre Bourdillon, Svetlana Pinet, Stéphane d'Ascoli, Thomas Moreau, and Jean-Rémi King.
   *Accurate decoding of natural sentences from non-invasive brain recordings.* Meta AI technical
   report, 2026. Brain2Qwerty v2, 29 June 2026.
   [github.com/facebookresearch/brain2qwerty](https://github.com/facebookresearch/brain2qwerty).
9. Vassil Panayotov, Guoguo Chen, Daniel Povey, and Sanjeev Khudanpur. *LibriSpeech: An ASR corpus
   based on public domain audio books.* ICASSP 2015, pages 5206–5210.
10. Harshavardhana T. Gowda, Zachary D. McNaughton, and Lee M. Miller. *Geometry of orofacial
    neuromuscular signals: Speech articulation decoding using surface electromyography.* Journal of
    Neural Engineering, 2024.
11. Harshavardhana T. Gowda and Lee M. Miller. *Non-invasive electromyographic speech neuroprosthesis:
    A geometric perspective.* 2025. [arXiv:2502.05762](https://arxiv.org/abs/2502.05762).
12. Awni Hannun, Ann Lee, Qiantong Xu, and Ronan Collobert. *Sequence-to-sequence speech recognition
    with time-depth separable convolutions.* Interspeech 2019.
    [arXiv:1904.02619](https://arxiv.org/abs/1904.02619).
13. Alex Graves, Santiago Fernández, Faustino Gomez, and Jürgen Schmidhuber. *Connectionist temporal
    classification: Labelling unsegmented sequence data with recurrent neural networks.* ICML 2006,
    pages 369–376.
14. Wei-Ning Hsu, Benjamin Bolte, Yao-Hung Hubert Tsai, Kushal Lakhotia, Ruslan Salakhutdinov, and
    Abdelrahman Mohamed. *HuBERT: Self-supervised speech representation learning by masked prediction
    of hidden units.* IEEE/ACM TASLP, 29:3451–3460, 2021.
    [arXiv:2106.07447](https://arxiv.org/abs/2106.07447).
15. Daniel Povey et al. *k2 and icefall: FSA/FST algorithms and ASR recipes.* 2023.
    [github.com/k2-fsa/k2](https://github.com/k2-fsa/k2) ·
    [github.com/k2-fsa/icefall](https://github.com/k2-fsa/icefall).
16. Anmol Gulati, James Qin, Chung-Cheng Chiu, Niki Parmar, Yu Zhang, Jiahui Yu, Wei Han, Shibo Wang,
    Zhengdong Zhang, Yonghui Wu, and Ruoming Pang. *Conformer: Convolution-augmented transformer for
    speech recognition.* Interspeech 2020. [arXiv:2005.08100](https://arxiv.org/abs/2005.08100).
17. Sanyuan Chen, Chengyi Wang, Zhengyang Chen, Yu Wu, Shujie Liu, Zhuo Chen, Jinyu Li, Naoyuki Kanda,
    Takuya Yoshioka, Xiong Xiao, Jian Wu, Long Zhou, Shuo Ren, Yanmin Qian, Yao Qian, Michael Zeng,
    Xiangzhan Yu, and Furu Wei. *WavLM: Large-scale self-supervised pre-training for full stack speech
    processing.* IEEE JSTSP, 16(6):1505–1518, 2022.
    [arXiv:2110.13900](https://arxiv.org/abs/2110.13900).
18. Aaron van den Oord, Yazhe Li, and Oriol Vinyals. *Representation learning with contrastive
    predictive coding.* 2018. [arXiv:1807.03748](https://arxiv.org/abs/1807.03748).
19. Qwen Team. *Qwen2.5 technical report.* 2024. [arXiv:2412.15115](https://arxiv.org/abs/2412.15115).
20. Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, and Luke Zettlemoyer. *QLoRA: Efficient finetuning of
    quantized LLMs.* NeurIPS 2023. [arXiv:2305.14314](https://arxiv.org/abs/2305.14314).
21. Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, and
    Weizhu Chen. *LoRA: Low-rank adaptation of large language models.* ICLR 2022.
    [arXiv:2106.09685](https://arxiv.org/abs/2106.09685).
22. Jingyuan Li, Trung Le, Chaofei Fan, Mingfei Chen, and Eli Shlizerman. *Brain-to-text decoding with
    context-aware neural representations and large language models.* 2024. DCoND-LIFT. Journal of
    Neural Engineering, 2025. [arXiv:2411.10657](https://arxiv.org/abs/2411.10657).
"""


def main():
    tex = TEX.read_text()
    tex = re.sub(r"(?m)^\s*%.*$\n?", "", tex)   # full-line comments
    body = tex[tex.index(r"\begin{abstract}"):tex.index(r"\bibliography{references}")]

    # ---- pass 1: build the label maps ------------------------------------
    sections = re.findall(r"\\section\{((?:[^{}]|\{[^{}]*\})*)\}\s*(?:\\label\{([^}]*)\})?", body)
    sec_ref, sec_titles = {}, []
    for i, (title, label) in enumerate(sections, start=1):
        sec_titles.append((i, title))
        if label:
            sec_ref[label] = (i, None)  # slug filled after titles convert

    faq_blocks = re.findall(r"\\faqq\{((?:[^{}]|\{[^{}]*\})*)\}\s*(?:\\label\{([^}]*)\})?", body, re.S)
    faq_ref, faq_qs = {}, []
    for i, (q, label) in enumerate(faq_blocks, start=1):
        faq_qs.append((i, q))
        if label:
            faq_ref[label] = (f"Q{i}", None)

    gl = [(m.group(1), m.group(2)) for m in
          re.finditer(r"\\glentry\{([^}]*)\}\{((?:[^{}]|\{[^{}]*\})*)\}", body)]

    # Tables: number in document order, and slug from the caption heading the
    # renderer will emit, so Table~\ref can link to it.
    tab_ref = {}
    tab_caps = []
    for i, m in enumerate(re.finditer(r"\\begin\{table\}.*?\\end\{table\}", body, re.S), start=1):
        blk = m.group(0)
        lab = re.search(r"\\label\{([^}]*)\}", blk).group(1)
        cap = take_macro(blk, "caption", 1)
        tab_ref[lab] = (i, None)
        tab_caps.append((lab, i, " ".join(cap[0][1][0].split()) if cap else ""))

    conv = Converter({}, sec_ref, faq_ref, tab_ref)

    # Glossary slugs come from the rendered heading text.
    gl_slug, seen = {}, {}
    for label, term in gl:
        text = strip_md(conv.heading(term))
        s = slugify(text)
        if s in seen:
            raise SystemExit(f"slug collision: {label} and {seen[s]} both -> {s}")
        seen[s] = label
        gl_slug[label] = s
    conv.gl_slug = gl_slug

    for lab, num, cap in tab_caps:
        lead = strip_md(conv.heading(cap)).partition(". ")[0]
        tab_ref[lab] = (num, slugify(caption_head(num, lead)))

    for label, (num, _) in sec_ref.items():
        title = strip_md(conv.heading(dict(sec_titles)[num]))
        sec_ref[label] = (num, slugify(f"{num}. {title}"))
    for label, (q, _) in faq_ref.items():
        n = int(q[1:])
        qt = strip_md(conv.heading(dict(faq_qs)[n]))
        faq_ref[label] = (q, slugify(f"{q}. {qt}"))

    # ---- pass 2: emit ----------------------------------------------------
    out = []
    out.append("# Myovox: Reading Speech from the Muscles of the Face\n")
    out.append(
        "**Varshith Madishetty** · [madishettyvarshith@gmail.com](mailto:madishettyvarshith@gmail.com) ·\n"
        "[github.com/Varshith-0/myovox](https://github.com/Varshith-0/myovox) ·\n"
        "[varshith-0.github.io/myovox](https://varshith-0.github.io/myovox/)\n"
    )

    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", body, re.S).group(1)
    out.append(conv.inline(" ".join(abstract.split())) + "\n")
    out.append("---\n")

    # Walk the body section by section.
    chunks = re.split(r"(\\section\*?\{(?:[^{}]|\{[^{}]*\})*\})", body)
    secnum = 0
    for k in range(1, len(chunks), 2):
        head, text = chunks[k], chunks[k + 1]
        starred = head.startswith(r"\section*")
        title_raw = re.match(r"\\section\*?\{(.*)\}$", head, re.S).group(1)
        title = conv.heading(title_raw)
        if starred:
            out.append(f"## {title}\n")
        else:
            secnum += 1
            out.append(f"## {secnum}. {title}\n")
        out.append(render_section(text, conv))
        out.append("---\n")

    # `[](#ref-n)` is an empty link: TechnicalPage renders it as a bare jump
    # target, which is how a list item gets an id that \citep can link to.
    out.append("## References\n")
    out.append(re.sub(r"(?m)^(\d{1,2})\. ", lambda m: f"{m.group(1)}. [](#ref-{m.group(1)})",
                      REFERENCES.strip()) + "\n")

    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md)

    # Anything still TeX-shaped is a conversion the script did not handle. Fail
    # rather than ship mangled prose that reads fine until you look closely.
    leftovers = [l for l in (r"\\[a-zA-Z]+", r"(?<!\\)\$", r"(?<!\\)\{")
                 for _ in [0] if re.search(l, md)]
    if leftovers:
        for pat in leftovers:
            for m in re.finditer(pat, md):
                line = md[:m.start()].count("\n") + 1
                ctx = md.splitlines()[line - 1][:150]
                print(f"  LEFTOVER line {line}: {ctx}", file=sys.stderr)
        raise SystemExit("unconverted TeX remains; refusing to write")

    # Every internal link must resolve to an anchor this file actually defines:
    # a heading, or an explicit `[](#id)` target.
    ids = {slugify(strip_md(m.group(1))) for m in re.finditer(r"^#{2,5} (.+)$", md, re.M)}
    ids |= set(re.findall(r"\[\]\(#([^)]*)\)", md))
    dead = {h for h in re.findall(r"\]\(#([^)]*)\)", md) if h and h not in ids}
    if dead:
        raise SystemExit(f"links to non-existent anchors: {sorted(dead)}")

    # Every reference must be cited, and every citation must have a reference.
    cited = {int(n) for n in re.findall(r"\]\(#ref-(\d+)\)", md)}
    listed = {int(n) for n in re.findall(r"(?m)^(\d{1,2})\. \[\]\(#ref-", md)}
    if cited != listed:
        raise SystemExit(f"citation/reference mismatch: cited-not-listed={sorted(cited - listed)} "
                         f"listed-not-cited={sorted(listed - cited)}")

    OUT.write_text(md)
    n_links = len(re.findall(r"\]\(#", md))
    print(f"wrote {OUT}: {len(md.splitlines())} lines")
    print(f"glossary entries: {len(gl_slug)}   sections: {secnum}   faq: {len(faq_qs)}")
    print(f"internal links: {n_links}   distinct anchors defined: {len(ids)}   dead: 0")


def render_section(text, conv):
    parts = []

    # tables -> caption paragraph + grid + footnote. Runs before labels are
    # stripped, since the label is what selects the grid.
    def table_repl(m):
        b = m.group(0)
        lab = re.search(r"\\label\{([^}]*)\}", b).group(1)
        num, _ = conv.tab_ref[lab]
        cap = take_macro(b, "caption", 1)
        cap_md = conv.inline(" ".join(cap[0][1][0].split())) if cap else ""
        # Footnotes are the {\footnotesize ...\par} groups BELOW the grid. The
        # table's own \footnotesize size switch sits above \caption; searching the
        # whole block would capture the entire table as one footnote.
        tail = b.split(r"\end{tabular}")[-1]
        foots = re.findall(r"\{\\footnotesize(.*?)\\par\}", tail, re.S)
        foot_md = "\n\n".join(conv.inline(" ".join(f.split())) for f in foots)
        # "Table N. <opening sentence>" is a heading: it numbers the caption as the
        # PDF does, and it is the anchor Table~\ref links to.
        lead, sep, rest = cap_md.partition(". ")
        chunk = f"\n##### {caption_head(num, lead)}\n"
        if sep:
            chunk += f"\n{rest}\n"
        chunk += linkify_cites(TABLES[lab])
        if foot_md:
            chunk += "\n" + "\n".join("> " + l for l in foot_md.split("\n")) + "\n"
        return chunk

    raw = re.sub(r"\\begin\{table\}.*?\\end\{table\}", table_repl, text, flags=re.S)
    raw = re.sub(r"\\label\{[^}]*\}", "", raw)
    raw = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", "\n@@EQUATION@@\n", raw, flags=re.S)

    for block in re.split(r"\n\s*\n", raw):
        b = block.strip()
        if not b:
            continue
        if b == "@@EQUATION@@":
            parts.append(EQUATION)
            continue
        if b.startswith("|") or b.startswith("**") and "\n|" in b:
            parts.append(b)
            continue
        parts.append(render_block(b, conv))
    return "\n\n".join(p for p in parts if p) + "\n"


def render_block(b, conv):
    if b.lstrip().startswith("\\cathead"):
        rest = take_macro(b, "cathead", 1)
        head = conv.heading(rest[0][1][0])
        tail = b[rest[0][0][1]:].strip()
        out = f"### {head}"
        if tail:
            out += "\n\n" + render_block(tail, conv)
        return out

    if b.lstrip().startswith("\\faqq"):
        # \faqq{...} and its {faqa} answer are one source block (no blank line
        # between them), so the tail after the question must be rendered too.
        m = take_macro(b, "faqq", 1)[0]
        n = render_block.faq_n = getattr(render_block, "faq_n", 0) + 1
        q = conv.heading(" ".join(m[1][0].split()))
        out = f"#### Q{n}. {q}"
        tail = b[m[0][1]:].strip()
        if tail:
            answer = render_block(tail, conv)
            if answer:
                out += "\n\n" + answer
        return out

    if b.startswith(r"\begin{faqa}") or b.startswith(r"\end{faqa}"):
        b = b.replace(r"\begin{faqa}", "").replace(r"\end{faqa}", "").strip()
        return conv.inline(" ".join(b.split())) if b else ""

    if b.startswith(r"\begin{itemize}") or b.startswith(r"\begin{enumerate}"):
        ordered = b.startswith(r"\begin{enumerate}")
        b = re.sub(r"\\begin\{(itemize|enumerate)\}(\[[^\]]*\])?", "", b)
        b = re.sub(r"\\end\{(itemize|enumerate)\}", "", b)
        items = [i.strip() for i in b.split(r"\item") if i.strip()]
        lines = []
        for i, it in enumerate(items, start=1):
            body = conv.inline(" ".join(it.split()))
            marker = f"{i}." if ordered else "-"
            lines.append(f"{marker} {body}")
        return "\n".join(lines)

    if b.startswith(r"\begin{glosslist}") or r"\glentry" in b:
        return render_glossary(b, conv)

    if b.lstrip().startswith("\\paragraph"):
        m = take_macro(b, "paragraph", 1)[0]
        head = conv.inline(m[1][0]).rstrip(".")
        tail = b[m[0][1]:].strip()
        return f"**{head}.** " + conv.inline(" ".join(tail.split()))

    b = b.replace(r"\noindent", "").replace(r"\par", "")
    b = re.sub(r"\\(begin|end)\{(glosslist|center|faqa)\}", "", b)
    return conv.inline(" ".join(b.split()))


def render_glossary(b, conv):
    b = re.sub(r"\\(begin|end)\{glosslist\}", "", b)
    out = []
    entries = take_macro(b, "glentry", 2)
    for i, ((a, e), args) in enumerate(entries):
        term = conv.heading(args[1])
        end = entries[i + 1][0][0] if i + 1 < len(entries) else len(b)
        definition = conv.inline(" ".join(b[e:end].split()))
        out.append(f"#### {term}\n\n{definition}")
    return "\n\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
