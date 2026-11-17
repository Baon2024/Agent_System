import json

# GBP per USD, checked 2026-11-17. Update when the exchange rate changes.
# https://wise.com/gb/currency-converter/usd-to-gbp-rate/history/17-11-2026
USD_TO_GBP = 0.7584


def save_gemini_cost(usage):
    """Print and save Gemini 3 Flash Preview token cost estimates in GBP."""
    if usage is None:
        print("Gemini cost unavailable: response has no usage metadata.")
        return

    from datetime import datetime, timezone
    from pathlib import Path

    prompt_tokens = usage.prompt_token_count or 0
    cached_tokens = usage.cached_content_token_count or 0
    candidate_tokens = usage.candidates_token_count or 0
    thoughts_tokens = usage.thoughts_token_count or 0
    # Candidates are visible output; thoughts are additional billed output.
    output_tokens = candidate_tokens + thoughts_tokens

    # Standard USD rates per million tokens, checked 2026-11-17:
    # https://ai.google.dev/gemini-api/docs/pricing#gemini-3-flash-preview
    audio_tokens = sum(item.token_count or 0 for item in usage.prompt_tokens_details or []
                       if item.modality == "AUDIO")
    cached_audio_tokens = sum(item.token_count or 0 for item in usage.cache_tokens_details or []
                              if item.modality == "AUDIO")
    input_cost = ((prompt_tokens - cached_tokens - audio_tokens + cached_audio_tokens) * 0.50
                  + (audio_tokens - cached_audio_tokens) * 1.00) / 1_000_000
    cached_cost = ((cached_tokens - cached_audio_tokens) * 0.05
                   + cached_audio_tokens * 0.10) / 1_000_000
    candidate_cost = candidate_tokens * 3.00 / 1_000_000
    thoughts_cost = thoughts_tokens * 3.00 / 1_000_000
    input_cost *= USD_TO_GBP
    cached_cost *= USD_TO_GBP
    candidate_cost *= USD_TO_GBP
    thoughts_cost *= USD_TO_GBP
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": "gemini-3-flash-preview",
        "currency": "GBP",
        "usd_to_gbp_rate": USD_TO_GBP,
        "exchange_rate_date": "2026-11-17",
        "prompt_tokens": prompt_tokens,
        "cached_tokens": cached_tokens,
        "candidate_tokens": candidate_tokens,
        "thoughts_tokens": thoughts_tokens,
        "output_tokens": output_tokens,
        "input_cost_gbp": round(input_cost, 10),
        "cached_cost_gbp": round(cached_cost, 10),
        "candidate_cost_gbp": round(candidate_cost, 10),
        "thoughts_cost_gbp": round(thoughts_cost, 10),
        "output_cost_gbp": round(candidate_cost + thoughts_cost, 10),
        "estimated_cost_gbp": round(input_cost + cached_cost + candidate_cost + thoughts_cost, 10),
    }
    print(f"Gemini cost: £{entry['estimated_cost_gbp']:.8f} GBP | {json.dumps(entry)}", flush=True)
    try:
        path = Path(__file__).with_name("gemini_costs.json")
        log = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"currency": "GBP", "calls": []}
        log["calls"].append(entry)
        log["total_estimated_cost_gbp"] = round(sum(call.get("estimated_cost_gbp") or 0 for call in log["calls"]), 10)
        path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"Could not save Gemini cost: {error}", flush=True)
