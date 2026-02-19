r"""
Run QAEvalChain against a set of QA examples.

Usage (from project root):
  .\.venv\Scripts\python.exe .\scripts\qa_eval.py --data data\processed\qa_eval_dataset.json
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict

from importlib import import_module

from src.database import list_indexes, load_vector_store, get_retriever
from src.llm import get_llm, create_rag_chain
from src.summary_metrics import generate_summary_metrics, get_prompt_metrics_context


DEFAULT_OUTPUT = Path("reports") / "qa_eval_results.json"


def load_examples(data_path: Path) -> List[Dict[str, str]]:
    if data_path.exists():
        with data_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    return [
        {
            "query": "Which region has the highest total sales?",
            "answer": "West is the best-performing region by total sales."
        },
        {
            "query": "What is the best month for sales performance?",
            "answer": "April is the best-performing month."
        },
        {
            "query": "Which product is the top seller by value?",
            "answer": "Widget A is the top-selling product by value."
        }
    ]


def get_qa_eval_chain(llm):
    try:
        module = import_module("langchain.evaluation")
        return module.QAEvalChain.from_llm(llm)
    except Exception:
        try:
            module = import_module("langchain.evaluation.qa")
            return module.QAEvalChain.from_llm(llm)
        except Exception as exc:  # pragma: no cover - missing dependency
            raise RuntimeError(
                "QAEvalChain is unavailable. Install/upgrade langchain and try again."
            ) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Run QAEvalChain evaluation")
    parser.add_argument("--data", type=str, default="data/processed/qa_eval_dataset.json")
    parser.add_argument("--index", type=str, default="")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    data_path = Path(args.data)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    examples = load_examples(data_path)
    if not examples:
        print("No evaluation examples found.")
        return 1

    index_name = args.index
    if not index_name:
        indexes = list_indexes()
        if not indexes:
            print("No vector indexes found. Create a vector store first.")
            return 1
        index_name = indexes[0]

    vector_store = load_vector_store(index_name)
    if not vector_store:
        print(f"Could not load vector store: {index_name}")
        return 1

    retriever = get_retriever(vector_store, k=5)
    llm = get_llm()

    metrics = generate_summary_metrics()
    chain = create_rag_chain(
        retriever,
        llm,
        metrics_provider=lambda q: get_prompt_metrics_context(metrics, query=q)
    )

    predictions = []
    for example in examples:
        query = example.get("query") or example.get("question") or ""
        response = chain.invoke(query)
        response_text = response.content if hasattr(response, "content") else response
        predictions.append({"result": str(response_text)})

    eval_chain = get_qa_eval_chain(llm)
    graded = eval_chain.evaluate(examples, predictions)

    result = {
        "index": index_name,
        "data_file": str(data_path),
        "examples": examples,
        "predictions": predictions,
        "grades": graded,
    }

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    print(f"Saved evaluation results to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
