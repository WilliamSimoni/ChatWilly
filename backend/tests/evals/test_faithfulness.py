from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatwilly_backend.graph.agents import evaluation_model
from chatwilly_backend.graph.graph import build_agent
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import faithfulness

EVAL_QUESTIONS: list[str] = [
    "Which tecnologies di you learn from your startup experience?",
]

EVALS_DIR = Path(__file__).parent
DATASETS_DIR = EVALS_DIR / "datasets"
RESULTS_DIR = EVALS_DIR / "results"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

DATASET_BASE_NAME = "chatwilly_faithfulness"

evaluator_llm = LangchainLLMWrapper(evaluation_model)


def _versioned_dataset_name(dataset_base_name: str) -> str:
    """cd
    Returns a dataset name that includes a timestamp for versioning.
    Example: chatwilly_faithfulness_202503191430
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    return f"{dataset_base_name}_{timestamp}"


async def run_graph_for_question(agent, question: str) -> dict[str, Any]:
    """
    Invoke the full ChatWilly graph for a single question.
    Returns a dict with:
      - question
      - answer       (grounded response from response_grounding node)
      - contexts     (raw tool outputs — used by RAGAS as retrieved context)
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    final_state = await agent.ainvoke(
        {"messages": [HumanMessage(content=question)]},
        config=config,
    )

    messages: list = final_state.get("messages", [])

    answer = ""
    for m in reversed(messages):
        if isinstance(m, AIMessage) and m.content:
            answer = m.content
            break

    last_human_idx = 0
    for i, m in enumerate(messages):
        if isinstance(m, HumanMessage):
            last_human_idx = i

    contexts: list[str] = []
    for m in messages[last_human_idx:]:
        if isinstance(m, ToolMessage) and m.content:
            contexts.append(str(m.content))

    if not contexts:
        contexts = ["(no tool output retrieved)"]

    return {
        "question": question,
        "answer": answer,
        "contexts": contexts,
    }


async def collect_eval_samples(agent) -> list[dict[str, Any]]:
    """Run all eval questions concurrently and collect samples."""
    tasks = [run_graph_for_question(agent, q) for q in EVAL_QUESTIONS]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    samples = []
    for q, result in zip(EVAL_QUESTIONS, results):
        if isinstance(result, Exception):
            print(f"[WARN] Question failed: {q!r}\n  Error: {result}")
            samples.append(
                {
                    "question": q,
                    "answer": "",
                    "contexts": ["(error — no tool output)"],
                }
            )
        else:
            samples.append(result)

    return samples


def build_ragas_dataset(samples: list[dict[str, Any]]) -> tuple[EvaluationDataset, str]:
    """
    Build a versioned native RAGAS Dataset from collected samples and persist
    it to tests/evals/datasets/<dataset_name>/ as a local CSV backend.

    The dataset name embeds a timestamp so every run produces a distinct,
    reloadable snapshot:
        chatwilly_faithfulness_202503191430

    Returns:
        dataset      — the RAGAS Dataset object, ready for evaluate()
        dataset_name — the versioned name used for storage and JSON results
    """
    dataset_name = _versioned_dataset_name(DATASET_BASE_NAME)

    dataset = []

    for i, sample in enumerate(samples):
        dataset.append(
            {
                "id": f"sample_{i + 1:03d}",
                "user_input": sample["question"],
                "response": sample["answer"],
                "retrieved_contexts": sample["contexts"],
            }
        )

    output_dir = Path(str(DATASETS_DIR)) / dataset_name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "dataset.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    ragas_dataset = EvaluationDataset.from_list(dataset, name=dataset_name)

    return ragas_dataset


def print_results_table(
    samples: list[dict], scores: list[float], dataset_name: str
) -> None:
    col_w = 55
    print("\n" + "=" * 80)
    print(f"  CHATWILLY — FAITHFULNESS EVALUATION  [{dataset_name}]")
    print("=" * 80)
    print(f"  {'Question':<{col_w}} {'Faithfulness':>12}")
    print("-" * 80)
    for sample, score in zip(samples, scores):
        q = sample["question"]
        if len(q) > col_w - 2:
            q = q[: col_w - 5] + "..."
        score_str = f"{score:.3f}" if isinstance(score, float) else str(score)
        print(f"  {q:<{col_w}} {score_str:>12}")
    print("-" * 80)
    valid_scores = [s for s in scores if isinstance(s, float)]
    mean_score = sum(valid_scores) / max(len(valid_scores), 1)
    print(f"  {'MEAN FAITHFULNESS':<{col_w}} {mean_score:>12.3f}")
    print("=" * 80 + "\n")


def save_results(
    samples: list[dict],
    scores: list[float],
    dataset_name: str,
) -> Path:
    """Save full results as JSON, named after the versioned dataset."""
    valid_scores = [s for s in scores if isinstance(s, float)]
    output = {
        "dataset_name": dataset_name,
        "run_at": datetime.utcnow().isoformat() + "Z",
        "mean_faithfulness": float(sum(valid_scores) / max(len(valid_scores), 1)),
        "results": [
            {
                "question": s["question"],
                "answer": s["answer"],
                "contexts": s["contexts"],
                "faithfulness_score": score,
            }
            for s, score in zip(samples, scores)
        ],
    }
    # Mirror the dataset name so CSV and JSON are trivially matched
    path = RESULTS_DIR / f"{dataset_name}.json"
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"Results saved → {path}")
    return path


async def run_evaluation() -> float:
    """
    Full pipeline.  Returns mean faithfulness score.
    Can be awaited directly or called from pytest.
    """
    checkpointer = MemorySaver()
    agent = build_agent(checkpointer=checkpointer)

    print(f"\nRunning {len(EVAL_QUESTIONS)} questions through the ChatWilly graph…")
    samples = await collect_eval_samples(agent)

    print("Building RAGAS dataset and evaluating faithfulness…")
    dataset = build_ragas_dataset(samples)
    import ipdb

    ipdb.set_trace()
    result = evaluate(dataset, metrics=[faithfulness], llm=evaluator_llm)

    result_df = result.to_pandas()
    scores: list[float] = result_df["faithfulness"].tolist()

    print_results_table(samples, scores, dataset.name)
    save_results(samples, scores, dataset.name)

    mean_score = float(result_df["faithfulness"].mean())
    return mean_score


def test_faithfulness_above_threshold():
    """
    Pytest entry point.
    Fails the test suite if mean faithfulness drops below PASS_THRESHOLD.
    Adjust the threshold to match your quality bar.
    """
    PASS_THRESHOLD = 0.75

    mean_score = asyncio.run(run_evaluation())

    print(f"\nMean faithfulness: {mean_score:.3f}  (threshold: {PASS_THRESHOLD})")
    assert mean_score >= PASS_THRESHOLD, (
        f"Faithfulness {mean_score:.3f} is below threshold {PASS_THRESHOLD}. "
        "Check tests/evals/results/ for the full breakdown."
    )


if __name__ == "__main__":
    asyncio.run(run_evaluation())
