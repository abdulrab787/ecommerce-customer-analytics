📊 Ecommerce Analytics — Power BI Project
A complete end‑to‑end analytics solution covering Marketing Performance, Customer Segmentation, Churn Prediction, Profitability, and RFM Analysis.
Built using Power BI, DAX, Tabular Editor, and a clean semantic model following enterprise BI standards.

🚀 Project Overview
This project analyzes ecommerce customer behavior and marketing performance using:

5‑page Power BI dashboard

RFM segmentation

Churn prediction & retention analysis

Profitability modeling (CLV, churn‑adjusted value, ROI)

Marketing funnel performance

Channel & audience insights

The goal is to provide a C‑suite ready analytics solution that supports data‑driven decisions across marketing, retention, and revenue strategy.

🧠 Key Dashboards Included
1️⃣ Executive Overview
Total Revenue, Leads, Conversions

Revenue per Lead

Performance Score

Marketing Funnel (Impressions → Clicks → Leads → Conversions)

Revenue Trend (MTD/YTD)

Channel Performance Comparison

2️⃣ RFM Segmentation
RFM Scores (Recency, Frequency, Monetary)

Segment Distribution (High / Medium / Low Value)

RFM Heatmap

FM Scatter Plot

Customer Value Analysis

3️⃣ Churn & Retention Analysis
Actual vs Predicted Churn

Retention Drivers (Segment & Campaign Type)

Churn Risk Heatmap

Predicted Churn by Segment

Churn Rate by Segment

4️⃣ Profitability Dashboard
Revenue → CLV → Churn Loss → Net Profit (Waterfall)

ROI by Channel

Profitability by Segment

CLV by Customer Segment

Revenue by Customer Segment

5️⃣ Channel & Audience Insights
Revenue by Segment

Conversions by Segment

ROI by Channel

Cost per Conversion

Channel Performance Comparison

🏗️ Project Folder Structure
Code
ecommerce-analytics/
│
├── powerbi/
│   ├── dashboards/
│   │   └── Ecommerce_Analytics.pbix        # Final 5‑page dashboard
│   │
│   ├── measures/                           # Exported via Tabular Editor
│   │   ├── Executive_Overview.dax
│   │   ├── RFM_Analysis.dax
│   │   ├── Churn_Retention.dax
│   │   ├── Profitability.dax
│   │   ├── _RFM/
│   │   ├── _Churn/
│   │   ├── _Revenue/
│   │   ├── _Performance/
│   │   ├── _Segmentation/
│   │   ├── _Time_Intelligence/
│   │   ├── _Formatting/
│   │   └── _Debug/
│   │
│   ├── models/
│   │   ├── star_schema.png
│   │   └── data_model.pbix
│   │
│   └── assets/                             
│
├── data/
│   ├── raw/
│   └── processed/
│
└── README.md
🧩 Semantic Model & DAX Highlights
This project uses a clean, enterprise‑grade semantic model:

Fact tables for revenue, conversions, impressions, churn, RFM

Dimension tables for customers, channels, campaigns, dates

Display folders for organized DAX:

_RFM

_Churn

_Revenue

_Performance

_Segmentation

_Time_Intelligence

_Formatting

_Debug

Key DAX Concepts Used:
RFM scoring

Churn probability modeling

CLV calculation

Churn‑adjusted profitability

Time intelligence (MTD, YTD, YoY)

KPI scoring model

Waterfall modeling using SWITCH()

All DAX measures are exported using Tabular Editor for version control.

🎯 Business Impact
This solution enables:

Identification of high‑value customer segments

Prediction of churn risk and retention opportunities

Optimization of marketing spend across channels

Understanding of profitability drivers

Executive‑level visibility into revenue performance

🛠️ Tools & Technologies
Power BI Desktop

DAX

Tabular Editor 2

Power Query

Git & GitHub

Semantic Modeling

Data Visualization & Storytelling

📥 How to Use
Clone the repository

Open the PBIX file:

Code
powerbi/dashboards/Ecommerce_Analytics.pbix
Review DAX scripts in:

Code
powerbi/measures/
Explore the semantic model in:

Code
powerbi/models/
📌 Future Enhancements
Add Python notebooks for churn modeling

Add SQL scripts for data extraction

Add Fabric Lakehouse version

Add automated refresh pipeline

👤 Author
Abdur  
Data Analyst | BI Developer | Power BI Specialist
Abu Dhabi, UAE