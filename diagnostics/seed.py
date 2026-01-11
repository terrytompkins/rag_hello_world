"""Seed the diagnostics database with demo data for Daisy the dog."""

import sqlite3
from datetime import datetime, timedelta
from diagnostics.db import get_db_path, init_db


def seed_database():
    """Seed the database with demo data."""
    init_db()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    try:
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM pets WHERE name = 'Daisy'")
        if cursor.fetchone()[0] > 0:
            print("Seed data already exists. Use clear_database() first if you want to reseed.")
            return
        
        # Owner
        cursor.execute("""
            INSERT INTO owners (owner_id, full_name, phone, email)
            VALUES (?, ?, ?, ?)
        """, ("OWNER001", "Alex Morgan", "555-0100", "alex.morgan@example.com"))
        
        # Pet: Daisy
        cursor.execute("""
            INSERT INTO pets (pet_id, owner_id, name, species, breed, sex, date_of_birth, weight_kg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("PET001", "OWNER001", "Daisy", "Dog", "Mixed breed", "FN", "2018-03-15", 18.2))
        
        # Visit
        visit_datetime = (datetime.now() - timedelta(days=2)).isoformat()
        cursor.execute("""
            INSERT INTO visits (visit_id, pet_id, clinic_name, visit_datetime, chief_complaint, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "VISIT001",
            "PET001",
            "Happy Paws Veterinary Clinic",
            visit_datetime,
            "Vomiting, lethargy, decreased appetite for 2 days",
            "Patient presented with acute onset of vomiting and lethargy. Owner reports decreased appetite and some dehydration."
        ))
        
        # Analytes (CBC)
        cbc_analytes = [
            ("ANALYTE001", "WBC", "White Blood Cell Count", "10^3/μL"),
            ("ANALYTE002", "RBC", "Red Blood Cell Count", "10^6/μL"),
            ("ANALYTE003", "HCT", "Hematocrit", "%"),
            ("ANALYTE004", "HGB", "Hemoglobin", "g/dL"),
            ("ANALYTE005", "PLT", "Platelet Count", "10^3/μL"),
            ("ANALYTE006", "NEU", "Neutrophils", "%"),
            ("ANALYTE007", "LYM", "Lymphocytes", "%"),
        ]
        
        # Analytes (Chemistry)
        chem_analytes = [
            ("ANALYTE008", "BUN", "Blood Urea Nitrogen", "mg/dL"),
            ("ANALYTE009", "CREA", "Creatinine", "mg/dL"),
            ("ANALYTE010", "ALT", "Alanine Aminotransferase", "U/L"),
            ("ANALYTE011", "ALP", "Alkaline Phosphatase", "U/L"),
            ("ANALYTE012", "GLU", "Glucose", "mg/dL"),
            ("ANALYTE013", "TP", "Total Protein", "g/dL"),
            ("ANALYTE014", "ALB", "Albumin", "g/dL"),
            ("ANALYTE015", "GLOB", "Globulin", "g/dL"),
            ("ANALYTE016", "NA", "Sodium", "mEq/L"),
            ("ANALYTE017", "K", "Potassium", "mEq/L"),
            ("ANALYTE018", "CL", "Chloride", "mEq/L"),
        ]
        
        all_analytes = cbc_analytes + chem_analytes
        cursor.executemany("""
            INSERT INTO analytes (analyte_id, analyte_code, analyte_name, unit)
            VALUES (?, ?, ?, ?)
        """, all_analytes)
        
        # Reference ranges for Dog
        # CBC ranges
        dog_ranges_cbc = [
            ("RANGE001", "Dog", "ANALYTE001", 6.0, 17.0, None),  # WBC
            ("RANGE002", "Dog", "ANALYTE002", 5.5, 8.5, None),  # RBC
            ("RANGE003", "Dog", "ANALYTE003", 37.0, 55.0, None),  # HCT
            ("RANGE004", "Dog", "ANALYTE004", 12.0, 18.0, None),  # HGB
            ("RANGE005", "Dog", "ANALYTE005", 200.0, 500.0, None),  # PLT
            ("RANGE006", "Dog", "ANALYTE006", 60.0, 77.0, None),  # NEU
            ("RANGE007", "Dog", "ANALYTE007", 12.0, 30.0, None),  # LYM
        ]
        
        # Chemistry ranges
        dog_ranges_chem = [
            ("RANGE008", "Dog", "ANALYTE008", 7.0, 27.0, None),  # BUN
            ("RANGE009", "Dog", "ANALYTE009", 0.5, 1.6, None),  # CREA
            ("RANGE010", "Dog", "ANALYTE010", 10.0, 100.0, None),  # ALT
            ("RANGE011", "Dog", "ANALYTE011", 23.0, 212.0, None),  # ALP
            ("RANGE012", "Dog", "ANALYTE012", 70.0, 120.0, None),  # GLU
            ("RANGE013", "Dog", "ANALYTE013", 5.2, 7.2, None),  # TP
            ("RANGE014", "Dog", "ANALYTE014", 2.5, 4.0, None),  # ALB
            ("RANGE015", "Dog", "ANALYTE015", 2.3, 3.5, None),  # GLOB
            ("RANGE016", "Dog", "ANALYTE016", 140.0, 154.0, None),  # NA
            ("RANGE017", "Dog", "ANALYTE017", 3.5, 5.6, None),  # K
            ("RANGE018", "Dog", "ANALYTE018", 105.0, 115.0, None),  # CL
        ]
        
        all_ranges = dog_ranges_cbc + dog_ranges_chem
        cursor.executemany("""
            INSERT INTO reference_ranges (range_id, species, analyte_id, low_value, high_value, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, all_ranges)
        
        # Tests
        test_datetime = visit_datetime
        result_datetime = (datetime.fromisoformat(visit_datetime) + timedelta(hours=2)).isoformat()
        
        cursor.execute("""
            INSERT INTO tests (test_id, visit_id, test_name, specimen_type, ordered_datetime, result_datetime, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("TEST001", "VISIT001", "CBC", "Blood", test_datetime, result_datetime, "Final"))
        
        cursor.execute("""
            INSERT INTO tests (test_id, visit_id, test_name, specimen_type, ordered_datetime, result_datetime, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("TEST002", "VISIT001", "Chemistry Panel", "Serum", test_datetime, result_datetime, "Final"))
        
        # CBC Results (some abnormal)
        cbc_results = [
            ("RESULT001", "TEST001", "ANALYTE001", 18.5, None, "10^3/μL", "H", None),  # WBC high
            ("RESULT002", "TEST001", "ANALYTE002", 5.8, None, "10^6/μL", "N", None),  # RBC normal
            ("RESULT003", "TEST001", "ANALYTE003", 42.0, None, "%", "N", None),  # HCT normal
            ("RESULT004", "TEST001", "ANALYTE004", 14.2, None, "g/dL", "N", None),  # HGB normal
            ("RESULT005", "TEST001", "ANALYTE005", 185.0, None, "10^3/μL", "L", None),  # PLT low
            ("RESULT006", "TEST001", "ANALYTE006", 78.0, None, "%", "H", None),  # NEU high
            ("RESULT007", "TEST001", "ANALYTE007", 15.0, None, "%", "N", None),  # LYM normal
        ]
        
        # Chemistry Results (some abnormal - consistent with dehydration/possible kidney issues)
        chem_results = [
            ("RESULT008", "TEST002", "ANALYTE008", 32.0, None, "mg/dL", "H", None),  # BUN high
            ("RESULT009", "TEST002", "ANALYTE009", 1.8, None, "mg/dL", "H", None),  # CREA high
            ("RESULT010", "TEST002", "ANALYTE010", 85.0, None, "U/L", "N", None),  # ALT normal
            ("RESULT011", "TEST002", "ANALYTE011", 245.0, None, "U/L", "H", None),  # ALP high
            ("RESULT012", "TEST002", "ANALYTE012", 95.0, None, "mg/dL", "N", None),  # GLU normal
            ("RESULT013", "TEST002", "ANALYTE013", 6.8, None, "g/dL", "N", None),  # TP normal
            ("RESULT014", "TEST002", "ANALYTE014", 3.2, None, "g/dL", "N", None),  # ALB normal
            ("RESULT015", "TEST002", "ANALYTE015", 3.6, None, "g/dL", "N", None),  # GLOB normal
            ("RESULT016", "TEST002", "ANALYTE016", 148.0, None, "mEq/L", "N", None),  # NA normal
            ("RESULT017", "TEST002", "ANALYTE017", 4.2, None, "mEq/L", "N", None),  # K normal
            ("RESULT018", "TEST002", "ANALYTE018", 108.0, None, "mEq/L", "N", None),  # CL normal
        ]
        
        all_results = cbc_results + chem_results
        cursor.executemany("""
            INSERT INTO test_results (result_id, test_id, analyte_id, value_num, value_text, unit, flag, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, all_results)
        
        conn.commit()
        print("✓ Seed data loaded successfully!")
        print(f"  - Owner: Alex Morgan")
        print(f"  - Pet: Daisy (Dog)")
        print(f"  - Visit: {visit_datetime}")
        print(f"  - Tests: CBC, Chemistry Panel")
        print(f"  - Results: {len(all_results)} analytes")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        conn.close()


def clear_database():
    """Clear all data from the database (keeps schema)."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM test_results")
        cursor.execute("DELETE FROM tests")
        cursor.execute("DELETE FROM visits")
        cursor.execute("DELETE FROM pets")
        cursor.execute("DELETE FROM owners")
        cursor.execute("DELETE FROM reference_ranges")
        cursor.execute("DELETE FROM analytes")
        conn.commit()
        print("✓ Database cleared successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Error clearing database: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_database()
    else:
        seed_database()
