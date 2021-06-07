import puppeteer from 'puppeteer-extra'
import StealthPlugin from 'puppeteer-extra-plugin-stealth'
import Adblocker from 'puppeteer-extra-plugin-adblocker'
import * as fs from 'fs'
import * as papaparse from 'papaparse'

// get date info
let datetime = new Date()
const date = datetime.getDate()
const month = datetime.getMonth() + 1
const year = datetime.getFullYear()
const fullDate = year + "-" + month + "-" + date

// contants
const numberDomains = 1000
const browserLimit = 300
const requestRetries = 3
const timeouts = [20000, 30000, 35000, 40000]
// const clearoutLimit = 10
const csvDir = 'data/stage4/csvs/' + fullDate

// variables
let index = 1
let domainIndex = 0

// using local copy of extension: https://www.i-dont-care-about-cookies.eu
const cookieExtension = 'extensions/cookies_ext/3.3.0_0'
// using local copy of extension: https://getadblock.com
const adblockerExtension = 'extensions/adblock_ext/4.33.0_0'

// Mullvad
const screenshotDir = 'data/stage4/screenshots/' + fullDate + '-mullvad'
const csvPath = csvDir + '/' + fullDate + '-mullvad.csv'

// Control
// const screenshotDir = 'data/stage4/screenshots/' + fullDate + '-control'
// const csvPath = csvDir + '/' + fullDate + '-control.csv'

// waiting
const delay = (ms: number | undefined) => new Promise(resolve => setTimeout(resolve, ms))

// make screenshots directory
fs.mkdir(screenshotDir, { recursive: true }, (error) => {
  if (error) throw error
})
// make CSVs directory
fs.mkdir(csvDir, { recursive: true }, (error) => {
  if (error) throw error
})

// load the domains from list created from Stage 4.1 data
const domainsPath = 'domains/2021-6-4-stage4domains.csv'
const parser = papaparse.parse(fs.readFileSync(domainsPath, { encoding: 'utf-8' }))
const links: string[][] = []
let pages: string[] = []
let dom = 'none'
for (let i = 0; i < parser.data.length; i++) {
  const row: any = parser.data[i]
  if (typeof row[1] == 'undefined') {
    continue
  }
  // new domain
  if (row[0] == '0') {
    // push array of subpages to array of links
    if (pages.length > 0) {
      links.push([...pages])
    }
    // reset array of subpages
    pages = []
    const link = row[1]
    dom = link.split("//")[1]
    pages.push(link)
  }
  else {
    const link = row[1]
    // check if there's at least one character of non-whitespace
    if (/\S/.test(link)) {
      pages.push(link)
    }
  }
}
// push final set of pages to links array
links.push([...pages])

// prepare the CSV file writer
const createCsvWriter = require('csv-writer').createObjectCsvWriter
const csvWriter = createCsvWriter({
  path: csvPath,
  header: [
    {id: 'id', title: 'ID'},
    {id: 'subpage', title: 'Subpage ID'},
    {id: 'time', title: 'Time'},
    {id: 'duration', title: 'Duration (ms)'},
    {id: 'attempts', title: 'Attempts'},
    {id: 'ogdomain', title: 'Request Domain'},
    {id: 'resdomain', title: 'Response Domain'},
    {id: 'ip', title: 'IP Address'},
    {id: 'status', title: 'HTTP Status Code'},
    {id: 'error', title: 'Error'},
  ]
})


async function runBrowser() {
  // start puppeteer
  await puppeteer
  .use(StealthPlugin())
  .use(Adblocker({ blockTrackers: true }))
  .launch({
    headless: false,
    args: [
      `--disable-extensions-except=${cookieExtension},${adblockerExtension}`,
      `--load-extension=${cookieExtension}`,
      `--load-extension=${adblockerExtension}`,
      '--window-size=1200,600',
    ],
  })
  .then(async browser => {
    // keep Chromium from downloading files
    let client = await browser.target().createCDPSession()
    await client.send('Browser.setDownloadBehavior', {behavior: 'deny'})
    let page = await browser.newPage()
    page.removeAllListeners('requests')
    // get session IP address
    let response
    let ipAddress
    for (let i = 0; i < requestRetries; i++) {
      try {
        response = await page.goto('https://api.ipify.org')
        ipAddress = await response?.text()
        break
      }
      catch (error) {
        await page.waitForTimeout(4000)
      }
    }
    await page.close()
    // figure out start and end index
    const start = domainIndex
    const end = Math.min(start + browserLimit, numberDomains)
    // start crawling domains
    for (let j = start; j < end; j++) {
      page = await browser.newPage()
      page.removeAllListeners('requests')
      // time request
      const startTime = process.hrtime.bigint()
      // get home and subpages
      const pages = links[j]
      // get domain
      const domain = pages[0].split("//")[1]
      for (let g = 0; g < pages.length; g++) {
        // retry non-2xx requests up to 3 times
        for (let i = 1; i < requestRetries+1; i++) {
          try {
            const domainResponse = await page.goto(pages[g], { waitUntil: 'domcontentloaded', timeout: timeouts[i] })
            // let extensions do their work
            await page.waitForTimeout(6000)
            let statusCode = domainResponse?.status()
            // check empty response
            if (typeof statusCode == 'undefined') {
              // special value so a screenshot will be taken, but we know something was not quite right
              statusCode = 215
            }
            // take screenshot if status code 2xx
            if (typeof statusCode !== 'undefined' && statusCode > 199 && statusCode < 300) {
              const screenshotPath = screenshotDir + '/' + fullDate + '-' + index + '-' + domain + '-' + g + '.png'
              await page.screenshot({ path: screenshotPath })
            }
            await saveData(startTime, g, i, pages[g], page.url(), ipAddress, statusCode, 'none')
            break
          } catch (error) {
            if (i == requestRetries) {
              await saveData(startTime, g, i, pages[g], 'none', ipAddress, 0, error.message)
            }
            else {
              await page.waitForTimeout(5000)
            }
          }
        }
        index++
      }
      domainIndex++
      // clear cache & cookies every clearoutLimit requests
      client = await page.target().createCDPSession()
      await client.send('Network.clearBrowserCookies')
      await client.send('Network.clearBrowserCache')
      // await page.waitForTimeout(1000)
      await page.close()
    }

    // close browser instance
    await browser.close()

  })
}

async function saveData(start: bigint, subpageIndex: number, attemptNumber: number, ogDomain: string, resDomain: string, ipAddress: string | undefined, statusCode: number, error: string) {
  // sort out timestamp for request
  datetime = new Date()
  const hours = datetime.getHours()
  const minutes = datetime.getMinutes()
  const seconds = datetime.getSeconds()
  const timeStamp = hours + ":" + minutes + ":" + seconds
  const data = [{
    'id': index,
    'subpage': subpageIndex,
    'time': timeStamp,
    'duration': (process.hrtime.bigint() - start) / BigInt(1e+6),
    'attempts': attemptNumber,
    'ogdomain': ogDomain,
    'resdomain': resDomain,
    'ip': ipAddress, 
    'status': statusCode, 
    'error': error
  }]
  await csvWriter.writeRecords(data)
}

async function run() {
  while (domainIndex < numberDomains) {
    try {
      await runBrowser()
    } catch (error) {
      console.log('Error at request index ' + String(index) + ', domain index ' + String(domainIndex))
      console.log(error)
      await delay(5000)
    }
  }
}

run()
