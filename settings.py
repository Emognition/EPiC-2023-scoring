from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()
DEFAULT_MAIL_FILE_PATH = PROJECT_DIR / "emails_teams.csv"
STORAGE_DIR = PROJECT_DIR / "storage"
DEFAULT_PROCESSING_DIR = STORAGE_DIR / "current_processing"
DETAILED_SCORES_DIR = STORAGE_DIR / "detailed_scores"
SCORED_FILES_MEMORY_DIR = STORAGE_DIR / "scored_submissions"
TEST_SETS_DEFAULT_DIR = STORAGE_DIR / "test_sets"
PREVIOUS_EVALUATIONS_DIR = STORAGE_DIR / "previous_evaluations"
DEFAULT_SUBMISSIONS_DIR = PROJECT_DIR / "submissions_to_score"
FINAL_SUBMISSIONS_DIR = PROJECT_DIR / "FINAL_SUBMISSIONS"
