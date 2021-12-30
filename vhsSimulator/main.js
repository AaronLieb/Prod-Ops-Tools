const https = require('https')

const env = 'qa-charlie'
// current environments: prod (.env.prod) and test (.env.test)
require('dotenv').config({path: `.env.${env}`})

const TEST_GUID = '00000000-0000-TEST-GUID-000000000000' // vhs accepts this guid, not linked to an account
const GUID = TEST_GUID

const NUM_SIMULATIONS = 10

const heartbeatInterval = 30
const intervalRandomness = 3
const delay = 0

const asyncRequests = false // recommended: false
const asyncSimulations = true
const displayRequests = true

const minDuration = 100
const maxDuration = 1500
/* to do: get duration of real videos before starting */

const randomVid = true // randomly generates a videoGUID in the format SIMxxxxxxx
const videoGUID = "LGU020"

const randomStopPercent = true // if false, stopPercent uses maxStopPercent
const minStopPercent = 50
const maxStopPercent = 100

const randint = (min, max) => {
    return Math.floor(min + Math.random() * (max - min + 1))
}

const sleep = async ms => {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}  

const get = async vid => {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: process.env.HOST,
            path: `/vhs/v1/${GUID}?limit=1&videoGuids=${vid}`,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Api-Key': process.env.API_KEY,
            }

        }
        const req = https.request(options, res => {
            let data = ''

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                resolve(JSON.parse(data))
            })
        })
    
        req.on('error', error => {
            console.error(error)
            resolve(-1)
        })

        req.end()

    })
}


const send = async (type, details, vid, timecode, duration, timestamp) => {
    if (displayRequests) process.stdout.write(`[${type}] ${timecode}/${duration} ${timestamp.slice(11,19)} `)
    if (asyncRequests) console.log()
    return new Promise((resolve, reject) => {
    if (asyncRequests) resolve()
    const data = JSON.stringify({
        "eventType": type,
        "eventDetails": details,
        "profileID": GUID,
        "videoGuid": vid,
        "duration": duration,
        "timecode": timecode,
        "audioTrack": "English - All Audio",
        "subtitlesOn": false,
        "platform": "web",
        "platformDetails": "Firefox - Mac OS",
        "heartbeatInterval": 30,
        "timestamp": timestamp,
        "playerVisible": true
    })
    const options = {
        hostname: process.env.HOST,
        path: '/vhs/v1/heartbeats',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': data.length,
            'X-Api-Key': process.env.API_KEY,
        }

    }
    const req = https.request(options, res => {
        if (displayRequests) console.log(((res.statusCode == 200) ? '\x1b[32m' : '\x1b[31m') + `${res.statusCode}\x1b[0m`)

        res.on('data', d => {
            if (d.length > 3) process.stdout.write(d + '\n')
        })
        resolve(res.statusCode)
    })
    
    req.on('error', error => {
        console.error(error)
        resolve(-1)
    })

    req.write(data)
    req.end()
    })
}

const simulate = async () => {
    return new Promise(async (resolve, reject) => {
    let duration = Math.floor(minDuration + Math.random() * (maxDuration - minDuration));
    let intervalOffset = Math.floor((Math.random() * intervalRandomness * 2) - intervalRandomness)

    let vid = randomVid ? 'SIM' + randint(0, 10000000) : videoGUID;

    let stopPercent = (randomStopPercent ? randint(minStopPercent, maxStopPercent) : maxStopPercent)/100
    let stopTime = Math.floor(duration * stopPercent) + 1
    let finalPercent = Math.min(1, (stopTime/duration))

    let date = new Date()

    console.log(`\n\x1b[36mSimulating  ${vid}  ${stopPercent * 100}%\n\x1b[0m`)

    await send('start', 'system generated', vid, 0, duration, date.toISOString())
    await sleep(delay)

    for (let t = heartbeatInterval; t <= stopTime; t += heartbeatInterval + intervalOffset) {
        date.setSeconds(date.getSeconds() + heartbeatInterval + intervalOffset)
        intervalOffset = Math.floor((Math.random() * intervalRandomness * 2) - intervalRandomness)
        let responseCode = await send('heartbeat', 'system generated', vid, t, duration, date.toISOString())
        await sleep(delay)

        if ((t + heartbeatInterval)/duration > stopPercent) {
            date.setSeconds(date.getSeconds() + stopTime - t)
            break
        }
    }

    let responseCode = await send('stop', 'media end', vid, stopTime, duration, date.toISOString())

    let entry = (await get(vid)).items[0]

    console.log(`\n\x1b[36mCompleted ${vid} Expected: ${(finalPercent * 100).toFixed(2)}% Actual: ${entry.percentageViewed}% Resumable: ${entry.resumable}\n\x1b[0m`)
    if (Math.abs(finalPercent*100 - parseFloat(entry.percentageViewed)) > 0.5 || entry.resumable) {
        console.log('\x1b[31mprogress does not match\n\x1b[0m')
        resolve(false)
    } else {
        resolve(true)
    }
})
}

let failures = 0

let main = async () => {
    simulations = []
    for (let i = 0; i < NUM_SIMULATIONS; i++) {
        simulations.push(simulate)
    }
    if (asyncSimulations) Promise.all(simulations.map(f => f())).then(values => {
        values.forEach(value => {if (!value) failures++})
        console.log(`---REPORT---\nSimulations: ${NUM_SIMULATIONS}\nFailures: ${failures}`)
    })
    else {
        for (let simulation of simulations) {
            if (!(await simulation())) failures++
        }
        console.log(`---REPORT---\nSimulations: ${NUM_SIMULATIONS}\nFailures: ${failures}`)
    }
}
main()

