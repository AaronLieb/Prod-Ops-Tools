const path = require('path');
const fs = require('fs');

const exp = /[A-Z]+-[A-Z]+-[0-9a-zA-Z_]+-[0-9]{2}\.[0-9]{2}\.[0-9]{2}-\[[a-zA-Z_]+-?[a-zA-Z_]*\]\.pdf/

const directoryPath = path.join(__dirname, 'files');
fs.readdir(directoryPath, function (err, files) {
    if (err) {
        return console.log('Unable to scan directory: ' + err);
    } 
    files.forEach(function (file) {
        if (file.slice(-3) == "pdf" || file.slice(-3) == "PDF") {
            let result = exp.test(file) ? "\x1b[32mtrue\x1b[0m" : "\x1b[31mfalse\x1b[0m"
            console.log(result + ": " + file); 
        }
    });
});
