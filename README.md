# Predicting changes to INa from missense mutations in human SCN5A

This repository contains the code and data set for the 2018 publication [Predicting changes to INa from missense mutations in human SCN5A](https://doi.org/10.1038/s41598-018-30577-5) by Michael Clerx, Jordi Heijman, Pieter Collins, and Paul G.A. Volders.

For this paper we created a list of **610 SCN5A missense mutations** (that's all I could find in the summer of 2016), and found **electrophysiology (EP) experiments had been performed for 243** of them.
This is a considerable number, given that there are only 11923 mutations possible (so 5.1% appear in the literature, and 2.0% had been measured when we performed this study).
Most data hadn't been published in a "raw" time-series form, but as "summary statistics" e.g. shifts in the midpoint of activation or inactivation of INa.
We saw that 175 studies reported the EP data for INa/INaL had changed due to the mutation, while 68 showed no significant change.
Activation was altered in 69 cases, inactivation in 125, the late component of INa had changed in 40 components, and 30 mutations showed no current at all.

**We asked if, given this data, we could predict the presence of these changes for the remaining 98% of mutants using statistics (or machine learning).**
If so, this would enable fully in-silico predictions from genotype to INa phenotype, and then all the way up to pseudo-ECG using computaional modelling!
So a very attractive prospect if possible.

Prediction happens in three steps:

1. **Features** are created for each mutation.
   In principle (position on the gene + new amino acid) is a full, unique descriptor of an SCN5A mutation.
   Yet this doesn't contain much useful information to link the mutation to its effect.
   So a representation in terms of features with much more information is required.
   We added several features to do with position (index of the gene, side of the membrane, distance to the voltage sensor etc.), and several to do with amino acid properties (change in charge, change in hydrophobicity), as well as a few others (Grantham similarity score, Gonnet substitution likelihood, SCNxA isoform conservedness).
2. **Machine-learning** is applied. 
  We defined 5 sub problems (affects EP, affects activation, affects inactivation, affects late component, leads to zero current) and tried to classify each mutation in the "yes" or "no" group for each problem.
  Because we didn't know which classification methods would work, we tried several different ones, that used very different mechanisms.
  10-fold cross-validation was used to tune the classifiers, and we used a separate validation set to see how well the tuned classifier performed.
  These methods were all obtained through [WEKA](https://www.cs.waikato.ac.nz/ml/weka/).
3. **Checking the results**.
   Finally, we check the performance of each method, and look at the MCC and AUC for each method and problem.

But it didn't work!
We got results that were slightly better than chance, so we could do better than just guessing, but not by much.
(We could, however, improve over clinically used predictors of pathogenicity, although that's a slightly different problem.)
Why didn't it work better?

We suspect these three causes:

1. Bias in the dataset. 
   Machine-learning works best if you have a good balance between each class (so e.g. equal numbers of mutations affecting activation and not affecting it).
   But who would express, measure, and publish a mutation that has no effect?
   Understandably, our data set was highly biased towards mutations with a strong effect.
2. Inconsistentcy.
   Measuring INa is hard, and lots of conditions matter.
   As a result, there was a lot of inconsistency in the data set (including for very similar experiments).
3. The choice of features.
   Inspecting the features used by the machine learning algorithms, we found they mostly focussed on the positional information, but got hardly anything from the old and new amino acids!
   So charge, hydrophobicity, etc. all got ignored.
   This suggests we need a better way to create meaningful features that describe what a particular mutation _means_ for the channel protein.

More recent work by other groups looked at similar problems, e.g. [Kroncke et al. 2019](https://doi.org/10.1016/j.csbj.2019.01.008), and [Heyne et al. 2020](https://doi.org/10.1126/scitranslmed.aay6848).

The code and data for the 2018 publication is available from this repository, and described below:

## Main files

- [db](db) Python code to turn CSV files into an SQLite database, perform queries, and create figures.
- [db/base](db/base) Python code to create and manage the database.
- [db/data-in](db/data-in) CSV files used to genenerate the SQLite database.
- [db/data-out](db/data-out) CSV and WEKA files created by querying the database.
- [db/figures-in](db/figures-in) Veusz ([link](https://veusz.github.io/)) figures that use the generated CSV data.
- [db/figures-out](db/figures-out) Rendered figures.
- [db/tasks](db/tasks) Python code that uses the above to create a database, query it, store CSVs, and generated figures. Accessed via the `run` script.
- [BruteSearchWeka](BruteSearchWeka) Java code that uses WEKA to perform machine-learning (and validation) on the WEKA files generated from the database.

## Auxillary files

- [acid-scores](acid-scores) Python code to convert Gonnet, Granthan and PAM scores to a form suitable for the database.
- [diagram](diagram) Python code that turns the SCN5A sequence into 2d coordinates, suitable for drawing a diagram.
- [genetic-code](genetic-code) Python code to list the possible missense mutations in SCN5A.
- [epdata-20160511.ods](epdata-20160511.ods) OpenOffice/LibreOffice Calc file with the main EPDATA, but a little outdated compared to the database code (better to look at `db/data-in`).

## Citing this work

If you use anything from this repository, please cite:

- Michael Clerx, Jordi Heijman,, Pieter Collins, Paul G.A. Volders
  Predicting changes to INa from missense mutations in human SCN5A.
  Scientific Reports 8, 12797 (2018).
  https://doi.org/10.1038/s41598-018-30577-5
