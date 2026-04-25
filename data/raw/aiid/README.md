# Attitudes, Identities, and Individual Differences: exploratory data subset

Please note that the dataset was previously referred to as the "Attiudes 2.0" study/dataset and some documentation still uses this title.

A 15% stratified subset of the total Attitudes, Identities, and Individual Differences (AIID) dataset is available for exploratory analyses. The much larger confirmatory data subset (c.70% of total) will be provided for confirmatory analyses.

Each data file is provided in both (a zipped) .csv and RData format. .csv is compatible with all major statistical software but uses larger file sizes: the IAT trial level data files will be around 1GB when unzipped.

## Data

### AIID_subset_exploratory

- A stratified 15% subset of the full data aggregated at the participant level.

### AIID_subset_exploratory_iat_trial_level_data

- Trial-level IAT data for the same session_ids included in the exploratory subset. 

### AIID_subset_confirmatory_masked_data.RData

- The masked confirmatory (70%) stratified subset of the full dataset, which will be used for confirmatory testing. All non-missing variables (other than demographics and exclusion variables) replaced with "1". This file allows for sample size calculations and power analyses to be performed while remaining blind to the data itself.

## Code

All processing and validation code from the creation of the master dataset can be found in the "code and codebooks" folder.

Some but not all R markdown files and their reports are are provided, on the basis that these some relevant only to the full dataset or contain information that would piece the blinding of the full dataset.

Note that files are named by order of execution. However, not all files are present here as some are relevant only to the full dataset.

.html reports can be opened in any browser and contain interactive tables and plots. "2_validation.html" is also hosted [here](http://mmmdata.io/AIID_validation.html) for live viewing. 

## Codebooks 

Codebooks for both the raw and processed data files are available in the data and codebooks folder. 

## Error reporting

A dataset this large and complex is likely to contain some irregularities or errors. Should you find any errors or issues with data processing or documentation, please contact Ian Hussey (ian.hussey@ugent.be) or [submit an issue on github](https://github.com/ianhussey/AIID-study/issues). 

## Version

In order to allows users of the dataset to track what changes have been made, a version number and changelog is provided below. Please ensure you apply your finalised analysis scripts to the most recent version of the data before submission of any manuscripts. 

1.0.8

## Changelog

1.0.8
- We have uploaded a delimted version of the file in  .TXT format (AIID_subset_confirmatory.txt).


1.0.7

- Updated processed data codebook: domain variable now explicitly states whether "X" and "Y" in each domain refer to each of the two categories, and point to a supporting document that lists the assignment for each file ("IAT word stimuli.xlsx")
- iat_failed_criteria_1 to iat_failed_criteria_8 were produced incorrectly in previous versions: previously, all NA entries had been replaced with FALSE and all non NA entries with TRUE. This was corrected. These variables now list which of multiple exclusion criteria were failed. 

1.0.6

- cultural influence self report item text, description, and response options were mislabelled in the codebook. 
- small typos in the codebook.

1.0.5

- NFCC A subscale column was empty - fixed data processing and reknitted all data processing steps.
- Fixed zip code removal workflow. Previous version excluded this when doing demographics, current version only excludes it at the very end. Scope for impact on other aspects of data processing therefore reduced. 
- Added conditional use of D, G, and A score object to speed up reknitting in the future if needed. 

1.0.4

- Fixed codebook processed data issues 
  - Interpretations of valence, warmth, and liking items were mixed up. 
  - Interpretation of cultural_pressure_mean and cultural_pressure_diff were corrected from "pressure to evaluation positively" to "Pressure to evaluate in some way, whether positive or negative, vs no pressure to feel a certain way about the categories."
- Fixed processing and processing notes for self_concept; code calculated reversed items but then didn't use them for the sum scores.

1.0.3

- all data files and references to them in code changed from attitudes_2.0 to AIID.
- .csv files now all us "NA" rather than "" for missing values, to help explicate when data is missing.

1.0.2

- processed data codebook incorrectly specified the max range of positive_only_x, positive_only_y, negative_only_x, negative_only_y, importance_x, importance_y to be 10 rather than 6. Corrected. Validation report correctly specified this to be 6 in its checks.

1.0.1

- Corrected the masking of 5 variables in the confirmatory masked dataset (attribute_category, attribute_label, block_order, individual_differences_measure, iat_type) which were being over-masked (all rows set to NA rather than NA or 1). Code and masked data updated.



