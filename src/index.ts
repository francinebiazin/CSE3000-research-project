import vanillaPuppeteer from 'puppeteer'
import { addExtra } from 'puppeteer-extra'
import StealthPlugin from 'puppeteer-extra-plugin-stealth'
import Adblocker from 'puppeteer-extra-plugin-adblocker'
import * as fs from 'fs'
import * as papaparse from 'papaparse'
import { exec } from 'child_process'

// get date info
const datetime = new Date()
const date = datetime.getDate()
const month = datetime.getMonth() + 1
const year = datetime.getFullYear()
const fullDate = year + "-" + month + "-" + date

// contants
const numberDomains = 100
const pageLimit = 20
const requestRetries = 3
const mullvadScreenshotDir = 'data/screenshots/' + fullDate + '-mullvad'
const controlScreenshotDir = 'data/screenshots/' + fullDate + '-control'
const csvDir = 'data/csvs/' + fullDate
const mullvadCsvPath = csvDir + '/' + fullDate + '-mullvad.csv'
const controlCsvPath = csvDir + '/' + fullDate + '-control.csv'
// using local copy of extension: https://www.i-dont-care-about-cookies.eu
const pathToExtension = 'extensions/cookies_ext/3.3.0_0'

// Mullvad commands
const turnOffCommand = 'mullvad disconnect'
const turnOnCommand = 'mullvad connect'

// variables
let mullvadIndex = 1
let mullvadPageCount = 0
let controlIndex = 1
let controlPageCount = 0

// waiting
const delay = (ms: number | undefined) => new Promise(resolve => setTimeout(resolve, ms))

// make screenshots directories
fs.mkdir(mullvadScreenshotDir, { recursive: true }, (error) => {
  if (error) throw error
})
fs.mkdir(controlScreenshotDir, { recursive: true }, (error) => {
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
for (let i = 0; i < numberDomains; i++) {
  const row : any = parser.data[i]
  domains.push(row[1])
}

// prepare the CSV file writers
const createCsvWriter = require('csv-writer').createObjectCsvWriter
const mullvadCsvWriter = createCsvWriter({
  path: mullvadCsvPath,
  header: [
    {id: 'id', title: 'ID'},
    {id: 'time', title: 'Time (ms)'},
    {id: 'attempts', title: 'Attempts'},
    {id: 'ogdomain', title: 'Request Domain'},
    {id: 'resdomain', title: 'Response Domain'},
    {id: 'ip', title: 'IP Address'},
    {id: 'status', title: 'HTTP Status Code'},
    {id: 'error', title: 'Error'},
  ]
})
const controlCsvWriter = createCsvWriter({
  path: controlCsvPath,
  header: [
    {id: 'id', title: 'ID'},
    {id: 'time', title: 'Time (ms)'},
    {id: 'attempts', title: 'Attempts'},
    {id: 'ogdomain', title: 'Request Domain'},
    {id: 'resdomain', title: 'Response Domain'},
    {id: 'ip', title: 'IP Address'},
    {id: 'status', title: 'HTTP Status Code'},
    {id: 'error', title: 'Error'},
  ]
})

// create browser instances
const mullvadBrowser = addExtra(vanillaPuppeteer)
  .use(StealthPlugin())
  .use(Adblocker({ blockTrackers: true }))
  .launch({
    headless: false,
    args: [
      `--disable-extensions-except=${pathToExtension}`,
      `--load-extension=${pathToExtension}`,
    ],
  })
const controlBrowser = addExtra(vanillaPuppeteer)
  .use(StealthPlugin())
  .use(Adblocker({ blockTrackers: true }))
  .launch({
    headless: false,
    args: [
      `--disable-extensions-except=${pathToExtension}`,
      `--load-extension=${pathToExtension}`,
    ],
  })

// define workflow for Mullvad
// this is also the function that will control entire script
async function mullvadCrawler() {
  // start browser
  let page = await (await mullvadBrowser).newPage()
  // set up array of domains for control
  let controlDomains = []
  // get session IP address
  // await page.waitForTimeout(5000)
  let response = await page.goto('https://api.ipify.org')
  let ipAddress = await response?.text()

  // start crawling domains
  for (const domain of domains) {

    // limit of requests per setting reached
    if (mullvadIndex % pageLimit == 0) {
      // close current page
      await page.close()
      // reset page count
      mullvadPageCount = 0
      // switch to control
      await controlCrawler(controlDomains)
      // reset controlDomains
      controlDomains = []
      // set up new page to resume crawling
      page = await (await mullvadBrowser).newPage()
      // get session IP address
      // await page.waitForTimeout(5000)
      response = await page.goto('https://api.ipify.org')
      ipAddress = await response?.text()
    }

    // add domain to control list
    controlDomains.push(domain)

    // time request
    const start = process.hrtime.bigint()
    // get complete domain path
    const completeDomain = 'http://www.' + domain
    // retry non-2xx requests up to 3 times
    for (let i = 1; i < requestRetries+1; i++) {
      try {
        // limit of requests per page reached
        if (mullvadPageCount % pageLimit == 0) {
          // close current page
          await page.close()
          // reset page count
          mullvadPageCount = 0
          // set up new page to resume crawling
          page = await (await mullvadBrowser).newPage()
        }
        // update page count
        mullvadPageCount++
        const domainResponse = await page.goto(completeDomain, { waitUntil: 'domcontentloaded', timeout: 15000 })
        // let cookie acceptance extension do its work
        await page.waitForTimeout(2000)
        const statusCode = domainResponse?.status()
        const data = [{
          'id': mullvadIndex, 
          'time': (process.hrtime.bigint() - start) / BigInt(1e+6),
          'attempts': i,
          'ogdomain': completeDomain,
          'resdomain': page.url(),
          'ip': ipAddress, 
          'status': statusCode, 
          'error': 'none'
        }]
        // take screenshot if status code 2xx
        if (statusCode && statusCode > 199 && statusCode < 300) {
          await mullvadCsvWriter.writeRecords(data)
          const screenshotPath = mullvadScreenshotDir + '/' + fullDate + '-' + mullvadIndex + '-' + domain + '.png'
          await page.screenshot({ path: screenshotPath })
          break
        }
        if (i == requestRetries) {
          await mullvadCsvWriter.writeRecords(data)
        }
        else {
          await page.waitForTimeout(3000)
        }
      } catch (error) {
        if (i == requestRetries) {
          const data = [{
            'id': mullvadIndex, 
            'time': (process.hrtime.bigint() - start) / BigInt(1e+6),
            'attempts': i,
            'ogdomain': completeDomain,
            'resdomain': 'none',
            'ip': ipAddress, 
            'status': 0, 
            'error': error.message
          }]
          await mullvadCsvWriter.writeRecords(data)
        }
        else {
          await page.waitForTimeout(3000)
        }
      }
    }
    mullvadIndex++
  }
  // close current page
  await page.close()
  // switch to control
  await controlCrawler(controlDomains)

  // close browser instances
  await (await controlBrowser).close()
  await (await mullvadBrowser).close()
}


async function controlCrawler(controlDomains: string[]) {
  // turn off Mullvad VPN
  await turnOffMullvad()

  // start browser
  let page = await (await controlBrowser).newPage()
  // get session IP address
  // await page.waitForTimeout(5000)
  let response = await page.goto('https://api.ipify.org', { waitUntil: 'domcontentloaded', timeout: 40000 })
  let ipAddress = await response?.text()

  // start crawling domains
  for (const domain of controlDomains) {
    // time request
    const start = process.hrtime.bigint()
    // get complete domain path
    const completeDomain = 'http://www.' + domain
    // retry non-2xx requests up to 3 times
    for (let i = 1; i < requestRetries+1; i++) {
      try {
        // limit of requests per page reached
        if (controlPageCount % pageLimit == 0) {
          // close current page
          await page.close()
          // reset page count
          controlPageCount = 0
          // set up new page to resume crawling
          page = await (await controlBrowser).newPage()
        }
        // update page count
        controlPageCount++
        const domainResponse = await page.goto(completeDomain, { waitUntil: 'domcontentloaded', timeout: 15000 })
        // let cookie acceptance extension do its work
        await page.waitForTimeout(2000)
        const statusCode = domainResponse?.status()
        const data = [{
          'id': controlIndex, 
          'time': (process.hrtime.bigint() - start) / BigInt(1e+6),
          'attempts': i,
          'ogdomain': completeDomain,
          'resdomain': page.url(),
          'ip': ipAddress, 
          'status': statusCode, 
          'error': 'none'
        }]
        // take screenshot if status code 2xx
        if (statusCode && statusCode > 199 && statusCode < 300) {
          await controlCsvWriter.writeRecords(data)
          const screenshotPath = controlScreenshotDir + '/' + fullDate + '-' + controlIndex + '-' + domain + '.png'
          await page.screenshot({ path: screenshotPath })
          break
        }
        if (i == requestRetries) {
          await controlCsvWriter.writeRecords(data)
        }
        else {
          await page.waitForTimeout(3000)
        }
      } catch (error) {
        if (i == requestRetries) {
          const data = [{
            'id': controlIndex, 
            'time': (process.hrtime.bigint() - start) / BigInt(1e+6),
            'attempts': i,
            'ogdomain': completeDomain,
            'resdomain': 'none',
            'ip': ipAddress, 
            'status': 0, 
            'error': error.message
          }]
          await controlCsvWriter.writeRecords(data)
        }
        else {
          await page.waitForTimeout(3000)
        }
      }
    }
    controlIndex++
  }
  // close page
  await page.close()
  // turn on Mullvad VPN
  await turnOnMullvad()
}


async function turnOffMullvad() {
  exec(turnOffCommand, function (err: any, stdout: any, stderr: any) {
    if (err) {
      // node couldn't execute the command
      console.log(err)
      return
    }
  })
  await delay(2000)
}

async function turnOnMullvad() {
  exec(turnOnCommand, function (err: any, stdout: any, stderr: any) {
    if (err) {
      // node couldn't execute the command
      console.log(err)
      return
    }
  })
  await delay(5000)
}

// begin crawl
mullvadCrawler()
