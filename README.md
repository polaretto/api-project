# api-project
API Project - Report Generator

## Usage
`
$ python api-report.py -i <input_file_name> -o <output_file_name> -b <http_url>
`

All parameters are optional.

### Note:
The script works only with a precise structure of the input csv (no header) and having the following fields in those specific positions:

`
<USER_CSV_ROW> : Username, _, _, Password, _*
`

It also relies on a specific HTML structure and may probably brake with CMS updates. 
