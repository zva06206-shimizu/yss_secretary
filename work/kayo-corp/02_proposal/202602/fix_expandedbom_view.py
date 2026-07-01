import argparse
import sqlite3

SQL = r"""
DROP VIEW IF EXISTS ExpandedBOM;
CREATE VIEW ExpandedBOM AS
WITH RECURSIVE tree AS (
    SELECT
        0 AS Level,
        b.ParentCode AS RootCode,
        '' AS ParentCode,
        b.ParentCode AS ItemCode,
        (SELECT sm.SheetParentName FROM SheetMaster sm WHERE sm.SheetParentCode = b.ParentCode LIMIT 1) AS ItemName,
        1.0 AS CumulativeQty
    FROM (SELECT DISTINCT ParentCode FROM BomEdge WHERE ParentCode IS NOT NULL AND ParentCode <> '') b
    WHERE b.ParentCode NOT IN (SELECT DISTINCT ChildCode FROM BomEdge WHERE ChildCode IS NOT NULL AND ChildCode <> '')

    UNION ALL

    SELECT
        t.Level + 1 AS Level,
        t.RootCode AS RootCode,
        e.ParentCode AS ParentCode,
        e.ChildCode AS ItemCode,
        COALESCE(e.ChildName, '') AS ItemName,
        t.CumulativeQty * COALESCE(e.Qty, 1.0) AS CumulativeQty
    FROM tree t
    JOIN BomEdge e ON e.ParentCode = t.ItemCode
    WHERE t.Level < 30
)
SELECT
    CAST(Level AS INTEGER) AS Level,
    CAST(RootCode AS TEXT) AS RootCode,
    CAST(ParentCode AS TEXT) AS ParentCode,
    CAST(ItemCode AS TEXT) AS ItemCode,
    CAST(ItemName AS TEXT) AS ItemName,
    CAST(CumulativeQty AS REAL) AS CumulativeQty
FROM tree;
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="parts_data.db のパス")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.executescript(SQL)
    conn.commit()
    conn.close()
    print("OK: ExpandedBOM view recreated.")


if __name__ == "__main__":
    main()
