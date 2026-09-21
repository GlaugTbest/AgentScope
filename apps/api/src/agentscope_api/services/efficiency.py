"""Deterministic efficiency calculations; simulated prices never imply billing."""
from sqlalchemy.orm import Session

from ..models import ExperimentModel, PriceCatalogModel


def estimate_price(catalog: PriceCatalogModel, input_tokens: int, output_tokens: int):
    nano = (input_tokens * catalog.input_per_million_nano_usd + output_tokens * catalog.output_per_million_nano_usd) // 1_000_000
    return {"catalog_id": catalog.catalog_id, "simulated": True, "input_tokens": input_tokens, "output_tokens": output_tokens, "estimated_cost_nano_usd": nano, "estimated_cost_usd": f"{nano / 1_000_000_000:.9f}"}


def _summary(samples: list[dict]):
    count = len(samples)
    return {"samples": count, "quality": sum(item["quality"] for item in samples) / count, "tokens": sum(item["input_tokens"] + item["output_tokens"] for item in samples), "latency_ms": sum(item["latency_ms"] for item in samples) / count}


def analyze_experiment(experiment: ExperimentModel):
    baseline = _summary(experiment.baseline)
    variant = _summary(experiment.variant)
    quality_delta = variant["quality"] - baseline["quality"]
    token_delta = variant["tokens"] - baseline["tokens"]
    latency_delta = variant["latency_ms"] - baseline["latency_ms"]
    if token_delta < 0 and quality_delta >= -0.05:
        recommendation = "adopt_variant"
        reason = "A variante reduziu tokens sem queda relevante de qualidade."
    elif quality_delta < -0.05:
        recommendation = "keep_baseline"
        reason = "A variante degradou a qualidade além do limite de 0,05."
    else:
        recommendation = "collect_more_evidence"
        reason = "A comparação não mostra uma redução de consumo com qualidade preservada."
    return {"experiment_id": experiment.experiment_id, "baseline": baseline, "variant": variant, "deltas": {"quality": quality_delta, "tokens": token_delta, "latency_ms": latency_delta}, "recommendation": recommendation, "reason": reason, "evidence": {"baseline_samples": baseline["samples"], "variant_samples": variant["samples"], "quality_threshold": 0.05}}
