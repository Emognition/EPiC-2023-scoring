# EPiC 2023 scoring repository
## 1. Repository preparation
To run the code in the repo you need python (tested on python 3.10) and libraries from the requirements.txt file.

We recommend using a conda environment with Python >= 3.10 (you can also use standard python, it's just that we tested it using conda).

You can get conda (we recommend miniconda) from [anaconda project website](https://docs.conda.io/en/latest/miniconda.html)

To create the conda environment named `epic_scoring` and activate it, run the following code. Omit this step of you don't need separate environment.
```
conda create -n epic_scoring python=3.10
conda activate epic_scoring
```

To run the code you need libraries that do not come preinstalled. To install them run:

```
pip install -r requirements.txt
```

## 2. Scoring submissions
Submissions will be scored only if the following conditions are met:
1. `.zip` files with submission must be put in directories named the same as team leaders' emails, either in `submissions_to_score` directory (for validation scoring) or `FINAL_SUBMISSIONS` (for final scoring), e.g., `submissions_to_score/bart@emognition.com/EPiC23_TestTeam_Attempt_1.zip`
2. Team leader and team name must be present in the respective columns in emails_teams.csv file, e.g., `bart@emognition.com, TestTeam` 

If the above conditions are present, run the `score_submissions.py` script, using one of the following:

For validation scoring (attempts scored on half of the test set, during the competition)
```
python score_submissions.py
```

For final scoring (after the end of the competition)
```
python score_submissions.py --final
```

Results are be saved in the `.csv` file in the root of the repository, named either `<timestamp>_validation_results.csv` for validation scoring, or `<timestamp>_final_results.csv` for final test scoring. At the same time, logs from processing are be saved in the `<timestamp>_processing_logs.csv`. If any old files with results or logs are present in the root of the repo, they will be moved to the `storage/previous_evaluarions` or `storage/previous_logs` respectively.

After the processing, scored submissions are moved from `submissions_to_score` to the `storage/scored_submissions` directory.