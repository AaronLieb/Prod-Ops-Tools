# Mass inviting users to BOD groups

1. Get the email lists separated by language/region
2. Open the provided csv files and copy the emails into a separte file, where each line only contains the an email
3. Run the cleanup script on the email file, `node cleanup.js <filename>`
This will remove duplicates, put all the emails in all uppercase, and sort the emails alphabetically
It will also remove all invalid emails.
4. A new file will be generated with the original filename and the prefix "cleaned"
5. You can choose to split the emails by running the split script, `./split.sh <filename> <prefix>. The default size is 1000, but you can edit the script to change the size.
If it doesn't let you run the script, do `chmod +x split.sh`
6. When inviting users, you should check the group to ensure that all of the participants were invited before inviting the next batch. You can do so by running the getParticipants script


# Installation and usage for getParticipants

`brew update`
`brew install node`
`brew install npm`
`npm install typescript --save-dev`
`mkdir ~/Documents/groups-script && cd $_`
Download the file `getParticipantsInAGroup.ts`
Move the file into `~/Documents/groups-script`
Download the zip for `https://github.com/beachbodydigital/Okta.git`
Unzip and move the folder into `~/Documents/groups-script`
`cd Okta-master`
If python is not installed:
`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
`brew install python3`
Once python is installed:
`python -m pip install -r requirements.txt`
`cp okta ~/.aws/okta`
`./get-aws-keys.py -p digi-bodprod`
`cd ..`
open getParticipantsInAGroup.ts  and change the group ID on line 5
`npm i --save-dev @types/node`
`npx tsc getParticipantsInAGroup.ts`
`node getParticipantsInAGroup.js`



