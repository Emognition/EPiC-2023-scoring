from pathlib import Path
from settings import DEFAULT_MAIL_FILE_PATH, DEFAULT_PROCESSING_DIR, SCORED_FILES_MEMORY_DIR, TEST_SETS_DEFAULT_DIR, PREVIOUS_EVALUATIONS_DIR
from datetime import datetime
import pandas as pd
import zipfile
import os
import re
import json
import shutil
# from logging import 


"""
TODO 
- Add logs with names of processed files in each session
- scores -> "scores_<datetime>.csv" with (mail, team, score) results
"""


full_test_set_path = TEST_SETS_DEFAULT_DIR / "final_test_set"
file_check_regex = re.compile("EPiC23_.+_Attempt_\d+.zip")
results_file_regex = re.compile(r"\d{4}")


with open(TEST_SETS_DEFAULT_DIR / "old_new_ids_map.json") as fp:
    OLD_NEW_ID_MAP = json.load(fp)


def select_files_to_score(submissions_dir: Path, scored_files_dir: Path = SCORED_FILES_MEMORY_DIR, mail_file_path: Path = DEFAULT_MAIL_FILE_PATH, max_attempts_num: int = 3):
    scored_submissions_set = set(zip_path.name for zip_path in scored_files_dir.glob("**/*.zip"))
    teams_num_attempts_dict = _count_teams_attempts(scored_submissions_set)
    teams_df = pd.read_csv(mail_file_path)
    valid_email_addresses_set = set(teams_df['email'])
    files_to_score = list()
    for submission_email_path in submissions_dir.iterdir():
        team_leader_email = submission_email_path.name
        if team_leader_email not in valid_email_addresses_set:
            if team_leader_email != '.gitkeep':
                print(f"Team leader {team_leader_email} does not exist in the database {mail_file_path}")
            continue
        expected_team_name = teams_df[teams_df['email'] == team_leader_email]['team_name']
        if expected_team_name.empty:
            print(f"No team registered for the email address {team_leader_email}")
        expected_team_name = expected_team_name.iloc[0]
        if teams_num_attempts_dict.get(expected_team_name, 0) > max_attempts_num:
            print(f"Team leader '{team_leader_email}' of team '{expected_team_name}' already has a max of {max_attempts_num} submissions scored")
            continue
        for submission_path in submission_email_path.iterdir():
            _, team_name, _, attempt_num = submission_path.name.split('.')[0].split('_')
            if not _is_valid_submission_name(submission_path.name):
                print(f"Submission '{submission_path}' has invalid name")
                continue
            elif team_name != expected_team_name:
                print(f"Submission '{submission_path}' team name '{team_name}' not in the database '{mail_file_path}'")
                continue
            elif submission_path.name in scored_submissions_set:
                print(f"Submission already scored: Team {team_name} submission {submission_path.name} - {submission_path}")
                continue
            files_to_score.append((team_leader_email, team_name, attempt_num, submission_path))
    return files_to_score


def _is_valid_submission_name(file_name):
    return bool(file_check_regex.match(file_name))


def _count_teams_attempts(submissions_set):
    counter = dict()
    for submission_file_name in submissions_set:
        _, team_name, _, _ = submission_file_name.split('.zip')[0].split('_')
        counter.setdefault(team_name, 0)
        counter[team_name] += 1
    return counter


def get_submission_file_metadata(file_path):
    metadata_dict = dict()
    modification_time = file_path.stat().st_mtime
    stats = file_path.stat()
    metadata_dict.update(
        {
        "modification_time": modification_time,
        "dt": pd.to_datetime(modification_time, unit='s'),
        "stats": stats
        }
    )
    return metadata_dict


def unzip_file(zip_file_path, submission_name: str, return_submission_processing_path: bool = False, output_dir: Path =DEFAULT_PROCESSING_DIR):
    """
    """
    processing_path = output_dir / submission_name
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(processing_path)
    if return_submission_processing_path:
        return processing_path
    return None


def examine_submission_directory(submission_directory_path, full_test_set_path=full_test_set_path):
    for file_path in submission_directory_path.glob("**/*.csv"):
        relative_path = file_path.relative_to(submission_directory_path)
        if 'train' in str(relative_path):
            continue
        if not (full_test_set_path / relative_path).exists():
            print(f"{file_path} does not have a corresponding path in the {full_test_set_path}")
            return False
    return True


def save_results_to_csv(results_dict, save_dir, time_str=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")):
    scores_df = pd.DataFrame.from_dict(results_dict, orient='index')
    scores_df.index.name = "team_leader_email"
    validation_results_files = list(Path(save_dir).glob("*_validation_results.csv"))
    for validation_results_file in validation_results_files:
        store_dst = PREVIOUS_EVALUATIONS_DIR / validation_results_file.name
        shutil.move(validation_results_file, store_dst)
    scores_df.to_csv(Path(save_dir, f"{time_str}_validation_results.csv"))
