# jobbot
An Ai agent for finding jobs matching a pre-determined applicant profile.
Written in [LangChain](https://www.langchain.com), uses Mistral as LLM.

## Pre-requisites
* Mistral API Key.

## Installation
```
conda create -n jobbot python=3.12
conda activate jobbot
python -m pip install -r requirements.txt
```

## Crawl the job sites
Crawl the web and get the jobs from the pre-configured sites (BHT, TU, FU, HU).

````
./jobsearch.sh
````
The jobs found will be stored in the directory `jobs`, one Excel file for each source.

## Assess the jobs using AI
Examine the jobs found and assess whether they correspond to the applicant's profile. 
The applicant's profile can be edited using the Jupyter Notebook.

The jobs will be assessed along these aspects:
* Technical Skills Set Required
* Work Area of the Organization
* Role Position Within the Organization
* Geographical Location

Each aspect will be given a score from 1 to 5: 1. Perfect fit, 2. Good Fit, 3. Probable Fit, 4. Poor Fit, 5. Not a Fit. 

```
jupyter lab
```

Create a `notebooks/.env` file containing your Mistral Key:
```
MISTRAL_API_KEY=.....
```

Check that everything works by running these Notebooks:
;00_mistral_test 
: Checks that the Mistral and LangChain packages are installed correctly.
;01_chain_test
:Matches an example job with an example applicant profile. After the notebook has run, you can see the result in `assessments/1_assessment.csv`. Manually check that this assessment corresponds to your expectations.

Now everything is in place to run the assessment on real jobs.
1. Open the Notebook `02_jobbot`
2. Check that the `profile` string in the notebook corresponds to the desired applicant's profile.
3. Run the notebook. Depending on the number of jobs, this may take 1 hour approximately. The assessments wuill be stored as CSV files in the `assessments` directory.

## Report best matches
Run the notebook `03_report_jobs`. This will print
* The best matches for the applicant's profile.
