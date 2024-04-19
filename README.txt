## Afternoon Program Enrollment: A Data Visualization Tool for Schools
### John Chung, Noah Rae-Grant, Ben Rutabana
### Northeastern University DS 5010 Spring 2024

An interactive data visualization dashboard designed to enable stakeholders at an educational institution to better understand and analyze enrollment trends and correlations in their afternoon programs. Each of the visualizations is customizable with multidimensional filtering to highlight demographic information.


Data Visualizations:
  - Total enrollment by program histogram
  - Enrollment over time by program histograms
  - Top program correlation heatmap
  - Program popularity by demographic treemap


Data format:
A CSV file, each row is an individual student's record from a single season. Students will have multiple rows across seasons and years at the school. The original dataset had over 38000 entries, over 5000 unique student IDs, and more than 60 program choices, with 22 years of data.
Columns:
  - Person ID: unique ID numbers for each student
  - Gender code: M, F, N
  - Race/ethnicity: self-reported. A value of 0 indicates that no race/ethnicity data was provided by the student
  - FA: student's financial aid status. A value of 0 indicates no financial aid, a value of 1 indicates some financial aid, and a value of 2 indicates 90%+ financial aid.
  - Acad Yr (start): academic year that the record is for
  - Code: bucket category for the program the student is enrolled in (e.g. "S" for "sports", "A" for "arts")
  - Program (name): name of the program the student is enrolled in
  - Program (Gender): primarily used to distinguish between male and female sports teams
  - Program (Level): primarily used to distinguish sports levels (e.g. "varsity", "junior varsity")
  - Program (Season): the school offers different programs in fall, winter, and spring
  - Grade at Time of Activity: the student's grade (between 7 and 12)
  - Grad year: student's expected graduation year


Running the Module:
  - Place the enrollment data CSV in the "aft_module" folder and rename the enrollment_data variable in aft_pkg/aft_data_org.py as needed
  - Run the aft_dashboard.py module and launch http://localhost:8050 in your webbrowser
