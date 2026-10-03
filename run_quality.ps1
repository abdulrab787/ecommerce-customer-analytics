# Windows one-click: run tests, experiment readouts and the DQ gate
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m src.experimentation.simulate
python -m src.experimentation.decide
python -m src.data_quality.runner --config config/dq_rules.yml
Write-Host "Reports in reports\dq and reports\experiments"
