from pathlib import Path
from typing import Optional, Union
from werkzeug.security import generate_password_hash

from database.db import close_db, get_db

SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"


def seed_data(db_path: Optional[Union[Path, str]] = None) -> None:
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Database schema file not found: {SCHEMA_FILE}")

    conn = get_db(db_path)
    try:
        conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))

        with conn:
            users_data = [
                {
                    "name": "Admin Officer",
                    "roll_no": "ADM001",
                    "email": "admin@campus.edu",
                    "password_hash": generate_password_hash("Admin@123"),
                    "role": "admin",
                },
                {
                    "name": "Aarav Sharma",
                    "roll_no": "2023CS01",
                    "email": "aarav@campus.edu",
                    "password_hash": generate_password_hash("Student@123"),
                    "role": "student",
                },
                {
                    "name": "Diya Patel",
                    "roll_no": "2023EC15",
                    "email": "diya@campus.edu",
                    "password_hash": generate_password_hash("Student@123"),
                    "role": "student",
                },
                {
                    "name": "Rohan Verma",
                    "roll_no": "2023ME42",
                    "email": "rohan@campus.edu",
                    "password_hash": generate_password_hash("Student@123"),
                    "role": "student",
                },
            ]

            for user in users_data:
                conn.execute(
                    """
                    INSERT INTO users (name, roll_no, email, password_hash, role)
                    SELECT ?, ?, ?, ?, ?
                    WHERE NOT EXISTS (SELECT 1 FROM users WHERE roll_no = ?);
                    """,
                    (
                        user["name"],
                        user["roll_no"],
                        user["email"],
                        user["password_hash"],
                        user["role"],
                        user["roll_no"],
                    ),
                )

            user_ids = {
                row["roll_no"]: row["user_id"]
                for row in conn.execute("SELECT roll_no, user_id FROM users;").fetchall()
            }

            # Canonical 7 locations matching PRD.md Section 4.2 and Canvas Map (800x500)
            locations_data = [
                ("Main Gate", 100, 400),
                ("Central Library", 250, 220),
                ("Academic Block A", 420, 180),
                ("Canteen", 380, 360),
                ("Hostel Complex", 650, 380),
                ("Sports Ground", 700, 150),
                ("Admin Vault", 500, 260),
            ]

            for name, x, y in locations_data:
                conn.execute(
                    """
                    INSERT INTO locations (name, x_coord, y_coord)
                    SELECT ?, ?, ?
                    WHERE NOT EXISTS (SELECT 1 FROM locations WHERE name = ?);
                    """,
                    (name, x, y, name),
                )

            loc_ids = {
                row["name"]: row["loc_id"]
                for row in conn.execute("SELECT name, loc_id FROM locations;").fetchall()
            }

            # Canonical 10 campus edges matching PRD.md and Canvas Map
            edges_data = [
                ("Main Gate", "Central Library", 150.0),
                ("Main Gate", "Canteen", 200.0),
                ("Central Library", "Academic Block A", 110.0),
                ("Central Library", "Canteen", 140.0),
                ("Academic Block A", "Sports Ground", 220.0),
                ("Academic Block A", "Admin Vault", 130.0),
                ("Canteen", "Hostel Complex", 180.0),
                ("Canteen", "Admin Vault", 95.0),
                ("Hostel Complex", "Admin Vault", 160.0),
                ("Sports Ground", "Admin Vault", 190.0),
            ]

            for src_name, dst_name, dist in edges_data:
                src_id = loc_ids[src_name]
                dst_id = loc_ids[dst_name]
                conn.execute(
                    """
                    INSERT INTO campus_edges (src_loc_id, dst_loc_id, distance_meters)
                    SELECT ?, ?, ?
                    WHERE NOT EXISTS (
                        SELECT 1 FROM campus_edges
                        WHERE (src_loc_id = ? AND dst_loc_id = ?)
                           OR (src_loc_id = ? AND dst_loc_id = ?)
                    );
                    """,
                    (src_id, dst_id, dist, src_id, dst_id, dst_id, src_id),
                )

            items_data = [
                {
                    "user_roll": "2023ME42",
                    "type": "LOST",
                    "title": "Dell XPS 15 Laptop",
                    "category": "Electronics",
                    "description": "Silver Dell XPS 15 with carbon fiber palm rest, lost near study desks.",
                    "serial_tag": "DELL-9821-X",
                    "loc_name": "Central Library",
                    "cluster_root_id": None,
                    "item_weight": 3,
                    "priority_value": 25,
                    "deadline_hours": 48,
                    "status": "OPEN",
                },
                {
                    "user_roll": "2023EC15",
                    "type": "FOUND",
                    "title": "Dell Laptop Silver 15-inch",
                    "category": "Electronics",
                    "description": "Found silver 15-inch Dell laptop in lab 3.",
                    "serial_tag": "DELL-9821-X",
                    "loc_name": "Academic Block A",
                    "cluster_root_id": None,
                    "item_weight": 3,
                    "priority_value": 25,
                    "deadline_hours": 48,
                    "status": "OPEN",
                },
                {
                    "user_roll": "2023CS01",
                    "type": "LOST",
                    "title": "Blue Hydro Flask 750ml",
                    "category": "Accessories",
                    "description": "Cobalt blue Hydro Flask insulated water bottle with scratch on lid.",
                    "serial_tag": None,
                    "loc_name": "Canteen",
                    "cluster_root_id": None,
                    "item_weight": 1,
                    "priority_value": 10,
                    "deadline_hours": 72,
                    "status": "OPEN",
                },
                {
                    "user_roll": "2023EC15",
                    "type": "FOUND",
                    "title": "Blue Flask Water Bottle",
                    "category": "Accessories",
                    "description": "Blue stainless steel bottle found on cafeteria table.",
                    "serial_tag": None,
                    "loc_name": "Canteen",
                    "cluster_root_id": None,
                    "item_weight": 1,
                    "priority_value": 10,
                    "deadline_hours": 72,
                    "status": "OPEN",
                },
                {
                    "user_roll": "2023CS01",
                    "type": "LOST",
                    "title": "Student ID Card 2023CS01",
                    "category": "Documents",
                    "description": "Campus RFID student ID card in transparent lanyard holder.",
                    "serial_tag": "2023CS01",
                    "loc_name": "Main Gate",
                    "cluster_root_id": None,
                    "item_weight": 1,
                    "priority_value": 15,
                    "deadline_hours": 24,
                    "status": "OPEN",
                },
            ]

            for item in items_data:
                uid = user_ids[item["user_roll"]]
                lid = loc_ids[item["loc_name"]]
                conn.execute(
                    """
                    INSERT INTO items (
                        user_id, type, title, category, description, serial_tag,
                        loc_id, cluster_root_id, item_weight, priority_value,
                        deadline_hours, status
                    )
                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    WHERE NOT EXISTS (
                        SELECT 1 FROM items
                        WHERE title = ? AND type = ? AND user_id = ?
                    );
                    """,
                    (
                        uid,
                        item["type"],
                        item["title"],
                        item["category"],
                        item["description"],
                        item["serial_tag"],
                        lid,
                        item["cluster_root_id"],
                        item["item_weight"],
                        item["priority_value"],
                        item["deadline_hours"],
                        item["status"],
                        item["title"],
                        item["type"],
                        uid,
                    ),
                )

            item_rows = conn.execute("SELECT item_id, title, type, user_id FROM items;").fetchall()
            item_ids = {
                (row["title"], row["type"], row["user_id"]): row["item_id"]
                for row in item_rows
            }

            matches_data = [
                {
                    "lost_title": "Dell XPS 15 Laptop",
                    "lost_user_roll": "2023ME42",
                    "found_title": "Dell Laptop Silver 15-inch",
                    "found_user_roll": "2023EC15",
                    "lcs_score": 0.76,
                    "spatial_dist": 110.0,
                    "confidence_score": 0.88,
                    "assigned_slot": 1,
                    "status": "PENDING",
                },
                {
                    "lost_title": "Blue Hydro Flask 750ml",
                    "lost_user_roll": "2023CS01",
                    "found_title": "Blue Flask Water Bottle",
                    "found_user_roll": "2023EC15",
                    "lcs_score": 0.70,
                    "spatial_dist": 0.0,
                    "confidence_score": 0.85,
                    "assigned_slot": 2,
                    "status": "APPROVED",
                },
            ]

            for match in matches_data:
                lost_uid = user_ids[match["lost_user_roll"]]
                found_uid = user_ids[match["found_user_roll"]]
                lost_id = item_ids.get((match["lost_title"], "LOST", lost_uid))
                found_id = item_ids.get((match["found_title"], "FOUND", found_uid))
                if lost_id and found_id:
                    conn.execute(
                        """
                        INSERT INTO matches (
                            lost_item_id, found_item_id, lcs_score, spatial_dist,
                            confidence_score, assigned_slot, status
                        )
                        SELECT ?, ?, ?, ?, ?, ?, ?
                        WHERE NOT EXISTS (
                            SELECT 1 FROM matches
                            WHERE lost_item_id = ? AND found_item_id = ?
                        );
                        """,
                        (
                            lost_id,
                            found_id,
                            match["lcs_score"],
                            match["spatial_dist"],
                            match["confidence_score"],
                            match["assigned_slot"],
                            match["status"],
                            lost_id,
                            found_id,
                        ),
                    )
    finally:
        close_db(conn)


if __name__ == "__main__":
    seed_data()
