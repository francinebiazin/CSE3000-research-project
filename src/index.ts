import puppeteer from 'puppeteer-extra'
import StealthPlugin from 'puppeteer-extra-plugin-stealth'
import Adblocker from 'puppeteer-extra-plugin-adblocker'
import * as fs from 'fs'
import * as papaparse from 'papaparse'
import { Browser } from 'puppeteer'

// get date info
let datetime = new Date()
const date = datetime.getDate()
const month = datetime.getMonth() + 1
const year = datetime.getFullYear()
const fullDate = year + "-" + month + "-" + date

// contants
const numberDomains = 100
const browserLimit = 50
const requestRetries = 3
const timeouts = [20000, 30000, 35000, 40000]
const clearoutLimit = 10
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

// load the domains from Alexa Top 1M list
const domainsPath = 'domains/top-1m.csv'
const parser = papaparse.parse(fs.readFileSync(domainsPath, { encoding: 'utf-8' }))
const domains: string[] = []
let k = 0
let added = 0
while (added < numberDomains) {
  const row : any = parser.data[k]
  const domain = row[1]
  // skip problematic domains
  if (domain.includes('oeeee.com') || domain.includes('taleo.net') || domain.includes('tamin.ir') || domain.includes('support.wix.com')) {
    k++
    continue
  }
  domains.push(domain)
  k++
  added++
}

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
    {id: 'links', title: 'Links Found'},
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
    // start browser
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
    const start = index - 1
    const end = Math.min(start + browserLimit, numberDomains)
    // start crawling domains
    for (let j = start; j < end; j++) {
      page = await browser.newPage()
      page.removeAllListeners('requests')
      // time request
      const start = process.hrtime.bigint()
      // get complete domain path
      const completeDomain = 'http://' + domains[j]
      // links for subpages
      let links: string[] = []
      // retry non-2xx requests up to 3 times
      for (let i = 1; i < requestRetries+1; i++) {
        try {
          // reset links
          links = []
          const domainResponse = await page.goto(completeDomain, { waitUntil: 'domcontentloaded', timeout: timeouts[i] })
          // let extensions do their work
          await page.waitForTimeout(6000)
          let statusCode = domainResponse?.status()
          // check empty response
          if (typeof statusCode == 'undefined') {
            // special value so a screenshot will be taken, but we know something was not quite right
            statusCode = 215
          }
          // sort out timestamp for request
          datetime = new Date()
          const hours = datetime.getHours()
          const minutes = datetime.getMinutes()
          const seconds = datetime.getSeconds()
          const timeStamp = hours + ":" + minutes + ":" + seconds
          // take screenshot if status code 2xx
          if (typeof statusCode !== 'undefined' && statusCode > 199 && statusCode < 300) {
            const screenshotPath = screenshotDir + '/' + fullDate + '-' + index + '-' + domains[j] + '-0.png'
            await page.screenshot({ path: screenshotPath })
            // get links
            const hrefs = await page.evaluate(() => 
              Array.from(document.querySelectorAll("a")).map(anchor => anchor.href)
            )
            links = hrefs.filter(link => link.includes(domains[j] + '/') && link != page.url() && link != (page.url() + '/#'))
            // links.map(link => console.log(link))
          }
          const data = [{
            'id': index,
            'subpage': 0,
            'time': timeStamp,
            'duration': (process.hrtime.bigint() - start) / BigInt(1e+6),
            'attempts': i,
            'ogdomain': completeDomain,
            'resdomain': page.url(),
            'links': links.length,
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
              'subpage': 0,
              'time': timeStamp,
              'duration': (process.hrtime.bigint() - start) / BigInt(1e+6),
              'attempts': i,
              'ogdomain': completeDomain,
              'resdomain': 'none',
              'links': links.length,
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
      domainIndex++
      // clear cache & cookies every clearoutLimit requests
      if (index % clearoutLimit == 0) {
        const client = await page.target().createCDPSession();
        await client.send('Network.clearBrowserCookies');
        await client.send('Network.clearBrowserCache');
      }
      // await page.waitForTimeout(1000)
      await page.close()
      // request subpages
      if (links.length > 0) {
        await requestSubpages(browser, links, domains[j], ipAddress)
      }
    }

    // close browser instance
    await browser.close()

  })
}

async function requestSubpages(browser: Browser, subpages: string[], domain: string, ipAddress: string | undefined) {
  let page = await browser.newPage()
  page.removeAllListeners('requests')
  // request 2 subpages
  for (let j = 0; j < 2; j++) {
    // time request
    const start = process.hrtime.bigint()
    // retry non-2xx requests up to 3 times
    for (let i = 1; i < requestRetries+1; i++) {
      try {
        const domainResponse = await page.goto(subpages[j], { waitUntil: 'domcontentloaded', timeout: timeouts[i] })
        // let extensions do their work
        await page.waitForTimeout(6000)
        let statusCode = domainResponse?.status()
        // check empty response
        if (typeof statusCode == 'undefined') {
          // special value so a screenshot will be taken, but we know something was not quite right
          statusCode = 215
        }
        // sort out timestamp for request
        datetime = new Date()
        const hours = datetime.getHours()
        const minutes = datetime.getMinutes()
        const seconds = datetime.getSeconds()
        const timeStamp = hours + ":" + minutes + ":" + seconds
        // take screenshot if status code 2xx
        if (typeof statusCode !== 'undefined' && statusCode > 199 && statusCode < 300) {
          const screenshotPath = screenshotDir + '/' + fullDate + '-' + index + '-' + domain + '-' + (j+1) + '.png'
          await page.screenshot({ path: screenshotPath })
        }
        const data = [{
          'id': index,
          'subpage': j + 1,
          'time': timeStamp,
          'duration': (process.hrtime.bigint() - start) / BigInt(1e+6),
          'attempts': i,
          'ogdomain': subpages[j],
          'resdomain': page.url(),
          'links': 0,
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
            'subpage': j + 1,
            'time': timeStamp,
            'duration': (process.hrtime.bigint() - start) / BigInt(1e+6),
            'attempts': i,
            'ogdomain': subpages[j],
            'resdomain': 'none',
            'links': 0,
            'ip': ipAddress, 
            'status': 0, 
            'error': error.message
          }]
          await csvWriter.writeRecords(data)
        }
        else {
          await page.waitForTimeout(3000)
        }
      }
    }
    index++
  }
  await page.close()
}

async function run() {
  while (domainIndex < numberDomains) {
    try {
      await runBrowser()
    } catch (error) {
      console.log('Error at request index ' + String(index))
      await delay(5000)
    }
  }
}

run()
