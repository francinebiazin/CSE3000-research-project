import puppeteer from 'puppeteer-extra'
import StealthPlugin from 'puppeteer-extra-plugin-stealth'
import Adblocker from 'puppeteer-extra-plugin-adblocker'
import * as fs from 'fs'
import * as papaparse from 'papaparse'

// contants
const numberDomains = 1000

var datetime = new Date()
const date = datetime.getDate()
const month = datetime.getMonth() + 1
const year = datetime.getFullYear()
const fullDate = year + "-" + month + "-" + date

// create the relevant directories for saving screenshots and csv files
// WITH MULLVAD
const screenshotDir = 'data/screenshots/' + fullDate + '-mullvad'
// CONTROL
// const screenshotDir = 'data/screenshots/' + fullDate + '-control'
fs.mkdir(screenshotDir, { recursive: true }, (error) => {
  if (error) throw error
})
const csvDir = 'data/csvs/' + fullDate
fs.mkdir(csvDir, { recursive: true }, (error) => {
  if (error) throw error
})

// load the domains
const domainsPath = 'domains/top-1m.csv'
const parser = papaparse.parse(fs.readFileSync(domainsPath, { encoding: 'utf-8' }))
const domains: string[] = []
for (let i = 0; i < numberDomains; i++) {
  const row : any = parser.data[i]
  domains.push(row[1])
}

// prepare the csv file writer
const createCsvWriter = require('csv-writer').createObjectCsvWriter
// WITH MULLVAD
const csvPath = csvDir + '/' + fullDate + '-mullvad.csv'
// CONTROL
// const csvPath = csvDir + '/' + fullDate + '-control.csv'
const csvWriter = createCsvWriter({
  path: csvPath,
  header: [
    {id: 'id', title: 'ID'},
    {id: 'time', title: 'Time (ms)'},
    {id: 'ogdomain', title: 'Request Domain'},
    {id: 'resdomain', title: 'Response Domain'},
    {id: 'ip', title: 'IP Address'},
    {id: 'status', title: 'HTTP Status Code'},
    {id: 'error', title: 'Error'},
  ]
})
const data: { 
  id: number;
  time: bigint;
  ogdomain: string;
  resdomain: string | undefined;
  ip: string | undefined; 
  status: number | undefined; 
  error: string | undefined 
}[] = []

// using local copy of extension: https://www.i-dont-care-about-cookies.eu
const pathToExtension = 'extensions/cookies_ext/3.3.0_0'

// start puppeteer
puppeteer
  .use(StealthPlugin())
  .use(Adblocker({ blockTrackers: true }))
  .launch({
    headless: false,
    args: [
      `--disable-extensions-except=${pathToExtension}`,
      `--load-extension=${pathToExtension}`,
    ],
  })
  .then(async browser => {
    // start browser
    let page = await browser.newPage()
    // await page.setViewport({ width: 1340, height: 700, deviceScaleFactor: 2 })
    // get session IP address
    const response = await page.goto('https://api.ipify.org')
    const ipAddress = await response?.text()
    // start crawling domains
    var i = 0
    for (const domain of domains) {
      if (i % 24 == 0) {
        await page.close()
        page = await browser.newPage()
        // await page.setViewport({ width: 1340, height: 700, deviceScaleFactor: 2 })
      }
      // time request
      const start = process.hrtime.bigint()
      // get complete domain path
      const completeDomain = 'http://www.' + domain
      try {
        const domainResponse = await page.goto(completeDomain, { waitUntil: 'networkidle0', timeout: 15000 })
        // let cookie acceptance extension do its work
        await page.waitForTimeout(2000)
        data.push({
          'id': i, 
          'time': (process.hrtime.bigint() - start) / BigInt(1e+6),
          'ogdomain': completeDomain,
          'resdomain': page.url(),
          'ip': ipAddress, 
          'status': domainResponse?.status(), 
          'error': 'none'
        })
        // necessary delay to avoid bot detection
        // await page.waitForTimeout(1000)
        // take screenshot
        const screenshotPath = screenshotDir + '/' + fullDate + '-' + i + '-' + domain.replace('.', 'DOT') + '.png'
        await page.screenshot({ path: screenshotPath })
      } catch (error) {
        data.push({
          'id': i, 
          'time': (process.hrtime.bigint() - start) / BigInt(1e+6),
          'ogdomain': completeDomain,
          'resdomain': 'none',
          'ip': ipAddress, 
          'status': 0, 
          'error': error.message
        })
      }
      i++
    }

    // close browser instance
    await browser.close()

    csvWriter
      .writeRecords(data)
      .then(() => console.log('The CSV file was written successfully'))

  })
