from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


def read_excel(path: str) -> List[Dict[str, Any]]:
    df = pd.read_excel(path)
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def write_excel(path: str, rows: Iterable[Dict[str, Any]], columns: Optional[List[str]] = None) -> None:
    df = pd.DataFrame(list(rows))
    if columns:
        for column in columns:
            if column not in df.columns:
                df[column] = None
        df = df[columns]

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)
