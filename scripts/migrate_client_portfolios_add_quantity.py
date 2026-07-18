from __future__ import annotations

import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path


REQUIRED_TICKER_ALIASES = (
    "Ticker",
    "ticker",
    "Symbol",
    "symbol",
    "Code",
    "code",
)

REQUIRED_COST_ALIASES = (
    "Cost",
    "cost",
    "CostPrice",
    "cost_price",
    "AverageCost",
    "average_cost",
    "AvgPrice",
    "avg_price",
)

QUANTITY_ALIASES = (
    "Quantity",
    "quantity",
    "Qty",
    "qty",
    "Volume",
    "volume",
)


def find_first_column(
    fieldnames: list[str],
    aliases: tuple[str, ...],
) -> str | None:
    for alias in aliases:
        if alias in fieldnames:
            return alias

    return None


def normalize_text(value: object) -> str:
    if value is None:
        return ""

    return str(value).strip()


def create_backup(
    source_file: Path,
    backup_root: Path,
    clients_folder: Path,
) -> Path:
    relative_path = source_file.relative_to(clients_folder)
    backup_file = backup_root / relative_path

    backup_file.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source_file, backup_file)

    return backup_file


def read_csv(
    file_path: Path,
) -> tuple[list[str], list[dict[str, str]]]:
    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header")

        fieldnames = [
            normalize_text(field)
            for field in reader.fieldnames
            if field is not None
        ]

        rows = [
            {
                normalize_text(key): normalize_text(value)
                for key, value in row.items()
                if key is not None
            }
            for row in reader
        ]

    return fieldnames, rows


def write_migrated_csv(
    file_path: Path,
    original_fieldnames: list[str],
    rows: list[dict[str, str]],
    ticker_column: str,
    cost_column: str,
    quantity_column: str | None,
) -> None:
    output_fieldnames = [
        "Ticker",
        "Quantity",
        "Cost",
    ]

    migrated_rows: list[dict[str, str]] = []

    for row in rows:
        migrated_rows.append(
            {
                "Ticker": normalize_text(
                    row.get(ticker_column)
                ).upper(),
                "Quantity": (
                    normalize_text(row.get(quantity_column))
                    if quantity_column is not None
                    else ""
                ),
                "Cost": normalize_text(
                    row.get(cost_column)
                ),
            }
        )

    temporary_file = file_path.with_suffix(
        file_path.suffix + ".tmp"
    )

    with temporary_file.open(
        mode="w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=output_fieldnames,
        )

        writer.writeheader()
        writer.writerows(migrated_rows)

    temporary_file.replace(file_path)


def migrate_file(
    file_path: Path,
    clients_folder: Path,
    backup_root: Path,
    dry_run: bool,
) -> str:
    fieldnames, rows = read_csv(file_path)

    ticker_column = find_first_column(
        fieldnames,
        REQUIRED_TICKER_ALIASES,
    )

    cost_column = find_first_column(
        fieldnames,
        REQUIRED_COST_ALIASES,
    )

    quantity_column = find_first_column(
        fieldnames,
        QUANTITY_ALIASES,
    )

    if ticker_column is None:
        return "SKIPPED: missing Ticker/Symbol column"

    if cost_column is None:
        return "SKIPPED: missing Cost column"

    already_standard = fieldnames == [
        "Ticker",
        "Quantity",
        "Cost",
    ]

    if already_standard:
        return "SKIPPED: already migrated"

    if dry_run:
        return (
            f"DRY-RUN: would migrate "
            f"{len(rows)} position(s)"
        )

    backup_file = create_backup(
        source_file=file_path,
        backup_root=backup_root,
        clients_folder=clients_folder,
    )

    write_migrated_csv(
        file_path=file_path,
        original_fieldnames=fieldnames,
        rows=rows,
        ticker_column=ticker_column,
        cost_column=cost_column,
        quantity_column=quantity_column,
    )

    return (
        f"MIGRATED: {len(rows)} position(s), "
        f"backup={backup_file}"
    )


def migrate_folder(
    clients_folder: Path,
    file_pattern: str,
    dry_run: bool,
) -> int:
    if not clients_folder.exists():
        raise FileNotFoundError(
            f"Clients folder not found: {clients_folder}"
        )

    if not clients_folder.is_dir():
        raise NotADirectoryError(
            f"Not a directory: {clients_folder}"
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_root = (
        clients_folder
        / "_migration_backups"
        / f"quantity_migration_{timestamp}"
    )

    client_files = sorted(
        clients_folder.glob(file_pattern)
    )

    if not client_files:
        print(
            f"No files matched pattern "
            f"'{file_pattern}' in {clients_folder}"
        )
        return 0

    migrated_count = 0
    skipped_count = 0
    failed_count = 0

    print("=" * 70)
    print("PE_V2.4 CLIENT PORTFOLIO MIGRATION")
    print(f"Folder : {clients_folder}")
    print(f"Pattern: {file_pattern}")
    print(f"Dry run: {dry_run}")
    print("=" * 70)

    for file_path in client_files:
        try:
            result = migrate_file(
                file_path=file_path,
                clients_folder=clients_folder,
                backup_root=backup_root,
                dry_run=dry_run,
            )

            print(f"{file_path.name}: {result}")

            if result.startswith("MIGRATED"):
                migrated_count += 1
            else:
                skipped_count += 1

        except Exception as exc:
            failed_count += 1
            print(
                f"{file_path.name}: FAILED: {exc}"
            )

    print("=" * 70)
    print(f"Migrated: {migrated_count}")
    print(f"Skipped : {skipped_count}")
    print(f"Failed  : {failed_count}")

    if not dry_run and migrated_count > 0:
        print(f"Backup  : {backup_root}")

    print("=" * 70)

    return 1 if failed_count > 0 else 0


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Add Quantity column to PE_V2.4 "
            "client portfolio CSV files."
        )
    )

    parser.add_argument(
        "--clients-folder",
        required=True,
        help=(
            "Folder containing client_*.csv files"
        ),
    )

    parser.add_argument(
        "--pattern",
        default="client_*.csv",
        help=(
            "File pattern. Default: client_*.csv"
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Preview changes without modifying files"
        ),
    )

    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    return migrate_folder(
        clients_folder=Path(
            args.clients_folder
        ).expanduser().resolve(),
        file_pattern=args.pattern,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())