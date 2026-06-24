<p align="center">
  <img src="https://img.shields.io/badge/Ecommerce%20Customer%20Analytics-Power%20BI%20%7C%20SQL%20%7C%20Python-005B96?style=for-the-badge&logo=powerbi&logoColor=white" />
</p>

<h1 align="center">📊 Ecommerce Customer Analytics — End‑to‑End BI & Data Science Project</h1>

<p align="center">
  <b>Marketing Analytics • RFM Segmentation • Churn Prediction • CLV Modeling • Profitability • Power BI Dashboard</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Power%20BI-Dashboard-FFB900?style=flat-square&logo=powerbi&logoColor=black" />
  <img src="https://img.shields.io/badge/Python-Data%20Science-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/SQL-Analytics-CC2927?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/DAX-Semantic%20Model-00A98F?style=flat-square&logo=microsoft&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Completed-2ECC71?style=flat-square" />
</p>

<p align="center">
  <i>Built with enterprise BI standards — clean semantic model, version‑controlled DAX, ML‑powered insights, and a 5‑page interactive Power BI dashboard.</i>
</p>

# 📊 **Ecommerce Customer Analytics — End‑to‑End Data & BI Project**

A complete analytics solution combining **SQL**, **Python**, **Machine Learning**, and **Power BI** to analyze ecommerce customer behavior, marketing performance, churn risk, profitability, and customer lifetime value.

This project follows a **full data lifecycle**:

✔ Data ingestion  
✔ SQL-based exploration  
✔ Python-based modeling  
✔ RFM segmentation  
✔ Churn prediction  
✔ CLV estimation  
✔ Power BI dashboarding  
✔ Semantic modeling & DAX  
✔ Business storytelling  

Built using **enterprise BI standards**, clean folder structure, and version‑controlled DAX via Tabular Editor.

---

# 🚀 **Project Overview**

This project analyzes ecommerce marketing and customer performance across three major beauty brands:

- **Nykaa**
- **Purplle**
- **Tira Beauty**

It includes:

### 🔹 **SQL Data Analysis**
- Campaign performance queries  
- Customer segmentation queries  
- RFM SQL logic  
- Churn labeling logic  

### 🔹 **Python Analytics & Modeling**
- Exploratory Data Analysis (EDA)  
- RFM segmentation  
- Churn prediction model (Random Forest)  
- CLV estimation (AOV, frequency-based, discounted CLV)  

### 🔹 **Power BI Dashboard (5 Pages)**
- Executive Overview  
- RFM Segmentation  
- Churn & Retention  
- Profitability  
- Channel & Audience Insights  

### 🔹 **Business Insights**
- High-value customer identification  
- Churn risk detection  
- Marketing ROI optimization  
- Profitability drivers  
- Channel performance benchmarking  

---

# 🧠 **Key Dashboards Included**

## **1️⃣ Executive Overview**
- Total Revenue, Leads, Conversions  
- Revenue per Lead  
- Performance Score  
- Marketing Funnel (Impressions → Clicks → Leads → Conversions)  
- Revenue Trend (MTD/YTD)  
- Channel Performance Comparison  

## **2️⃣ RFM Segmentation**
- Recency, Frequency, Monetary scoring  
- High / Medium / Low value segmentation  
- RFM Heatmap  
- FM Scatter Plot  
- Customer Value Analysis  

## **3️⃣ Churn & Retention Analysis**
- Actual vs Predicted Churn  
- Retention Drivers (Segment & Campaign Type)  
- Churn Risk Heatmap  
- Predicted Churn by Segment  
- Churn Rate by Segment  

## **4️⃣ Profitability Dashboard**
- Revenue → CLV → Churn Loss → Net Profit (Waterfall)  
- ROI by Channel  
- Profitability by Segment  
- CLV by Customer Segment  
- Revenue by Customer Segment  

## **5️⃣ Channel & Audience Insights**
- Revenue by Segment  
- Conversions by Segment  
- ROI by Channel  
- Cost per Conversion  
- Channel Performance Comparison  

---

# 🗂️ **Project Folder Structure**

```
ecommerce-customer-analytics/
│
├── data/
│   ├── raw/                 # Original CSV files
│   └── processed/           # Cleaned datasets, RFM, churn, CLV outputs
│
├── notebooks/
│   ├── 01_eda.ipynb         # Exploratory Data Analysis
│   ├── 02_rfm_analysis.ipynb
│   ├── 03_churn_model.ipynb
│   └── 04_clv_estimation.ipynb
│
├── sql/
│   ├── customer_analysis.sql
│   ├── rfm_queries.sql
│   └── churn_queries.sql
│
├── src/
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   └── evaluate_model.py
│
├── powerbi/
│   ├── dashboards/
│   │   └── Ecommerce_Analytics.pbix
│   ├── measures/            # Exported via Tabular Editor
│   ├── models/
│   │   ├── star_schema.png
│   │   └── data_model.pbix
│   └── assets/
│
├── reports/
│   └── business_report.pdf
│
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

---

# 🧩 **Semantic Model & DAX Highlights**

This project uses a **clean star schema**:

### **Fact Tables**
- Campaign Performance  
- Conversions  
- Revenue  
- Churn Predictions  
- RFM Scores  
- CLV Outputs  

### **Dimension Tables**
- Customers  
- Channels  
- Campaigns  
- Dates  

### **Display Folders (Tabular Editor)**
- _RFM  
- _Churn  
- _Revenue  
- _Performance  
- _Segmentation  
- _Time_Intelligence  
- _Formatting  
- _Debug  

### **Key DAX Concepts**
- RFM scoring  
- Churn probability modeling  
- CLV calculation  
- Churn‑adjusted profitability  
- Time intelligence (MTD, YTD, YoY)  
- KPI scoring model  
- Waterfall modeling using SWITCH()  

All DAX measures are exported using **Tabular Editor** for version control.

---

# 🎯 **Business Impact**

This analytics solution enables:

### ✔ High‑value customer identification  
### ✔ Churn risk prediction & retention strategy  
### ✔ Marketing spend optimization  
### ✔ Profitability & CLV‑driven decision making  
### ✔ Executive‑level visibility into performance  
### ✔ Channel & audience targeting insights  

---

# 🛠️ **Tools & Technologies**

- Power BI Desktop  
- DAX  
- Tabular Editor  
- Python (Pandas, Scikit‑Learn)  
- SQL  
- Power Query  
- Git & GitHub  
- Semantic Modeling  
- Data Visualization & Storytelling  

---

# 📥 **How to Use This Project**

### 1. Clone the repository  
```
git clone https://github.com/yourusername/ecommerce-customer-analytics.git
```

### 2. Open the Power BI dashboard  
```
powerbi/dashboards/Ecommerce_Analytics.pbix
```

### 3. Explore the DAX measures  
```
powerbi/measures/
```

### 4. Run Python notebooks  
```
notebooks/01_eda.ipynb
notebooks/02_rfm_analysis.ipynb
notebooks/03_churn_model.ipynb
notebooks/04_clv_estimation.ipynb
```

### 5. Review SQL scripts  
```
sql/
```

---

# 📌 **Future Enhancements**

- Add Fabric Lakehouse version  
- Add automated refresh pipeline  
- Add Power BI deployment pipeline  
- Add ML model monitoring  
- Add real‑time streaming dashboard  

---

# 👤 **Author**

**Abdurrab**  
Data Analyst | BI Developer | Power BI Specialist  
Abu Dhabi, UAE  