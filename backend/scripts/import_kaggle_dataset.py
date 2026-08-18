"""Automated script to batch-import Kaggle medical reports into the database."""
import os
import sys
import argparse
import csv
import random

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import SessionLocal, init_db
from app.database.models import User
from app.core.security import hash_password
from app.services.storage_service import LocalStorageService
from app.services.report_pipeline import process_report_pipeline
from app.repositories.report_repository import ReportRepository


def get_or_create_default_user(db):
    """Ensures a default user exists for importing datasets."""
    email = "dataset.admin@example.com"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, password_hash=hash_password("KaggleImport2026!"))
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created default dataset owner: {email}")
    return user


def import_text_report(db, user, storage, filename, text_content):
    """Stores text content and runs the complete 10-stage processing pipeline."""
    content_bytes = text_content.encode("utf-8")
    stored_path = storage.save_file(content_bytes, filename)
    report_id = f"REP-{random.randint(10000, 99999)}"

    report, job = ReportRepository.create_report(
        db=db,
        user_id=user.id,
        report_id=report_id,
        filename=filename,
        stored_path=stored_path,
        storage_type="local",
    )

    process_report_pipeline(report.id, job.id)
    return report


def process_csv_file(csv_path, max_records=50):
    """Parses a Kaggle CSV dataset and ingests text reports."""
    init_db()
    db = SessionLocal()
    storage = LocalStorageService(base_dir="./storage/uploads")
    user = get_or_create_default_user(db)

    print(f"\n[INFO] Reading Kaggle CSV: {csv_path}")
    count = 0

    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        candidate_cols = ["transcription", "report", "text", "description", "content", "clinical_note"]
        text_col = None
        for col in reader.fieldnames or []:
            if col.lower().strip() in candidate_cols:
                text_col = col
                break

        if not text_col:
            text_col = reader.fieldnames[0] if reader.fieldnames else None

        print(f"[INFO] Identified report text column: '{text_col}'")

        for idx, row in enumerate(reader):
            if count >= max_records:
                print(f"Reached maximum import limit ({max_records} records).")
                break

            text_data = row.get(text_col, "").strip()
            if len(text_data) < 20:
                continue

            doc_name = f"kaggle_report_{idx + 1}.txt"
            report = import_text_report(db, user, storage, doc_name, text_data)
            print(f"  [{count + 1}/{max_records}] Ingested {doc_name} -> Report ID: {report.report_id} (Type: {report.report_type})")
            count += 1

    db.close()
    print(f"\n[OK] Successfully imported and analyzed {count} medical reports into your database!")


def process_directory(dir_path):
    """Processes all report files in a directory."""
    init_db()
    db = SessionLocal()
    storage = LocalStorageService(base_dir="./storage/uploads")
    user = get_or_create_default_user(db)

    valid_exts = (".txt", ".pdf", ".png", ".jpg", ".jpeg")
    files = [f for f in os.listdir(dir_path) if f.lower().endswith(valid_exts)]
    print(f"\n[INFO] Found {len(files)} files in directory: {dir_path}")

    for idx, fname in enumerate(files):
        fpath = os.path.join(dir_path, fname)
        with open(fpath, "rb") as f:
            content_bytes = f.read()

        stored_path = storage.save_file(content_bytes, fname)
        report_id = f"REP-{random.randint(10000, 99999)}"

        report, job = ReportRepository.create_report(
            db=db,
            user_id=user.id,
            report_id=report_id,
            filename=fname,
            stored_path=stored_path,
            storage_type="local",
        )
        process_report_pipeline(report.id, job.id)
        print(f"  [{idx + 1}/{len(files)}] Processed {fname} -> Report ID: {report.report_id} (Type: {report.report_type})")

    db.close()
    print(f"\n[OK] All {len(files)} files successfully processed and stored in database!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Kaggle Medical Datasets")
    parser.add_argument("--file", help="Path to Kaggle CSV file")
    parser.add_argument("--dir", help="Path to directory of report files")
    parser.add_argument("--limit", type=int, default=30, help="Max records to import from CSV")

    args = parser.parse_args()

    if args.file:
        process_csv_file(args.file, max_records=args.limit)
    elif args.dir:
        process_directory(args.dir)
    else:
        print("Please specify --file <path_to_csv> or --dir <path_to_folder>")
        print("Example: python backend/scripts/import_kaggle_dataset.py --dir sample_reports/")
