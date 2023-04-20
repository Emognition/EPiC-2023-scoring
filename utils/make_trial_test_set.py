from benedict import benedict
from settings import TEST_SETS_DEFAULT_DIR
import os
import pandas as pd
import numpy as np
import shutil

final_test_path = TEST_SETS_DEFAULT_DIR / "final_test_set"
trial_test_path = TEST_SETS_DEFAULT_DIR / "trial_test_set"


if __name__ == "__main__":
    paths_storage = benedict()
    subjects_storage = benedict()
    videos_storage = benedict()
    scenarios_folds_set = set()
    for file_path in sorted(final_test_path.glob("**/*.csv")):
        relative_path = file_path.relative_to(final_test_path)
        relative_spl = str(relative_path).split(os.sep)
        scenario, fold = relative_spl[:2]
        name = relative_path.stem
        _, sub, _, vid = name.split("_")
        if 'fold' not in fold:
            fold = '*'
        scenarios_folds_set.add((scenario, fold))
        paths_storage[scenario, fold, sub, vid] = relative_path
        subjects_storage.setdefault(scenario, dict())
        subjects_storage[scenario].setdefault(fold, set())
        subjects_storage[scenario, fold].add(sub)
        videos_storage.setdefault(scenario, dict())
        videos_storage[scenario].setdefault(fold, set())
        videos_storage[scenario, fold].add(vid)
    trial_test_paths = benedict()
    for scenario, fold_name in sorted(scenarios_folds_set):
        rng = np.random.default_rng(seed=[2023, 2024])
        subjects_permutation = rng.permutation(sorted(list(subjects_storage[scenario, fold_name])))
        videos_permutation = rng.permutation(sorted(list(videos_storage[scenario, fold_name])))
        trial_test_paths[scenario, fold_name] = list()
        for subject in subjects_permutation:
            for video in videos_permutation[:len(videos_permutation)//2]:
                trial_test_paths[scenario, fold_name].append(paths_storage[scenario, fold_name, subject, video])
            videos_permutation = np.roll(videos_permutation, 2)
    for keypath in trial_test_paths.keypaths():
        paths_list_maybe = trial_test_paths[keypath]
        if not isinstance(paths_list_maybe, list):
            continue
        for relative_path in paths_list_maybe:
            dst_path = trial_test_path / relative_path
            dst_path.parent.resolve().mkdir(parents=True, exist_ok=True)
            shutil.copy(final_test_path / relative_path, trial_test_path / relative_path)
