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
const requestRetries = 3
const timeout = 40000
const csvDir = 'data/csvs/' + fullDate

// variables
let index = 1

// using local copy of extension: https://www.i-dont-care-about-cookies.eu
const cookieExtension = 'extensions/cookies_ext/3.3.0_0'
// using local copy of extension: https://getadblock.com
const adblockerExtension = 'extensions/adblock_ext/4.33.0_0'

// Mullvad
const screenshotDir = 'data/screenshots/' + fullDate + '-mullvad'
const csvPath = csvDir + '/' + fullDate + '-mullvad.csv'

// Control
// const screenshotDir = 'data/screenshots/' + fullDate + '-control'
// const csvPath = csvDir + '/' + fullDate + '-control.csv'

// waiting
// const delay = (ms: number | undefined) => new Promise(resolve => setTimeout(resolve, ms))

// make screenshots directory
fs.mkdir(screenshotDir, { recursive: true }, (error) => {
  if (error) throw error
})
// make CSVs directory
fs.mkdir(csvDir, { recursive: true }, (error) => {
  if (error) throw error
})

// load the domains from Alexa Top 1M list
const domainsPath = 'domains/top-1m.csv'
const parser = papaparse.parse(fs.readFileSync(domainsPath, { encoding: 'utf-8' }))
const domains: string[] = []
let i = 0
let added = 0
while (added < numberDomains) {
  const row : any = parser.data[i]
  const domain = row[1]
  // skip problematic domains
  if (domain.includes('oeeee.com') || domain.includes('taleo.net')) {
    i++
    continue
  }
  domains.push(domain)
  i++
  added++
}

// prepare the CSV file writer
const createCsvWriter = require('csv-writer').createObjectCsvWriter
const csvWriter = createCsvWriter({
  path: csvPath,
  header: [
    {id: 'id', title: 'ID'},
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

// start puppeteer
puppeteer
  .use(StealthPlugin())
  .use(Adblocker({ blockTrackers: true }))
  .launch({
    headless: false,
    args: [
      `--disable-extensions-except=${cookieExtension},${adblockerExtension}`,
      `--load-extension=${cookieExtension}`,
      `--load-extension=${adblockerExtension}`,
      // '--ignore-certificate-errors',
      '--window-size=1200,600',
    ],
  })
  .then(async browser => {
    // start browser
    let page = await browser.newPage()
    // await page.setViewport({ width: 1340, height: 700, deviceScaleFactor: 2 })
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
    // start crawling domains
    for (const domain of domains) {
      page = await browser.newPage()
      // time request
      const start = process.hrtime.bigint()
      // get complete domain path
      const completeDomain = 'http://' + domain
      // retry non-2xx requests up to 3 times
      for (let i = 1; i < requestRetries+1; i++) {
        try {
          const domainResponse = await page.goto(completeDomain, { waitUntil: 'domcontentloaded', timeout: timeout })
          // let cookie acceptance extension do its work
          // await page.waitForTimeout(2000)
          // sort out timestamp for request
          datetime = new Date()
          const hours = datetime.getHours()
          const minutes = datetime.getMinutes()
          const seconds = datetime.getSeconds()
          const timeStamp = hours + ":" + minutes + ":" + seconds
          const statusCode = domainResponse?.status()
          // take screenshot if status code 2xx
          if (statusCode && statusCode > 199 && statusCode < 300) {
            const screenshotPath = screenshotDir + '/' + fullDate + '-' + index + '-' + domain + '.png'
            await page.screenshot({ path: screenshotPath })
          }
          const data = [{
            'id': index,
            'time': timeStamp,
            'duration': (process.hrtime.bigint() - start) / BigInt(1e+6),
            'attempts': i,
            'ogdomain': completeDomain,
            'resdomain': page.url(),
            'ip': ipAddress, 
            'status': statusCode, 
            'error': 'none'
          }]
          await csvWriter.writeRecords(data)
          break
        } catch (error) {
          if (i == requestRetries) {
            // sort out timestamp for request
            datetime = new Date()
            const hours = datetime.getHours()
            const minutes = datetime.getMinutes()
            const seconds = datetime.getSeconds()
            const timeStamp = hours + ":" + minutes + ":" + seconds
            const data = [{
              'id': index,
              'time': timeStamp,
              'duration': (process.hrtime.bigint() - start) / BigInt(1e+6),
              'attempts': i,
              'ogdomain': completeDomain,
              'resdomain': 'none',
              'ip': ipAddress, 
              'status': 0, 
              'error': error.message
            }]
            await csvWriter.writeRecords(data)
          }
          else {
            await page.waitForTimeout(5000)
          }
        }
      }
      index++
      // clear cache & cookies every 500 requests
      // if (index % 500 == 0) {
      //   const client = await page.target().createCDPSession();
      //   await client.send('Network.clearBrowserCookies');
      //   await client.send('Network.clearBrowserCache');
      // }
      await page.close()
    }

    // close browser instance
    await browser.close()

  })

