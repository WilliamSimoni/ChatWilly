import os

import yaml
from chatwilly_knowledge.core.model import extractor_model
from chatwilly_knowledge.core.semantic_process import semantic_process
from chatwilly_knowledge.data.extract_text import extract_text, get_file_hash
from chatwilly_knowledge.settings import knowledge_settings


def get_staging_file_path(original_filename):
    """
    Converts 'my_cv.pdf' -> 'staging/my_cv.yaml'
    """
    file_stem = os.path.splitext(original_filename)[0]
    yaml_name = f"{file_stem}.yaml"
    return os.path.join(knowledge_settings.staging_folder, yaml_name)


def run_processor():
    if not os.path.exists(knowledge_settings.staging_folder):
        os.makedirs(knowledge_settings.staging_folder)

    error_log_path = os.path.join(
        knowledge_settings.staging_folder, "processing_errors.yaml"
    )

    local_files = [
        f
        for f in os.listdir(knowledge_settings.document_folder)
        if f.endswith((".pdf", ".docx", ".txt"))
    ]

    processed_count = 0
    skipped_count = 0
    error_list = []

    print(
        f"📂 Found {len(local_files)} documents in {knowledge_settings.document_folder}"
    )

    for filename in local_files:
        source_path = os.path.join(knowledge_settings.document_folder, filename)
        staging_path = get_staging_file_path(filename)

        try:
            current_hash = get_file_hash(source_path)

            if os.path.exists(staging_path):
                with open(staging_path, "r", encoding="utf-8") as f:
                    existing_data = yaml.safe_load(f) or {}

                if existing_data.get("file_hash") == current_hash:
                    print(f"⏭Skipping {filename} (Up to date)")
                    skipped_count += 1
                    continue

            print(f"Processing {filename}...")
            raw_text = extract_text(source_path)

            if not raw_text:
                raise ValueError("Text extraction returned empty string or None.")

            processed_data = semantic_process(raw_text, extractor_model)

            if not processed_data or not processed_data.get("chunks"):
                raise ValueError(
                    "Semantic processor returned empty data (Parsing failed or LLM Error)."
                )

            file_data = {
                "source_filename": filename,
                "file_hash": current_hash,
                "document_summary": processed_data["document_summary"],
                "content": processed_data["chunks"],
            }

            with open(staging_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    file_data,
                    f,
                    allow_unicode=True,
                    sort_keys=False,
                    default_flow_style=False,
                )

            print(f"Saved to {os.path.basename(staging_path)}")
            processed_count += 1

        except Exception as e:
            error_msg = str(e)
            print(f"Error on {filename}: {error_msg}")

            error_list.append({"filename": filename, "error": error_msg})

            if os.path.exists(staging_path):
                try:
                    os.remove(staging_path)
                except OSError:
                    pass

    if error_list:
        print(
            f"\nWriting {len(error_list)} errors to {os.path.basename(error_log_path)}"
        )
        with open(error_log_path, "w", encoding="utf-8") as f:
            yaml.dump(error_list, f, allow_unicode=True, sort_keys=False)
    else:
        if os.path.exists(error_log_path):
            os.remove(error_log_path)

    print("\nProcessor finished.")
    print(f"   - Processed: {processed_count}")
    print(f"   - Skipped (Cached): {skipped_count}")
    print(f"   - Errors: {len(error_list)}")


if __name__ == "__main__":
    run_processor()
