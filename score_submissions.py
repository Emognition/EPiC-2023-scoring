from datetime import datetime
from utils.io_utils import select_files_to_score, unzip_file, examine_submission_directory, save_results_to_csv, move_logs
from utils.scoring_utils import score_submission
from settings import PROJECT_DIR, DETAILED_SCORES_DIR, SCORED_FILES_STORAGE_DIR, DEFAULT_SUBMISSIONS_DIR, TEST_SETS_DEFAULT_DIR, FINAL_SUBMISSIONS_DIR, DEFAULT_LOGGING_STORAGE_DIR
import numpy as np
import argparse
import shutil
import logging
import sys


parser = argparse.ArgumentParser(description="Process submissions for EPiC 2023 competition")
parser.add_argument('-f', '--final', action='store_true', help='if final scoring - done on the whole test set')
args = parser.parse_args()


logging_dir = DEFAULT_LOGGING_STORAGE_DIR / ("final" if args.final else "trial")
submissions_dir = FINAL_SUBMISSIONS_DIR if args.final else DEFAULT_SUBMISSIONS_DIR
test_set_dir = TEST_SETS_DEFAULT_DIR / ("final_test_set" if args.final else "trial_test_set")
scored_files_memory_dir = SCORED_FILES_STORAGE_DIR / ("final" if args.final else "trial")
detailed_scores_memory_dir = DETAILED_SCORES_DIR / ("final" if args.final else "trial")

scoring_save_dir = "./"

if __name__ == "__main__":
    script_start_time_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    logging_file_path = PROJECT_DIR / f"{script_start_time_str}_processing_logs.log"
    move_logs(PROJECT_DIR)
    logging.basicConfig(filename=logging_file_path, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.info("FINAL PROCESSING" if args.final else "Trial processing")
    # select files to score from the submissions directory
    files_to_score = select_files_to_score(submissions_dir, logger, scored_files_memory_dir, is_final=args.final)
    # exit if nothing to score
    if not files_to_score:
        # print("Nothing to score")
        logger.info("Nothing to score")
        exit()
    # iterate over selected files
    scoring_results_dict = dict()
    for team_leader_email, attempt_num, team_name, submission_path in files_to_score:
        # unzip the submission
        # submission_processing_path = output_dir / team_leader_email
        # if args.final and submission_path.is_dir():
        #     shutil.copy(submission_path)
        # else:
        submission_processing_path = unzip_file(submission_path, team_leader_email, return_submission_processing_path=True)
        # prepare directory for results 
        submission_directory_path = submission_processing_path / "results"
        # check if submission has proper structure - everything is in the "results" dir
        if not submission_directory_path.is_dir():
            # print(f"Invalid submission structure: Team {team_name} submission {attempt_num} - {submission_path}")
            logger.error(f"Invalid submission structure: Team {team_name} submission {attempt_num} - {submission_path}")
            continue
        # check if submission has proper structure - iterate over all directories and files
        if not examine_submission_directory(submission_directory_path, logger=logger):
            # print(f"Wrong structure of the submission directory: {submission_directory_path}")
            logger.error(f"Wrong structure of the submission directory: {submission_directory_path}")
            continue
        # score submissions
        # print(f"Processing {submission_path}")
        logger.info(f"Processing {submission_path}")
        scores_benedict = score_submission(submission_directory_path, test_set_dir)
        # compute end result
        end_avg_rmse = np.mean(list(scores_benedict['dimensions_level'].values()))
        scoring_results_dict.setdefault(team_leader_email, dict())
        scoring_results_dict[team_leader_email].setdefault("submission_name", submission_path.stem)
        scoring_results_dict[team_leader_email].setdefault("rmse", end_avg_rmse)
        logger.info(f"Submission {submission_path} avg rmse: {end_avg_rmse}")
        # prepare directory to store results
        detailed_scores_path = detailed_scores_memory_dir / team_leader_email
        detailed_scores_path.mkdir(parents=True, exist_ok=True)
        # create results file path and save results to .json file
        results_save_path = detailed_scores_path / (submission_path.stem + ".json")
        scores_benedict.to_json(filepath=results_save_path)
        # prepare directory to store original submission
        submission_store_dst = scored_files_memory_dir / submission_path.relative_to(submissions_dir)
        submission_store_dst.parent.resolve().mkdir(parents=True, exist_ok=True)
        # move .zip submission file to storage directory
        shutil.move(submission_path, submission_store_dst)
        # remove files extracted for processing
        shutil.rmtree(submission_processing_path)
    # save results
    save_results_to_csv(scoring_results_dict, scoring_save_dir, script_start_time_str, is_final=args.final)
