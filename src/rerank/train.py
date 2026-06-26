"""LIFT step 2 — QLoRA fine-tune a local instruct LLM on (n-best + phonemes -> reference) pairs.

TRAIN split only (leakage-safe). 4-bit base + LoRA fit in 12 GB. Completion-only loss (prompt tokens
masked to -100). Uses transformers.Trainer + peft directly (NOT trl, whose unconditional `import
wandb` is broken in this env). Adapter saved under checkpoints/.
"""
import argparse, json
import torch
from datasets import load_dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
                          Trainer, TrainingArguments, DataCollatorForSeq2Seq)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

from myovox.config import apply_config_and_logging
from myovox.paths import CKPT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train_jsonl", required=True)
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--name", default="lift_qwen")
    ap.add_argument("--epochs", type=float, default=3.0)
    ap.add_argument("--bs", type=int, default=2)
    ap.add_argument("--accum", type=int, default=8)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--r", type=int, default=16)
    ap.add_argument("--max_len", type=int, default=320)
    ap.add_argument("--max_steps", type=int, default=-1)
    args = apply_config_and_logging(ap)
    out = CKPT / args.name; out.mkdir(parents=True, exist_ok=True)

    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    def tokenize(ex):
        full_msgs = [{"role": "system", "content": ex["system"]},
                     {"role": "user", "content": ex["user"]},
                     {"role": "assistant", "content": ex["target"]}]
        full = tok.apply_chat_template(full_msgs, tokenize=False)
        prompt = tok.apply_chat_template(full_msgs[:-1], tokenize=False, add_generation_prompt=True)
        ids = tok(full, truncation=True, max_length=args.max_len).input_ids
        plen = len(tok(prompt, truncation=True, max_length=args.max_len).input_ids)
        labels = [-100] * min(plen, len(ids)) + ids[plen:]
        labels = labels[:len(ids)]
        return {"input_ids": ids, "attention_mask": [1] * len(ids), "labels": labels}

    ds = load_dataset("json", data_files=args.train_jsonl, split="train")
    ds = ds.map(tokenize, remove_columns=ds.column_names, num_proc=4)
    print(f"[lift_train] {len(ds)} examples; e.g. lens "
          f"in={len(ds[0]['input_ids'])} sup={sum(1 for l in ds[0]['labels'] if l!=-100)}", flush=True)

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=bnb, device_map={"": 0})
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    model.config.use_cache = False
    lora = LoraConfig(r=args.r, lora_alpha=2 * args.r, lora_dropout=0.05, bias="none",
                      task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                      "gate_proj", "up_proj", "down_proj"])
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    targs = TrainingArguments(
        output_dir=str(out), num_train_epochs=args.epochs, max_steps=args.max_steps,
        per_device_train_batch_size=args.bs, gradient_accumulation_steps=args.accum,
        learning_rate=args.lr, lr_scheduler_type="cosine", warmup_ratio=0.03,
        logging_steps=20, save_strategy="no", fp16=True, optim="paged_adamw_8bit",
        gradient_checkpointing=True, gradient_checkpointing_kwargs={"use_reentrant": False},
        report_to=[], dataloader_num_workers=2, remove_unused_columns=False,
    )
    coll = DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100)
    trainer = Trainer(model=model, args=targs, train_dataset=ds, data_collator=coll)
    trainer.train()
    model.save_pretrained(str(out))
    tok.save_pretrained(str(out))
    print(f"[lift_train] saved adapter -> {out}", flush=True)
    print("LIFT_TRAIN_DONE", flush=True)


if __name__ == "__main__":
    main()
