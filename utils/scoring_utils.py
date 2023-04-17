from sklearn.metrics import mean_squared_error
from tqdm import tqdm
from benedict import benedict
import numpy as np
import pandas as pd
import os


def score_submission(submission_directory_path, test_set_dir):
    # prepare storage benedict for currently processed submission
    per_file_results_benedict = benedict()
    print(f"Scoring submission")
    # iterate over all .csv in the test dir
    for test_file_path in tqdm(test_set_dir.glob("**/*.csv")):
        # get relative file path and get the same file from submission dir
        relative_file_path = test_file_path.relative_to(test_set_dir)
        prediction_path = submission_directory_path / relative_file_path
        # load files
        test_scores = pd.read_csv(test_file_path)
        prediction_scores = pd.read_csv(prediction_path)
        # check if file has all predictions
        if len(prediction_scores) != len(test_scores):
            print(f"Length of predictions ({len(prediction_scores)} samples) does not match length of test file ({len(test_scores)} samples)")
            break
        elif 'arousal' not in prediction_scores.columns or 'valence' not in prediction_scores.columns:
            print(f"Missing at least on of arousal/valence columns {prediction_path}")
            break
            # throw error here?
        # compute rmse for arousal and valence separately
        file_rmse_arousal = np.sqrt(mean_squared_error(test_scores['arousal'].to_numpy(), prediction_scores['arousal'].to_numpy()))
        file_rmse_valence = np.sqrt(mean_squared_error(test_scores['valence'].to_numpy(), prediction_scores['valence'].to_numpy()))
        # save results in memory
        # scenario 1 - no folds
        if len(x := str(relative_file_path).split(os.sep)) == 4: 
            scenario, _, _, file_name = x
            file_name = file_name.replace(".csv", "")
            per_file_results_benedict[scenario, file_name, "arousal"] = file_rmse_arousal
            per_file_results_benedict[scenario, file_name, "valence"] = file_rmse_valence
        # other scenarios - folds
        elif len(x) == 5:
            scenario, fold, _, _, file_name = x
            file_name = file_name.replace(".csv", "")
            per_file_results_benedict[scenario, fold, file_name, "arousal"] = file_rmse_arousal
            per_file_results_benedict[scenario, fold, file_name, "valence"] = file_rmse_valence
    print("Computing average results per fold")
    per_fold_results_benedict = compute_averaged_results(per_file_results_benedict, level="files")
    print("Computing average results per scenario")
    per_scenario_results_benedict = compute_averaged_results(per_fold_results_benedict, level="folds")
    print("Computing average results per dimension")
    per_dimension_results_benedict = compute_averaged_results(per_scenario_results_benedict, level="scenarios")
    return_benedict = benedict()
    return_benedict["files_level"] = per_file_results_benedict
    return_benedict["folds_level"] = per_fold_results_benedict
    return_benedict["scenarios_level"] = per_scenario_results_benedict
    return_benedict["dimensions_level"] = per_dimension_results_benedict
    return return_benedict


def compute_averaged_results(results_benedict: benedict, level: str):
    "Compute average score at second to last level (dict key). Assumes last level is arousal/valence."
    return_benedict = benedict()
    # assert level is correctrly specified
    assert level in {"scenarios", "folds", "files"}, "Specify level - one of {'scenarios', 'folds', 'files'}"
    # compute max keypath len and check if level is 'folds' - so later when averaging folds we don't average scenario 1
    keypath_max_len = max(map(lambda x: len(x.split(results_benedict.keypath_separator)), results_benedict.keypaths()))
    is_level_folds = (level == 'folds')
    save_keypath_len_dict = dict()
    for keypath in results_benedict.keypaths():
        # split keypath so we can retrieve info from it
        keypath_split = keypath.split(results_benedict.keypath_separator)
        # if averaging between folds level just save scenario 1 - it has shorter keypaths and is already on scenario level
        # if not a number
        if isinstance(results_benedict[keypath], benedict):
            continue
        elif is_level_folds and (len(keypath_split) < keypath_max_len):
            return_benedict[keypath] = results_benedict[keypath]
            continue
        # create save keypath removing second to last key
        save_keypath = results_benedict.keypath_separator.join(keypath_split[:-2] + [keypath_split[-1]])
        # sum results and their count
        return_benedict.setdefault(save_keypath, 0)
        return_benedict[save_keypath] += results_benedict[keypath]
        save_keypath_len_dict.setdefault(save_keypath, 0)
        save_keypath_len_dict[save_keypath] += 1
    # average stored results
    for keypath, num_samples in save_keypath_len_dict.items():
        return_benedict[keypath] /= num_samples
    # return benedict with results
    return return_benedict
