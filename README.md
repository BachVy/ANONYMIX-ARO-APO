# 🛡️ ANONYMIX: Hybrid ARO-APO Optimization for Data Anonymization

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/Framework-Streamlit-red" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/ML-RandomForest-green" alt="RandomForest"/>
  <img src="https://img.shields.io/badge/Optimization-ARO--APO-purple" alt="ARO-APO"/>
  <img src="https://img.shields.io/badge/Status-Research-success" alt="Research"/>
  <img src="https://img.shields.io/badge/License-Academic-lightgrey" alt="License"/>
</p>

<p align="center">
  <h1>Privacy vs Utility — Optimized by Hybrid Swarm Intelligence</h1>
</p>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Motivation](#-motivation)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [System Workflow](#-system-workflow)
- [Installation](#-installation)
- [Usage](#-usage)
- [Experiments](#-experiments)
- [Results](#-results)
- [Dataset](#-dataset)
- [Reproducibility](#-reproducibility)
- [Contributing](#-contributing)
- [License](#-license)
- [Citation](#-citation)
- [Acknowledgements](#-acknowledgements)
- [Author](#-author)
- [Future Work](#-future-work)

---

## 🔍 Overview

**ANONYMIX** is a research platform for **privacy-preserving data publishing (PPDP)**, specifically designed to solve the critical trade-off between:

- 🔒 **Privacy:** Protecting individual identities and sensitive information.
- 📊 **Utility:** Maintaining the analytical value and accuracy of the data.

The system pioneers a hybrid meta-heuristic optimization model combining **Artificial Rabbits Optimization (ARO)** for global exploration and **Arctic Puffins Optimization (APO)** for deep exploitation to find the most efficient Generalization Levels.

---

## 💡 Motivation

Traditional data anonymization methods often suffer from:
- **High Information Loss:** Resulting in data that is no longer useful for research.
- **Weak Utility:** Poor performance when used in Machine Learning models.
- **Vulnerability:** Susceptibility to Background Knowledge and Skewness attacks.

**ANONYMIX** addresses these issues by integrating **Swarm Intelligence Optimization** with **Real-time Machine Learning Evaluation**.

---

## 🚀 Key Features

- **Hybrid ARO-APO Engine:** Uses Levy Flight and adaptive strategies to prevent local optima.
- **Advanced Privacy Models:** Implements $k$-Anonymity and Recursive $(c,l)$-Diversity.
- **Utility-Aware Fitness:** Uses Random Forest Classifier Accuracy as a primary fitness component.
- **Synthetic Generator:** Creates 50,000+ medical records with hierarchies up to 7 levels deep.
- **Interactive Dashboard:** Built with Streamlit for trial management and log-scale convergence tracking.

---

## 🏗️ Architecture

```
📂 ANONYMIX_PROJECT
├── 📂 data/                   # Dataset & Ontology Management
│   ├── 📂 adult/, 📂 cmc/ ... # Benchmark Datasets
│   └── 📂 medical/            # Synthetic Medical Data
│       ├── 📂 hierarchies/    # Hierarchy CSV files
│       ├── medical.csv        # Raw dataset
│       ├── medical_train.txt  # Training indices
│       └── medical_test.txt   # Test indices
├── 📂 pages/                  # Streamlit Multi-page UI
├── 📂 results/                # CSV Logs & Generated Plots
├── app.py                     # Main Entry Point
├── aro_apo_optimizer.py       # Core Hybrid Algorithm
├── anonymizer.py              # K-Anonymity & L-Diversity Logic
├── classifier.py              # Utility Evaluation (Random Forest)
├── config.py                  # System & Fitness Parameters
├── run_parallel.py            # Multiprocessing trial engine
└── visualize.py               # Research-grade plotting engine
```
## ⚙️ System Workflow
### Optimization Function
The system evaluates each potential anonymization strategy using the following objective function:
$$Fitness = w \cdot InfoLoss + u \cdot ViolationPenalty + v \cdot (1 - Accuracy)$$

### Pipeline
1. Preprocessing: Load raw data and Domain Ontologies (Hierarchies).
2. Hybrid Search: ARO-APO explores the space of generalization levels.
3. Validation: Each candidate is checked for privacy violations and ML accuracy.
4. Aggregation: Results are compiled into Master Reports with mean and standard deviation.

---
## 💻 Installation
### Requirements
- Python: 3.9+
- RAM: ≥ 8GB (Recommended for parallel processing)
- OS: Windows / Linux / macOS

### Setup
```
# Clone the repository
git clone [https://github.com/your-username/anonymix.git](https://github.com/your-username/anonymix.git)
cd anonymix

# Install dependencies
pip install -r requirements.txt
```
---
## ▶️ Usage
### Start the Dashboard
```
streamlit run app.py
```
Then open your browser at http://localhost:8501.

### Command Line Execution
To run experiments for all datasets in batch mode:
```
python run_batch.py
```
---
## 🧪 Experiments
- Total Datasets: 7 (Adult, California Housing, CMC, INFORMS, Italia, MGM, Medical).
- Trials per Algorithm: 30+ iterations to ensure statistical stability.
- Comparative Baseline: Genetic Algorithm (GA) and Particle Swarm Optimization (PSO).
---
## 📊 Results
### 📈 Convergence Comparison
- ARO-APO demonstrates significantly faster convergence than GA and PSO.
- Achieves lower (better) final fitness values across 90% of test cases.
### 📋 Benchmark Table (Summary)

| Algorithm | Fitness ↓ | Accuracy ↑ | Stability |
|----------|----------|------------|-----------|
| ARO-APO  | Lowest   | Highest    | High      |
| GA       | Medium   | Medium     | Medium    |
| PSO      | Good     | Good       | Medium    |
---
## 📂 Datasets
The project includes a comprehensive data suite located in /data/:
- Standard Benchmarks: Adult, Italia, CMC, MGM, etc.
- Custom Data: Synthetic Medical Dataset with 50,000 records.
---
## 🤝 Contributing
1. Fork the Project.
2. Create your Feature Branch (git checkout -b feature/AmazingFeature).
3. Commit your Changes (git commit -m 'Add some AmazingFeature').
4. Push to the Branch (git push origin feature/AmazingFeature).
5. Open a Pull Request.
---
## ⚖️ License
This project is licensed for Academic and Research Use Only.

Users must comply with:
- Decree 13/2023/NĐ-CP (Vietnam Personal Data Protection)
- GDPR (General Data Protection Regulation)
---
## 👨‍💻 Author
### HUIT Research Team
- Lead Developer: [Your Name/Team Member Name]
- Contact: bachngocvy25112005@gmail.com
---
## 🌟 Future Work
- Integration of Deep Learning (Autoencoders) for utility metrics.
- Implementation of Differential Privacy as an additional security layer.
- Development of a SaaS API for real-world healthcare application deployment.