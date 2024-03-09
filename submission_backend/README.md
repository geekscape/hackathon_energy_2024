## Testing evaluation

`python submission_backend/dock.py` will run the current algorithm in a docker container and save the output to `submisison_backend/cruft/output.json`. As long as this works we know that the submission backend will be able to run this algorithm successfully. 

## Submission Schema

The schema for participant data saved to the public dynamodb database is given below.

```json
{
    "main_trial_idx": 0.0,
    "std_profit": 63.258054731668594,
    "error_traceback": null,
    "main_trial": {
        "profits": [
            -7.979027700261019,
            3.5329587136597684,
        ],
        "socs": [
            53.75,
            49.120370370370374,
            52.870370370370374,
        ],
        "start_step": 0.0,
        "market_prices": [
            34.14524892893011,
            23.603033351187605,
        ],
        "actions": [
            50.0,
            -50.0,
        ],
        "episode_length": 289.0
    },
    "status": "success",
    "class_name": "RandomPolicy",
    "score": 69.92687885964213,
    "submitted_at": 1709940984995.0,
    "num_runs": 100.0,
    "parameters": {},
    "team": "scream-team",
    "error": null,
    "mean_profit": 69.92687885964213,
    "commit_hash": "098fffa0-bf29-45ef-81c8-b10d72aa62e2"
}
```

An example database in JSON format is given in `data/example_db.json`.

In addition more data will be saved to the private database. The main differnce between the public and the private database is that it may contain an additional `"trails"` key which may be an arrray containing tens or hundreds of trials in the exact same format as `"main_trial"`. This will likely be saved as individual JSON files each named `TEAM_NAME-COMMIT_HASH` since dynamodb can only handle 400k of data per item and 100 trials will be far larger than this amount.