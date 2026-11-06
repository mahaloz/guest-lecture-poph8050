Build an interactive web application called **Avian Influenza Outbreak Explorer**.

The goal is to help avian virology researchers visually explore historical HPAI outbreaks in the United States.

This is a rapid prototype for demonstrating how AI coding agents can build useful scientific tools. Prioritize a polished, working interface over complex infrastructure.

### Data

Use real USDA APHIS data on confirmed HPAI detections in commercial and backyard poultry flocks from 2022 onward.

Official source:
https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks

A convenient downloadable CSV derived from APHIS data:
https://casey891.github.io/hpai-dashboard/data/poultry_detections.csv

Download and inspect the dataset. Determine its available columns and date coverage. Do not invent data or silently fill missing values.

### Application

Build a visually appealing, interactive dashboard with:

**1. Animated US outbreak map**
- Display confirmed HPAI detections geographically, aggregated by state.
- Include a timeline slider and a Play/Pause button to animate outbreaks over time.
- Allow users to switch between monthly outbreaks and cumulative outbreaks.
- Use a color scale to indicate outbreak intensity.
- Hovering over a state should show relevant statistics.

**2. Interactive outbreak timeline**
- Show confirmed outbreak detections over time.
- Allow users to zoom into particular years or months.
- Selecting a time period should update the map.

**3. Data exploration**
- Filter by state, date range, and commercial versus backyard flock categories where the data permits.
- Toggle between the number of affected flocks and the total number of birds in affected flocks.
- Display summary statistics that update with the filters.

**4. Interesting observations**
- Automatically surface simple descriptive observations from the currently selected data, such as the month with the highest number of detections or the states with the most affected flocks.
- Do not use an LLM for this feature. Compute the observations directly from the data.
- Make observations transparent and verifiable.

### Technical requirements

- Use Python, Streamlit, Pandas, and Plotly.
- Run locally with a single command.
- Cache downloaded data to avoid repeated requests.
- Use real historical data rather than simulated outbreaks.
- Clearly display the data source, retrieval date, and limitations.
- Distinguish flock detections from numbers of birds in affected flocks; do not label the latter as confirmed infected or dead birds.
- Include a README with setup instructions.

### Priorities

First build the working interactive map, timeline, and filters. Then add animation and automatic observations. Avoid unnecessary backend services, accounts, databases, or deployment infrastructure.

Make reasonable design and implementation decisions autonomously. Execute the application, check for errors, and fix any problems you find.

I want an attractive, functional scientific visualization tool that I can demonstrate live to graduate students.
