import puppeteer from 'puppeteer-extra'
import StealthPlugin from 'puppeteer-extra-plugin-stealth'

puppeteer
  .use(StealthPlugin())
  .launch({ headless: true })
  .then(async browser => {
    const page = await browser.newPage()
    const response = await page.goto('https://api.ipify.org')
    const ipAddress = await response?.text()
    console.log(response?.request().headers())
    console.log(ipAddress)
    await page.waitForTimeout(2000)
    await page.screenshot({ path: 'data/screenshots/stealth.png', fullPage: true })
    await browser.close()
  })
