# Installation
`python3 -m pip install -r requirements.txt`

run
`crontab -e`
and add the lines
```
USABILLA=/path/to/repo
*/30 8-18 * * 1-5 python3 $USABILLA/fetchData.py >2 $USABILLA/cron.log
```
where `/path/to/repo` is the path to this repository

This will run the script every 30 minutes Monday-Friday from 8am-6pm on the local time of the machine.
If the hosting machine is in a timezone other than PST, please edit the hours to fall under 8am-6pm PT

# Usage
Once installed, everything should be viewable from the [google sheets for the Usabilla data](https://docs.google.com/spreadsheets/d/17sPgywLbVhnXrQyTvU7dNP_-yY78ty9Cxy-dGwckn-Y/edit#gid=1724410617)

Under the 'Status' sheet, you can find a record of all the script executions



