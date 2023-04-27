from benedict import benedict
from pathlib import Path
from settings import DETAILED_SCORES_DIR, PROJECT_DIR
import numpy as np

detailed_scores_path = DETAILED_SCORES_DIR / "final"
scores_with_stds = PROJECT_DIR / "scores_with_stds"

for scores_file in detailed_scores_path.glob("**/*.json"):
    scores_parent = scores_file.parent.resolve()
    scores_save_dir = scores_with_stds / scores_parent.relative_to(detailed_scores_path)
    scores_save_dir.mkdir(parents=True, exist_ok=True)
    scores_benedict = benedict.from_json(scores_file)
    files_scores = scores_benedict['files_level']
    scoring_benedict = benedict()
    results_benedict = benedict()
    for scenario in ["scenario_1", "scenario_2", "scenario_3", "scenario_4"]:
        scenario_benedict = files_scores[scenario]
        scoring_benedict[scenario] = benedict()
        for flat_keypath in scenario_benedict.flatten(separator="/"):
            split_keypath = flat_keypath.split("/")
            keypath = files_scores.keypath_separator.join(split_keypath)
            if scenario == "scenario_1":
                _, affect_dim = split_keypath
                scoring_benedict[scenario].setdefault(affect_dim, list())
                scoring_benedict[scenario, affect_dim].append(scenario_benedict[keypath])
            else:
                fold, _, affect_dim = split_keypath
                scoring_benedict[scenario].setdefault(fold, benedict())
                scoring_benedict[scenario, fold].setdefault(affect_dim, list())
                scoring_benedict[scenario, fold, affect_dim].append(scenario_benedict[keypath])
    folds_benedict = scores_benedict['folds_level']
    for scenario in ["scenario_2", "scenario_3", "scenario_4"]:
        scenario_benedict = folds_benedict[scenario]
        for flat_keypath in scenario_benedict.flatten(separator="/"):
            split_keypath = flat_keypath.split("/")
            keypath = files_scores.keypath_separator.join(split_keypath)
            _, affect_dim = split_keypath
            scoring_benedict[scenario].setdefault(affect_dim, list())
            scoring_benedict[scenario, affect_dim].append(scenario_benedict[keypath])
    for keypath in scoring_benedict.keypaths():
        if not isinstance(scoring_benedict[keypath], list):
            continue
        std_score = np.std(scoring_benedict[keypath])
        avg_score = np.mean(scoring_benedict[keypath])
        if 'fold' in keypath:
            results_benedict['folds_level', keypath, 'rmse'] = avg_score
            results_benedict['folds_level',keypath, 'std'] = std_score
            continue
        elif "scenario_1" in keypath:
            results_benedict['folds_level', keypath, 'rmse'] = avg_score
            results_benedict['folds_level',keypath, 'std'] = std_score
        results_benedict['scenarios_level', keypath, 'rmse'] = avg_score
        results_benedict['scenarios_level',keypath, 'std'] = std_score
    results_benedict['files_level'] = scores_benedict['files_level']
    results_benedict.to_json(filepath = scores_save_dir / scores_file.name)
