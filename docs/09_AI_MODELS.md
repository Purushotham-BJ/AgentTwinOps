# AI Models

---

# Objective

The AI layer predicts infrastructure behavior and assists administrators with proactive recommendations.

---

# AI Components

1. Prediction Engine

2. Anomaly Detection

3. Recommendation Engine

4. Infrastructure Health Scoring

---

# CPU Prediction

Inputs

- CPU History
- Request Rate
- Number of Containers

Outputs

Future CPU Utilization

Algorithms

- XGBoost
- Random Forest

The current implementation uses a CPU-based Random Forest regressor. It retrieves
historical CPU metrics through the backend metrics API and builds deterministic
four-point lag features (`t-4` through `t-1`) to predict the next value. At least
30 historical records are required. Responses include MAE, RMSE, and R² from the
current validation split; these are measurements, not accuracy claims.

---

# Memory Prediction

Inputs

- Historical Memory Usage
- Running Pods
- Active Sessions

Outputs

Future Memory Usage

Algorithms

- XGBoost

The memory implementation uses the same lag-feature pipeline and minimum history
requirement as CPU prediction.

---

# Failure Prediction

Inputs

CPU

Memory

Disk

Latency

Error Rate

Outputs

Failure Probability

Algorithms

Random Forest
Gradient Boosting

The current failure prediction is a deterministic operational heuristic based on
service health, incidents, and horizon context. It is not represented as a
supervised ML classifier and does not use fabricated training labels.

When history is below the configured minimum, CPU and memory predictions return
`INSUFFICIENT_DATA` with `prediction_source: none`. Unexpected model failures are
reported as `ERROR` with `prediction_source: fallback`; they are never reported
as successful ML predictions.

Successful CPU and memory predictions are sent through the backend Twin API and
persisted in `Twin.predicted_state`. `current_state` is not overwritten.

---

# Anomaly Detection

Purpose

Detect abnormal infrastructure behavior.

Examples

- Sudden CPU spike

- Memory Leak

- Container Restart Loop

Algorithms

Isolation Forest

One-Class SVM

---

# Recommendation Engine

Input

Prediction Results

Output

Infrastructure Recommendations

Examples

Scale replicas

Restart container

Increase resources

Investigate service

---

# Infrastructure Health Score

Formula

Health Score =

CPU Score +

Memory Score +

Latency Score +

Availability Score

Normalized to 100.

---

# Training Dataset

Sources

Prometheus Metrics

Generated Simulation Data

Historical Infrastructure Logs

---

# Model Evaluation

Metrics

Accuracy

Precision

Recall

F1 Score

MAE

RMSE

ROC-AUC

---

# Future Improvements

LSTM

Transformer Models

Reinforcement Learning

Federated Learning

Graph Neural Networks
