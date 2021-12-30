const fs = require('fs')
let file;

try {
    const data = fs.readFileSync(process.argv[2], 'utf8')
    let emails = data.split('\n')

    let outEmails = []
    let invalidEmails = []
    let duplicateEmails = []

    for (let email of emails) {
        let re = /(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])/i
		if(re.test(email)) {
            if (!outEmails.includes(email)) {
                outEmails.push(email.toUpperCase())
            } else {
                duplicateEmails.push(email)
            }
        } else {
            if (email.length > 0) invalidEmails.push(email) 
        }
    }

    outEmails.sort(function (a, b) {
        return a.length - b.length;
    });

    let output = outEmails.reduce((a, b) => { return a + b + "\n" }, ""); 

    fs.writeFileSync("cleaned_" + process.argv[2], output);
    console.log(`Created file cleaned_${process.argv[2]}`);
    console.log(`${invalidEmails.length} invalid emails`);
    console.log(invalidEmails);
    console.log(`${duplicateEmails.length} duplicate emails`);
    console.log(duplicateEmails);


} catch (err) {
    console.error(err)
}

