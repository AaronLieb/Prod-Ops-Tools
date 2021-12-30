import { DynamoDB } from "aws-sdk";
const fs = require('fs')


const groupID = 'd7e71cbd-0b0f-400a-bb34-e2b75f0d5e9a'
const tableName = 'groups-api-prod'

const AWS = require('aws-sdk');

AWS.config.update({
  region: 'us-west-2',
});

const dynamoClient = new DynamoDB.DocumentClient()

function filterDuplicated(emails: string[]): string[] {
  let length = emails.length, result: string[] = [], seen = new Set();
  for (let index = 0; index < length; index++) {
    let value = emails[index];
    if (seen.has(value)) {
      console.log(`Duplicate: ${value}`)
      continue
    }
    seen.add(value);
    result.push(emails[index]);
  }
  return result
}


async function execute() {
  const pendingParticipantQuery: DynamoDB.DocumentClient.QueryInput = {
    TableName: tableName,
    IndexName: 'GSI_2',
    KeyConditionExpression: 'GSI2_PK = :PK AND begins_with(GSI2_SK, :SK)',
    ExpressionAttributeValues: {
      ':PK': `CHALLENGE_GROUP-${groupID}`,
      ':SK': 'PARTICIPANT#'
    },
    ExpressionAttributeNames: {
      '#state': 'state'
    },
    ProjectionExpression: 'attributes.id, attributes.#state, attributes.userInfo.email'
  }
  let result, count: number = 0, emails: Array<{ id: string, email: string, state: string }> = []
  do {
    result = await dynamoClient.query(pendingParticipantQuery).promise()
    if (result.Items && result.Items.length > 0) {
      result.Items.forEach((record) => {
        if (record.attributes) {
          count++
          emails.push({
            id: record.attributes.id,
            email: record.attributes.userInfo.email,
            state: record.attributes.state
          })
        } else {
          console.log(`No attributes for: ${record?.PK}`)
        }
      })
      console.log(emails.length)
      if (result.LastEvaluatedKey) {
        pendingParticipantQuery.ExclusiveStartKey = result.LastEvaluatedKey
      }
    }
  } while (result.LastEvaluatedKey)
  // console.log(emails)
  emails.forEach((email)=>{
    fs.appendFileSync('./emails', `${email.id},${email.email},${email.state}\n`)
  })

  console.log(`Participant length: ${emails.length}`)

  // const dedupemails = filterDuplicated(emails)
  // console.log(dedupemails.length)
  console.log("Count: " + count)
}

console.time('Counting')
execute().then(() => {

    console.timeEnd('Counting')
    console.debug('finished'), (err) => {
      console.error(`Error: ${err.message}`)
    }
  }
)

