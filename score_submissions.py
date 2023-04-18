import pandas as pd
import numpy as np
import argparse
import shutil
from datetime import datetime
# from utils.scoring_utils import unzip
from utils.io_utils import select_files_to_score, unzip_file, examine_submission_directory, save_results_to_csv
from utils.scoring_utils import score_submission
from settings import DETAILED_SCORES_DIR, SCORED_FILES_MEMORY_DIR, DEFAULT_SUBMISSIONS_DIR, TEST_SETS_DEFAULT_DIR


# TODO default or provided via argument 
submissions_dir = DEFAULT_SUBMISSIONS_DIR
test_set_dir = TEST_SETS_DEFAULT_DIR / "final_test_set"
scoring_save_dir = "./"


if __name__ == "__main__":
    script_start_time_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    # select files to score from the submissions directory
    files_to_score = select_files_to_score(submissions_dir)
    # exit if nothing to score
    if not files_to_score:
        print("Nothing to score")
        exit()
    # iterate over selected files
    scoring_results_dict = dict()
    for team_leader_email, attempt_num, team_name, submission_path in files_to_score:
        # unzip the submission
        submission_processing_path = unzip_file(submission_path, team_leader_email, return_submission_processing_path=True)
        # prepare directory for results 
        submission_directory_path = submission_processing_path / "results"
        results_save_directory = SCORED_FILES_MEMORY_DIR / team_leader_email
        results_save_directory.mkdir(parents=True, exist_ok=True)
        # check if submission has proper structure - everything is in the "results" dir
        if not submission_directory_path.is_dir():
            print(f"Invalid submission structure: Team {team_name} submission {attempt_num} - {submission_path}")
            continue
        # check if submission has proper structure - iterate over all directories and files
        if not examine_submission_directory(submission_directory_path):
            print(f"Wrong structure of the submission directory: {submission_directory_path}")
            continue
        # score submissions
        print(f"Processing {submission_path}")
        scores_benedict = score_submission(submission_directory_path, test_set_dir)
        # compute end result
        end_avg_rmse = np.mean(list(scores_benedict['dimensions_level'].values()))
        scoring_results_dict.setdefault(team_leader_email, dict())
        scoring_results_dict[team_leader_email].setdefault("submission_name", submission_path.stem)
        scoring_results_dict[team_leader_email].setdefault("rmse", end_avg_rmse)
        # prepare directory to store results
        detailed_scores_path = DETAILED_SCORES_DIR / team_leader_email
        detailed_scores_path.mkdir(exist_ok=True)
        # create results file path and save results to .json file
        results_save_path = detailed_scores_path / (submission_path.stem + ".json")
        scores_benedict.to_json(filepath=results_save_path)
        # prepare directory to store original submission
        submission_store_dst = SCORED_FILES_MEMORY_DIR / submission_path.relative_to(submissions_dir)
        submission_store_dst.parent.resolve().mkdir(parents=True, exist_ok=True)
        # move .zip submission file to storage directory
        shutil.move(submission_path, submission_store_dst)
        # remove files extracted for processing
        shutil.rmtree(submission_processing_path)
    # save results
    save_results_to_csv(scoring_results_dict, scoring_save_dir, script_start_time_str)

# for zipfile_path in submissions_dir.glob("*.zip"):
#     print(get_submission_file_metadata(zipfile_path))
    
    # check_if_valid_team("freedom.kangaroo@us.com")


# parser = argparse.ArgumentParser(description="Process submission for EPiC 2023 competition")
# parser.add_argument('--force', help='force scoring if anything is blocking it')
# parser.add_argument('--final', help='if final scoring done on the whole test set')
# parser.add_argument('--', help='')

# parser.add_argument('--sum', dest='accumulate', action='store_const',
#                     const=sum, default=max,
#                     help='sum the integers (default: find the max)')

# args = parser.parse_args()
# print(args.accumulate(args.integers))

