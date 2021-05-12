import puppeteer from 'puppeteer-extra'
import StealthPlugin from 'puppeteer-extra-plugin-stealth'
import Adblocker from 'puppeteer-extra-plugin-adblocker'
import * as fs from 'fs'
import * as papaparse from 'papaparse'

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
for (let i = 0; i < 10; i++) {
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

// start puppeteer
puppeteer
  .use(StealthPlugin())
  .use(Adblocker({ blockTrackers: true }))
  .launch({ headless: true })
  .then(async browser => {
    // start browser
    const page = await browser.newPage()
    // get session IP address
    const response = await page.goto('https://api.ipify.org')
    const ipAddress = await response?.text()
    // await page.waitForTimeout(2000)
    // start crawling domains
    var i = 0
    for (const domain of domains) {
      // time request
      const start = process.hrtime.bigint()
      // get complete domain path
      const complete = 'http://' + domain
      try {
        const domainResponse = await page.goto(complete, { 'timeout': 40000 })
        data.push({
          'id': i, 
          'time': (process.hrtime.bigint() - start) / BigInt(1e+9),
          'ogdomain': complete,
          'resdomain': domainResponse?.url(),
          'ip': ipAddress, 
          'status': domainResponse?.status(), 
          'error': 'none'
        })
        // necessary delay to avoid bot detection
        await page.waitForTimeout(5000)
        // take screenshot
        const screenshotPath = screenshotDir + '/' + fullDate + '-' + i + '-' + domain.replace('.', 'DOT') + '.png'
        await page.screenshot({ path: screenshotPath, fullPage: true })
      } catch (error) {
        data.push({
          'id': i, 
          'time': (process.hrtime.bigint() - start) / BigInt(1e+6),
          'ogdomain': complete,
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
      .then(()=> console.log('The CSV file was written successfully'))

  })
