# WHOOP Recovery Predictor
Project in active development.

Predicting next-day recovery score from ~900 nights of personal WHOOP data.
An n-of-1 study testing whether population-level exercise-science findings
hold at the individual level.

## Overview
The aim of the project is to create a tool which predicts the next day recovery score based on the current days biological data extracted from the users WHOOP device with clear explainability of the drivers of the expected recovery.
The use case for this is to act as an evening planning tool to help the user deliberately adapt the next days training session based on expected recovery to reduce risk of injury whilst also delivering an optimal exercise stimulus to improve overall Health and Physical fitness.

## Data
- Source: personal WHOOP export → Supabase (recovery, sleep, cycle/strain tables)
- ~900 nights, naps excluded
- Pipeline: github.com/JordanPickles/whoop-pipeline

## Method
- Target: recovery_tomorrow (recovery_score shifted −1 day)
- Temporal 70/30 split, 7-day embargo matching rolling-window length (leakage control)
- Baselines: mean predictor (RMSE 20.33), persistence (RMSE 27.20 — worse than mean,
  reflecting near-zero lag-1 autocorrelation of 0.095)
- Models: Linear Regression, LASSO, XGBoost with TimeSeriesSplit CV
- SHAP values and explainability
- Leakage discipline: value imputation fit inside pipelines, per-fold

## Status / Roadmap
Project in active development.

Done:
- [x] Data pipeline (WHOOP → Supabase)
- [x] Feature engineering (temporal, sleep timing, rolling trends, sleep debt)
- [x] Baseline benchmarks (mean predictor, persistence)
- [x] Model comparison: Linear Regression, LASSO, XGBoost
- [x] Bias-variance analysis across models
- [x] SHAP feature attribution (XGBoost) delivering the driver-of-recovery analysis and explainability

In progress / planned:
- [ ] Model Training transfered from .ipynb into .py files
- [ ] Finish the creation of predicted sleep consistency
- [ ] Streamlit app for inference (evening planning tool) | Current prototype but requires inputted planned sleep scores and deployment
- [ ] Write-up: key findings
