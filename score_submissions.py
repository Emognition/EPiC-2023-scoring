import pandas as pd
import numpy as np
import argparse
import os
import shutil
from benedict import benedict
from pathlib import Path
from tqdm import tqdm
# from utils.scoring_utils import unzip
from utils.io_utils import select_files_to_score, unzip_file, examine_submission_directory
from settings import PROJECT_DIR, DEFAULT_PROCESSING_DIR, DETAILED_SCORES_DIR, SCORED_FILES_MEMORY_DIR, DEFAULT_SUBMISSIONS_DIR, TEST_SETS_DEFAULT_DIR
from sklearn.metrics import mean_squared_error


# TODO default or provided via argument 
submissions_dir = DEFAULT_SUBMISSIONS_DIR
test_set_dir = TEST_SETS_DEFAULT_DIR / "final_test_set"


if __name__ == "__main__":
    files_to_score = select_files_to_score(submissions_dir)
    if not files_to_score:
        print("Nothing to score")
        exit()
    for team_leader_email, attempt_num, team_name, submission_path in files_to_score:
        submission_results_storage = benedict()
        submission_processing_path = unzip_file(submission_path, team_leader_email, return_submission_processing_path=True)
        submission_directory_path = submission_processing_path / "results"
        results_save_directory = SCORED_FILES_MEMORY_DIR / team_leader_email
        results_save_directory.mkdir(parents=True, exist_ok=True)
        if not submission_directory_path.is_dir():
            print(f"Invalid submission structure: Team {team_name} submission {attempt_num} - {submission_path}")
            continue
        if not examine_submission_directory(submission_directory_path):
            print(f"Wrong structure of the submission directory: {submission_directory_path}")
            continue
        print(f"Scoring submission {submission_path}")
        for test_file_path in tqdm(test_set_dir.glob("**/*.csv")):
            relative_file_path = test_file_path.relative_to(test_set_dir)
            prediction_path = submission_directory_path / relative_file_path
            test_scores = pd.read_csv(test_file_path)
            prediction_scores = pd.read_csv(prediction_path)
            if len(prediction_scores) != len(test_scores):
                print(f"Length of predictions ({len(prediction_scores)} samples) does not match length of test file ({len(test_scores)} samples)")
                break
            elif 'arousal' not in prediction_scores.columns or 'valence' not in prediction_scores.columns:
                print(f"Missing at least on of arousal/valence columns {prediction_path}")
                break
                # throw error here?
            file_rmse_arousal = np.sqrt(mean_squared_error(test_scores['arousal'].to_numpy(), prediction_scores['arousal'].to_numpy()))
            file_rmse_valence = np.sqrt(mean_squared_error(test_scores['valence'].to_numpy(), prediction_scores['valence'].to_numpy()))
            if len(x := str(relative_file_path).split(os.sep)) == 4:
                scenario, _, _, file_name = x
                submission_results_storage[scenario, file_name, "arousal"] = file_rmse_arousal
                submission_results_storage[scenario, file_name, "valence"] = file_rmse_valence
            elif len(x) == 5:
                scenario, fold, _, _, file_name = x
                submission_results_storage[scenario, fold, file_name, "arousal"] = file_rmse_arousal
                submission_results_storage[scenario, fold, file_name, "valence"] = file_rmse_valence
        detailed_scores_path = DETAILED_SCORES_DIR / team_leader_email
        detailed_scores_path.mkdir(exist_ok=True)
        results_save_path = detailed_scores_path / str(submission_path.name).replace(".zip", ".json")
        submission_results_storage.to_json(filepath=results_save_path)
        submission_store_dst = SCORED_FILES_MEMORY_DIR / submission_path.relative_to(submissions_dir)
        submission_store_dst.parent.resolve().mkdir(parents=True, exist_ok=True)
        shutil.move(submission_path, submission_store_dst)
        shutil.rmtree(submission_processing_path)


        # at the end cp zip file and rm it from submissions

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

