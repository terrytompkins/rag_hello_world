PRAGMA foreign_keys = ON;

-- --- Core entities ---
CREATE TABLE IF NOT EXISTS owners (
  owner_id        TEXT PRIMARY KEY,
  full_name       TEXT NOT NULL,
  phone           TEXT,
  email           TEXT
);

CREATE TABLE IF NOT EXISTS pets (
  pet_id          TEXT PRIMARY KEY,
  owner_id        TEXT NOT NULL REFERENCES owners(owner_id),
  name            TEXT NOT NULL,
  species         TEXT NOT NULL,        -- e.g., Dog, Cat
  breed           TEXT,
  sex             TEXT,                 -- M, F, MN, FN
  date_of_birth   TEXT,                 -- ISO date
  weight_kg       REAL
);

CREATE TABLE IF NOT EXISTS visits (
  visit_id        TEXT PRIMARY KEY,
  pet_id          TEXT NOT NULL REFERENCES pets(pet_id),
  clinic_name     TEXT NOT NULL,
  visit_datetime  TEXT NOT NULL,        -- ISO datetime
  chief_complaint TEXT,
  notes           TEXT
);

-- --- Diagnostics orders / panels ---
CREATE TABLE IF NOT EXISTS tests (
  test_id         TEXT PRIMARY KEY,
  visit_id        TEXT NOT NULL REFERENCES visits(visit_id),
  test_name       TEXT NOT NULL,        -- e.g., "CBC", "Chemistry Panel", "Urinalysis"
  specimen_type   TEXT,                 -- e.g., Blood, Serum, Urine
  ordered_datetime TEXT,
  result_datetime  TEXT,
  status          TEXT                  -- e.g., Final
);

-- --- Individual analytes in a test (e.g., ALT, AST, WBC) ---
CREATE TABLE IF NOT EXISTS analytes (
  analyte_id      TEXT PRIMARY KEY,
  analyte_code    TEXT NOT NULL,        -- e.g., ALT, BUN, WBC
  analyte_name    TEXT NOT NULL,
  unit            TEXT NOT NULL
);

-- Reference ranges can vary by species (and optionally age group)
CREATE TABLE IF NOT EXISTS reference_ranges (
  range_id        TEXT PRIMARY KEY,
  species         TEXT NOT NULL,        -- Dog/Cat
  analyte_id      TEXT NOT NULL REFERENCES analytes(analyte_id),
  low_value       REAL,
  high_value      REAL,
  notes           TEXT
);

-- Results: one row per analyte per test
CREATE TABLE IF NOT EXISTS test_results (
  result_id       TEXT PRIMARY KEY,
  test_id         TEXT NOT NULL REFERENCES tests(test_id),
  analyte_id      TEXT NOT NULL REFERENCES analytes(analyte_id),
  value_num       REAL,                 -- numeric value when applicable
  value_text      TEXT,                 -- for qualitative results (e.g., "Negative")
  unit            TEXT NOT NULL,        -- duplicated for convenience / display
  flag            TEXT,                 -- H, L, N, or NULL
  comment         TEXT
);

-- Helpful views (optional) for easier reporting / NL queries
CREATE VIEW IF NOT EXISTS v_results AS
SELECT
  v.visit_id,
  v.visit_datetime,
  p.name AS pet_name,
  p.species,
  t.test_id,
  t.test_name,
  a.analyte_code,
  a.analyte_name,
  r.value_num,
  r.value_text,
  r.unit,
  r.flag
FROM test_results r
JOIN tests t     ON t.test_id = r.test_id
JOIN visits v    ON v.visit_id = t.visit_id
JOIN pets p      ON p.pet_id = v.pet_id
JOIN analytes a  ON a.analyte_id = r.analyte_id;
