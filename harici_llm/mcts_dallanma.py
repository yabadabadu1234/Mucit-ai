"""
Verilen kodun test-time egitim + MCTS dallanma (turbo_dfs) mekanizmasi,
aynen uygulanmis halde. Tek gercek celiski: orijinal kod Qwen tokenizer'ina
sabitlenmis ARC_VOCAB/USER_TOKEN_ID/PAD_ID degerleri kullaniyordu; bizim uc
model ailemiz (RWKV-7, Mamba-Codestral, Falcon-Mamba) tamamen farkli
tokenizer'lara sahip oldugundan bu ID'ler dinamik olarak her tokenizer'dan
cikarilir (arac_kelime_dagarcigi_olustur). Ikinci celiski: RWKV/Mamba HF
forward() imzasi `past_key_values=` yerine kendi ozel cache parametresini
kullanir; bunu cozen ince bir uyumluluk katmani eklendi, turbo_dfs'in DFS
dallanma mantiginin kendisi degistirilmedi.
"""
import time
from collections import defaultdict
from typing import Any, Dict, List, Tuple

import torch

PAD_ID_YER_TUTUCU = -1


def arac_kelime_dagarcigi_olustur(tokenizer: Any) -> Dict[str, int]:
    """Her tokenizer icin 0-9 rakam token'lari, satir sonu ve EOS'u
    dinamik olarak bulur (Qwen'e sabitlenmis ARC_VOCAB'in yerini alir)."""
    sozluk: Dict[str, int] = {}
    for rakam in "0123456789":
        idler = tokenizer.encode(rakam, add_special_tokens=False)
        if len(idler) == 1:
            sozluk[rakam] = idler[0]
    for aday in ("\n", "Ċ"):
        idler = tokenizer.encode(aday, add_special_tokens=False)
        if len(idler) == 1:
            sozluk["\n"] = idler[0]
            break
    sozluk["<eos>"] = tokenizer.eos_token_id
    sozluk["<pad>"] = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    return sozluk


def _ileri_gecis(model: Any, model_ailesi: str, input_ids: torch.Tensor,
                  position_ids: Any, onbellek: Any) -> Any:
    """Model ailesine gore dogru cache parametre adini kullanarak tek
    adim ileri gecis yapar. RWKV `state=`, Mamba `cache_params=`,
    standart transformer `past_key_values=` bekler."""
    if model_ailesi == "rwkv":
        return model(input_ids=input_ids, state=onbellek, use_cache=True, return_dict=True)
    if model_ailesi in ("mamba", "falcon_mamba"):
        return model(input_ids=input_ids, cache_params=onbellek, use_cache=True, return_dict=True)
    return model(
        input_ids=input_ids, position_ids=position_ids,
        past_key_values=onbellek, use_cache=True, return_dict=True,
    )


def _onbellegi_al(outputs: Any, model_ailesi: str) -> Any:
    if model_ailesi == "rwkv":
        return outputs.state
    if model_ailesi in ("mamba", "falcon_mamba"):
        return getattr(outputs, "cache_params", None)
    return outputs.past_key_values


def turbo_dfs(model, model_ailesi, arac_vocab, logits, max_new_tokens, max_score,
              scores, pos, cache, start_time, end_time) -> dict:

    n = logits.size(0)

    arac_tokenlari = [v for k, v in arac_vocab.items() if k not in ("<pad>",)]
    eos_id = arac_vocab["<eos>"]
    pad_id = arac_vocab["<pad>"]

    nll = torch.tensor(scores, dtype=torch.float32).view(n, 1) - logits.float().cpu().log_softmax(-1)

    suffixes = defaultdict(list)
    candidates = dict()

    for i in range(n):
        candidates[i] = []
        for t in arac_tokenlari:
            score = nll[i, t].item()
            if score < max_score:
                if t == eos_id:
                    suffixes[i].append((score, [t]))
                elif max_new_tokens > 1:
                    candidates[i].append((score, t))

    for i in range(n):
        candidates[i] = sorted(candidates[i], key=lambda x: x[0])

    while time.time() - start_time < 540 and time.time() < end_time:

        batch_tokens = []
        batch_scores = []
        num_alive_beams = 0

        for i in range(n):
            if len(candidates[i]) == 0:
                batch_tokens.append(pad_id)
                batch_scores.append(1000)
            else:
                score, t = candidates[i].pop(0)
                batch_tokens.append(t)
                batch_scores.append(score)
                num_alive_beams += 1

        if num_alive_beams == 0:
            break

        outputs = _ileri_gecis(
            model, model_ailesi,
            input_ids=torch.tensor(batch_tokens, device=model.device, dtype=torch.long).view(-1, 1),
            position_ids=torch.full((n, 1), pos, device=model.device),
            onbellek=cache,
        )

        next_suffixes = turbo_dfs(
            model, model_ailesi, arac_vocab,
            logits=outputs.logits[:, -1],
            max_new_tokens=max_new_tokens - 1,
            max_score=max_score,
            scores=batch_scores,
            pos=pos + 1,
            cache=_onbellegi_al(outputs, model_ailesi),
            start_time=start_time,
            end_time=end_time,
        )

        for batch_id, beams in next_suffixes.items():
            for score, suffix_tokens in beams:
                suffix_tokens.insert(0, batch_tokens[batch_id])
                suffixes[batch_id].append((score, suffix_tokens))

    return suffixes


@torch.no_grad()
def inference_turbo_dfs(model, model_ailesi, arac_vocab, prefix_tokens, max_new_tokens, max_score, end_time):
    input_ids = torch.tensor(prefix_tokens, device=model.device, dtype=torch.long)
    outputs = _ileri_gecis(model, model_ailesi, input_ids=input_ids, position_ids=None, onbellek=None)
    suffixes = turbo_dfs(
        model, model_ailesi, arac_vocab,
        logits=outputs.logits[:, -1],
        max_new_tokens=max_new_tokens,
        max_score=max_score,
        scores=[0.0] * input_ids.size(0),
        pos=input_ids.size(1),
        cache=_onbellegi_al(outputs, model_ailesi),
        start_time=time.time(),
        end_time=end_time,
    )
    result = []
    for batch_id, beams in suffixes.items():
        sorted_beams = sorted(beams, key=lambda x: x[0])
        result.append((batch_id, sorted_beams))
    return result


@torch.no_grad()
def calc_scores(queries, answers, tokenizer, model, model_ailesi, pad_id) -> List[float]:
    batch_query_tokens = []
    batch_answer_tokens = []
    batch_tokens = []
    batch_lengths = []
    for query, answer in zip(queries, answers):
        query_tokens = tokenizer.encode(query)
        answer_tokens = tokenizer.encode(answer)
        tokens = query_tokens + answer_tokens
        batch_query_tokens.append(query_tokens)
        batch_answer_tokens.append(answer_tokens)
        batch_tokens.append(tokens)
        batch_lengths.append(len(tokens))
    max_len = max(batch_lengths)
    padded_tokens = []
    for tokens in batch_tokens:
        padded = tokens + [pad_id] * (max_len - len(tokens))
        padded_tokens.append(padded)
    input_ids = torch.tensor(padded_tokens, device=model.device, dtype=torch.long)
    outputs = _ileri_gecis(model, model_ailesi, input_ids=input_ids, position_ids=None, onbellek=None)
    batch_logits = outputs.logits.float().cpu().log_softmax(-1)
    result = []
    for logits, query_tokens, answer_tokens in zip(batch_logits, batch_query_tokens, batch_answer_tokens):
        query_length = len(query_tokens)
        answer_logits = logits[query_length - 1:query_length - 1 + len(answer_tokens)]
        answer_score = answer_logits[torch.arange(len(answer_tokens)), answer_tokens].sum()
        result.append(-answer_score.item())
    return result
