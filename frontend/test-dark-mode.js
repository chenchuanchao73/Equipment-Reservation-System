// Test script for dark mode
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Go to the homepage
    await page.goto('http://localhost:8080/');
    
    // Wait for page to load
    await page.waitForSelector('.feature-card', { timeout: 10000 });
    
    console.log('Page loaded successfully. Checking dark mode toggle...');
    
    // Take screenshot before toggle
    await page.screenshot({ path: 'before-dark-mode.png' });
    
    // Toggle dark mode (assuming there's a button with class .dark-mode-toggle)
    const darkModeToggle = await page.$('.dark-mode-toggle');
    if (darkModeToggle) {
      await darkModeToggle.click();
      console.log('Dark mode toggled');
      
      // Wait for dark mode to apply
      await page.waitForTimeout(1000);
      
      // Take screenshot after toggle
      await page.screenshot({ path: 'after-dark-mode.png' });
      
      console.log('Dark mode test completed. Check the screenshots to verify changes.');
    } else {
      console.log('Could not find dark mode toggle button');
    }
  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    // Pause to see the results
    await page.waitForTimeout(5000);
    await browser.close();
  }
})(); 