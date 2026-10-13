"""Run the SentiEdge AI NLP pipeline over a JSONL dataset."""

import argparse
import json
import sys
import time
from pathlib import Path

from src.nlp.pipeline import process_record


DEFAULT_INPUT = Path("data/final/government_data_tokenized.jsonl")
DEFAULT_OUTPUT = Path("data/processed/government_data_nlp.jsonl")
DEFAULT_SUMMARY = Path("reports/pipeline_batch_summary.json")


def main():
    parser = argparse.ArgumentParser(
        description="Process government records through the NLP pipeline."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    source = args.input
    output = args.output
    summary_path = args.summary

    if not source.is_file():
        parser.error(f"Input file does not exist: {source}")

    resolved_source = source.resolve()
    resolved_output = output.resolve()
    resolved_summary = summary_path.resolve()

    if resolved_source in {resolved_output, resolved_summary}:
        parser.error("Output and summary must not overwrite the input file.")

    if resolved_output == resolved_summary:
        parser.error("Output and summary must use different paths.")

    # Refuse to overwrite any existing results.
    existing = [
        path for path in (output, summary_path)
        if path.exists()
    ]
    if existing:
        parser.error(
            "Refusing to overwrite existing files: "
            + ", ".join(str(path) for path in existing)
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    total = successful = partial = failed = 0
    started = time.time()
    failures = []

    try:
        with source.open("r", encoding="utf-8-sig") as src, \
             output.open("x", encoding="utf-8") as dst:

            for line_number, line in enumerate(src, start=1):
                if not line.strip():
                    continue

                total += 1

                try:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        raise ValueError("JSONL record must be an object")

                    result = process_record(record)
                    status = result["nlp_results"]["status"]

                    if status == "success":
                        successful += 1
                    else:
                        partial += 1
                        failures.append({
                            "line": line_number,
                            "status": "partial",
                            "errors": result["nlp_results"]["errors"],
                        })

                    dst.write(
                        json.dumps(result, ensure_ascii=False) + "\n"
                    )

                except Exception as exc:
                    failed += 1
                    failures.append({
                        "line": line_number,
                        "status": "failed",
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    })

                    error_record = {
                        "source_line": line_number,
                        "pipeline_error": {
                            "type": type(exc).__name__,
                            "message": str(exc),
                        },
                    }

                    # Preserve the original record when it was parsed.
                    if "record" in locals() and isinstance(record, dict):
                        error_record["record"] = record

                    dst.write(
                        json.dumps(error_record, ensure_ascii=False) + "\n"
                    )

                if total % 25 == 0:
                    dst.flush()
                    elapsed = time.time() - started
                    print(
                        f"Processed {total} | success={successful} "
                        f"| partial={partial} | failed={failed} "
                        f"| elapsed={elapsed:.1f}s",
                        flush=True,
                    )

                # Avoid accidentally reusing the previous record on bad JSON.
                record = None

    except Exception:
        print(
            "Batch run stopped unexpectedly. Inspect the output file before "
            "resuming; rerunning will not overwrite existing output.",
            file=sys.stderr,
        )
        raise

    elapsed = time.time() - started
    summary = {
        "input": str(source),
        "output": str(output),
        "total_records": total,
        "successful_records": successful,
        "partial_records": partial,
        "failed_records": failed,
        "elapsed_seconds": round(elapsed, 2),
        "failures": failures,
    }

    with summary_path.open("x", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print("\n===== BATCH SUMMARY =====")
    print(json.dumps(
        {key: value for key, value in summary.items() if key != "failures"},
        ensure_ascii=False,
        indent=2,
    ))
    print("Summary saved to:", summary_path)


if __name__ == "__main__":
    main()
