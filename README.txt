## Afternoon Program Enrollment: A Data Visualization Tool for Schools
### John Chung, Noah Rae-Grant, Ben Rutabana
### DS 5010 Spring 2024

An interactive data visualization dashboard designed to enable stakeholders at an educational institution to better understand and analyze enrollment trends and correlations in their afternoon programs.


Data format:
A CSV file, each row is an individual student's record from a single season.
Columns:
  - Person ID: unique ID numbers for each student
  - Gender code: M, F, N
  - Race/ethnicity: self-reported. A value of 0 indicates that no race/ethnicity data was provided by the student
  - FA: student's financial aid status
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
