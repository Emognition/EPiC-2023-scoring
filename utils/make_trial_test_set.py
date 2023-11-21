from benedict import benedict
from settings import TEST_SETS_DEFAULT_DIR
import os
import pandas as pd
import numpy as np
import shutil

final_test_path = TEST_SETS_DEFAULT_DIR / "final_test_set"
trial_test_path = TEST_SETS_DEFAULT_DIR / "trial_test_set"


if __name__ == "__main__":
    # prepare data storing
    paths_storage = benedict()
    subjects_storage = benedict()
    videos_storage = benedict()
    scenarios_folds_set = set()
    trial_test_paths = benedict()
    # for file in test set
    for file_path in sorted(final_test_path.glob("**/*.csv")):
        # get relative path
        relative_path = file_path.relative_to(final_test_path)
        # split it into parts
        relative_spl = str(relative_path).split(os.sep)
        # get scenario and fold
        scenario, fold = relative_spl[:2]
        # get file name
        name = relative_path.stem
        _, sub, _, vid = name.split("_")
        # if scenario 1
        if 'fold' not in fold:
            fold = '*'
        # add file to processing set
        scenarios_folds_set.add((scenario, fold))
        # add relative path to storage
        paths_storage[scenario, fold, sub, vid] = relative_path
        # add subject to subjects set
        subjects_storage.setdefault(scenario, dict())
        subjects_storage[scenario].setdefault(fold, set())
        subjects_storage[scenario, fold].add(sub)
        videos_storage.setdefault(scenario, dict())
        # add video to videos set
        videos_storage[scenario].setdefault(fold, set())
        videos_storage[scenario, fold].add(vid)
    # for fold in folds set
    for scenario, fold_name in sorted(scenarios_folds_set):
        # permute subjects and videos
        rng = np.random.default_rng(seed=[2023, 2024])
        subjects_permutation = rng.permutation(sorted(list(subjects_storage[scenario, fold_name])))
        videos_permutation = rng.permutation(sorted(list(videos_storage[scenario, fold_name])))
        trial_test_paths[scenario, fold_name] = list()
        # for each subject
        for subject in subjects_permutation:
            # for the first half of videos
            for video in videos_permutation[:len(videos_permutation)//2]:
                # save subject video data path to trial test set
                trial_test_paths[scenario, fold_name].append(paths_storage[scenario, fold_name, subject, video])
            # shift videos by 2 so next subject has slightly different videos
            videos_permutation = np.roll(videos_permutation, 2)
    # copy items that we want to trial test set
    for keypath in trial_test_paths.keypaths():
        paths_list_candidate = trial_test_paths[keypath]
        if not isinstance(paths_list_candidate, list):
            continue
        for relative_path in paths_list_candidate:
            dst_path = trial_test_path / relative_path
            dst_path.parent.resolve().mkdir(parents=True, exist_ok=True)
            shutil.copy(final_test_path / relative_path, trial_test_path / relative_path)
