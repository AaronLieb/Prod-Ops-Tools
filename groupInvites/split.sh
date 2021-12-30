split -l $3 $1 $2
FILES="./$2*"
INDEX=1
for f in $FILES; do 
    mv $f $2${INDEX}
    let INDEX=${INDEX}+1
done
