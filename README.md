# Bulk Tags Project

## CSV File Format
Assume the format is `org slug, project name`

*Note:* see `sample.csv` for example

## How to Run
Assume: `python 3.13`

```bash
pip install -r requirements.txt

python main.py --snyk-token $SNYK_TOKEN --csv-path <PATH TO CSV> --tag-key <KEY> --tag-value <VALUE>
```