# 🚀 NetGuard AI — Hybrid Attention-Based Intrusion Detection System

<p align="center">
  <b>🔥 Real-Time AI-Based Intrusion Detection System 🔥</b><br>
  <i>Detect • Alert • Protect</i>
</p>

## 📌 Overview
NetGuard AI is an advanced AI-powered Intrusion Detection System (IDS) designed to detect malicious network traffic in both real-time and batch processing scenarios.

The system uses a Hybrid Attention-Based Machine Learning Model to identify cyber threats such as DDoS, PortScan, and other attacks with high accuracy, along with real-time alerts, dashboard monitoring, and automated email notifications.

## ❗ Problem Statement

With the rapid growth of networked systems and Software-Defined Networking (SDN), cyber threats such as DDoS attacks, port scanning, and brute-force attacks have become increasingly frequent and sophisticated. Traditional intrusion detection systems often rely on static rule-based methods, which struggle to detect evolving and unknown attack patterns in real time.

Additionally, many existing solutions lack:
- Real-time monitoring capabilities  
- Intelligent feature prioritization  
- Automated alerting mechanisms  
- Scalable and user-friendly interfaces  

This creates a critical need for an intelligent, automated, and real-time intrusion detection system that can accurately identify malicious network activities and provide immediate alerts to prevent potential damage.

Therefore, this project aims to develop a Hybrid Attention-Based Intrusion Detection System that leverages machine learning to detect network attacks efficiently, supports both batch and real-time data processing, and enhances security through automated alerting and monitoring.

## 🎯 Objectives

- To develop an intelligent intrusion detection system capable of identifying malicious network traffic with high accuracy.  

- To design and implement a hybrid attention-based machine learning model that prioritizes important features for improved detection performance.  

- To enable real-time monitoring of network traffic using WebSocket-based streaming.  

- To support batch processing of network logs through CSV upload for offline analysis.  

- To provide automated alert mechanisms, including email notifications, for rapid response to detected attacks.  

- To build a user-friendly backend system with secure authentication using JWT.  

- To visualize network traffic statistics and attack distribution through a dashboard.  

- To achieve high performance and reliability using the CICIDS dataset for training and evaluation.  
## 🎯 Key Features

- ⚡ Real-Time Intrusion Detection using WebSockets  
- 📂 Batch CSV Upload Analysis  
- 🧠 Hybrid Attention-Based Model (Feature Weighting + Neural Network)  
- 📊 Live Dashboard with Traffic & Attack Statistics  
- 🚨 Automated Email Alerts for Attacks  
- 🔐 JWT-Based Authentication System  
- 📥 Downloadable Prediction Reports (CSV)  
- 📈 High Accuracy (~98%) on CICIDS Dataset  

## 🧠 System Architecture:
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/32827152-56ec-4c68-acfc-86064d819e53" />

## 🛠️ Tech Stack

### 👨‍💻 Backend
- FastAPI  
- Python  
- WebSockets  

### 🤖 Machine Learning
- Scikit-learn  
- Gradient Boosting (Feature Importance)  
- MLP Classifier  

### 📊 Data Processing
- Pandas  
- NumPy  
- StandardScaler  
- LabelEncoder  

### 🔐 Security
- JWT Authentication  

### 📧 Alerts
- SMTP Email Integration

## 📊 Model Performance

| Metric      | Value   |
|------------|--------|
| Accuracy   | 98.07% |
| Precision  | 98.39% |
| Recall     | 98.07% |
| F1 Score   | 98.19% |

## OUTPUT:
### Login Page:
<img width="1903" height="966" alt="image" src="https://github.com/user-attachments/assets/7cee1151-fee1-4100-a58e-244cebc1a622" />
### Dashboard:
<img width="1911" height="968" alt="image" src="https://github.com/user-attachments/assets/a8ea79ad-5b4d-46ff-8604-ad9475a02653" />

### Batch Log Prediction:
<img width="1915" height="969" alt="image" src="https://github.com/user-attachments/assets/785e4743-d48b-4dee-8a50-46f496470ad4" />

### Real time data Monitoring:
<img width="1880" height="957" alt="image" src="https://github.com/user-attachments/assets/e52f9ee9-832f-420c-bf5a-cc7d3bef276b" />

### Alert Page:
<img width="1914" height="964" alt="image" src="https://github.com/user-attachments/assets/b8d97af4-539a-440c-b793-73af2753bd75" />
### Real-Time Email Alert for Batch log prediction:

<img width="1424" height="869" alt="image" src="https://github.com/user-attachments/assets/6fe67d1f-bbdc-4e0c-b3dc-4d8ac2e8f66a" />

### Real-Time Email Alert for Real time Monitoring:
<img width="1261" height="757" alt="image" src="https://github.com/user-attachments/assets/6346eaaf-0d4e-40f7-888c-a337e6aaf5da" />

## 📂 Features Usage
### 📌 CSV Upload
1.Upload network logs
2.Get attack predictions
### ⚡ Real-Time Monitoring
1.Stream traffic via WebSocket
2.Get instant predictions
### 🚨 Alerts
Email sent when attack detected
Includes:
Attack type
Confidence
Timestamp
## 💡 Use Cases
1.Network Security Monitoring
2.Enterprise Cybersecurity Systems
3.SDN Intrusion Detection
4.Real-Time Threat Detection
## 🔮 Future Enhancements
1.Database integration (MongoDB/PostgreSQL)
2.Docker deployment
3.Cloud deployment (AWS/GCP)
4.Deep Learning (LSTM/Transformer upgrade)

## 👩‍💻 Author
Harini V
B.Tech Artificial Intelligence & Data Science


