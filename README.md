# Predicting changes to INa from missense mutations in human SCN5A

This repository contains the code and data set for the publication "Predicting changes to INa from missense mutations in human SCN5A".

## Main files

- [db] Python code to turn CSV files into an SQLite database, perform queries, and create figures.
- [db/base] Python code to create and manage the database.
- [db/data-in] CSV files used to genenerate the SQLite database.
- [db/data-out] CSV and WEKA files created by querying the database.
- [db/figures-in](db/figures-in) Veusz ([link](https://veusz.github.io/)) figures that use the generated CSV data.
- [db/figures-out] Rendered figures.
- [db/tasks] Python code that uses the above to create a database, query it, store CSVs, and generated figures. Accessed via the `run` script.
- [BruteSearchWeka] Java code that uses WEKA to perform machine-learning (and validation) on the WEKA files generated from the database.

## Auxillary files

- [acid-scores] Python code to convert Gonnet, Granthan and PAM scores to a form suitable for the database.
- [diagram] Python code that turns the SCN5A sequence into 2d coordinates, suitable for drawing a diagram.
- [genetic-code] Python code to list the possible missense mutations in SCN5A.
- [epdata-20160511.ods] OpenOffice/LibreOffice Calc file with the main EPDATA, but a little outdated compared to the database code (better to look at `db/data-in`).

## Citing this work

If you use any of the code or data in this repository, please cit

Michael Clerx, Jordi Heijman,, Pieter Collins, Paul G.A. Volders
Predicting changes to INa from missense mutations in human SCN5A.
Scienticif Reports 8, 12797 (2018).
https://doi.org/10.1038/s41598-018-30577-5
