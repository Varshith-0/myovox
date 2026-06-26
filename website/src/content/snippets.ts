/**
 * Curated code excerpts for the Code page. Each is faithful to the actual
 * implementation in the Myovox repository (lightly trimmed for clarity); the
 * page links to the real files. Keep these in sync with the source if it moves.
 */

export interface Snippet {
  readonly id: string
  readonly title: string
  readonly language: string
  readonly source: string
  readonly description: string
  readonly code: string
}

export const SNIPPETS: readonly Snippet[] = [
  {
    id: 'objective',
    title: 'The four-term cross-modal objective',
    language: 'text',
    source: 'src/training/train.py',
    description:
      'The headline encoder is pulled toward the parallel audio’s WavLM-Large layer-9 features. Two CTC heads, a feature-regression term, a frame-synchronous contrastive term, and — load-bearing — a frozen WavLM→phoneme recognizer that forces the projection to stay phoneme-decodable.',
    code: `Loss = 0.8·CTC_unit  + 0.1·CTC_phone + 0.1·consistency
     + 0.5·L2(proj, WavLM-L9)          (i)   feature regression  (masked, resampled)
     + 0.5·InfoNCE(proj, WavLM-L9)     (ii)  frame-synchronous contrast (τ = 0.1)
     + 1.0·CTC(recognizer(proj), phones)  (iii) frozen WavLM→phoneme head`,
  },
  {
    id: 'encoder',
    title: 'Bidirectional Conformer encoder',
    language: 'python',
    source: 'src/models/model.py',
    description:
      'The full-context replacement for the upstream causal TDS: a torchaudio Conformer over the rotation-invariant feature front-end, with two CTC heads (HuBERT-unit + phoneme) and a WavLM projection. Self-attention is inherently full-context; the depthwise conv supplies local context.',
    code: `def forward(self, inputs, in_lens=None):
    x = inputs.permute(1, 0, 2, 3).contiguous()   # (T, N, C, C)
    y = self.featNorm(x)
    y = self.riMlp(y)                              # (T, N, H)
    T, N, H = y.shape
    ycb = y.permute(1, 0, 2).contiguous()         # (N, T, H)
    g, _ = self.conformer(ycb, lengths)           # (N, T, H), full-context
    g = g.permute(1, 0, 2).contiguous()           # (T, N, H)
    y = self.enc_norm(y + g)                       # residual + norm
    z = self.post(y)                               # (T, N, bottleneck)
    return {
        "unitLogprobs":  F.log_softmax(self.unitHead(z),  dim=-1),
        "phoneLogprobs": F.log_softmax(self.phoneHead(z), dim=-1),
        "distill":       self.distill(z),          # → WavLM 1024-dim space
    }`,
  },
  {
    id: 'contrast',
    title: 'Frame-synchronous InfoNCE',
    language: 'python',
    source: 'src/models/losses.py',
    description:
      'Term (ii): a symmetric, frame-aligned contrastive loss between the EMG projection and the resampled WavLM frames. Each EMG frame must match its own audio frame against all others in the utterance.',
    code: `def crosscon_loss(distill_TBD, wavlm_BTD, in_lens, tau=0.1):
    emg = distill_TBD.permute(1, 0, 2)            # (B, T, D)
    B, T_emg, _ = emg.shape
    w_res = F.interpolate(wavlm_BTD.transpose(1, 2), size=T_emg,
                          mode="linear").transpose(1, 2)
    e_n, w_n = F.normalize(emg, dim=-1), F.normalize(w_res, dim=-1)
    loss = 0.0
    for b in range(B):
        Tt = min(int(in_lens[b]), T_emg)          # valid frames in this utterance
        sim = (e_n[b, :Tt] @ w_n[b, :Tt].T) / tau
        lab = torch.arange(Tt, device=sim.device)
        loss += (F.cross_entropy(sim, lab) + F.cross_entropy(sim.T, lab)) / 2
    return loss / B`,
  },
  {
    id: 'decode',
    title: 'Open-vocabulary decode hyperparameters',
    language: 'python',
    source: 'src/config.py',
    description:
      'The decode-time knobs the public release omitted — the single largest lever from 51% → 40% WER on the baseline. Tuned on validation, applied once to test, over a 34,546-word HLG lexicon.',
    code: `OFFLINE_SCALE     = 0.25   # acoustic scale (headline Conformer; 1.0 for baseline)
DEFAULT_BLANK_PEN = 2.0    # CTC blank-emission penalty (posteriors are blank-dominant)
DECODE_SCALES     = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]   # validation tuning grid
# HLG = H ∘ L ∘ G  (k2 / icefall), 34,546-word LibriSpeech-derived lexicon`,
  },
  {
    id: 'reproduce',
    title: 'Reproduce the numbers',
    language: 'bash',
    source: 'scripts/run.sh',
    description:
      'Every step is idempotent — skipped if its output exists. --check verifies the cached artifacts reproduce 26.14 (acoustic) and 18.53 (final); the bare command trains the whole chain from scratch.',
    code: `bash scripts/setup.sh           # deps + icefall WFST decoder + OSF data
pip install -e .

bash scripts/run.sh --check     # verify cached 26.14 + 18.53   (~15 min, GPU)
bash scripts/run.sh             # full pipeline from scratch    (~15–25 h, GPU 0)`,
  },
] as const
