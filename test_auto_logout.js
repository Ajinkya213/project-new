const puppeteer = require('puppeteer');

async function testAutoLogout() {
    console.log('🚀 Starting auto-logout test...');

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null,
        args: ['--start-maximized']
    });

    const page = await browser.newPage();

    try {
        // Navigate to the application
        console.log('📱 Navigating to application...');
        await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });

        // Wait for the page to load
        await page.waitForTimeout(2000);

        // Check if we're on login page
        const loginForm = await page.$('form');
        if (loginForm) {
            console.log('🔐 Found login form, attempting to login...');

            // Fill in login credentials (you may need to adjust these)
            await page.type('input[name="username"]', 'testuser');
            await page.type('input[name="password"]', 'testpass123');

            // Click login button
            await page.click('button[type="submit"]');

            // Wait for login to complete
            await page.waitForTimeout(3000);
        }

        // Check if we're authenticated
        const isAuthenticated = await page.evaluate(() => {
            return localStorage.getItem('access_token') !== null;
        });

        if (!isAuthenticated) {
            console.log('❌ Not authenticated, cannot proceed with test');
            return;
        }

        console.log('✅ Successfully authenticated');

        // Get initial auth state
        let initialAuthState = await page.evaluate(() => {
            return {
                token: localStorage.getItem('access_token'),
                user: localStorage.getItem('user'),
                timestamp: Date.now()
            };
        });

        console.log('📊 Initial auth state:', {
            hasToken: !!initialAuthState.token,
            timestamp: new Date(initialAuthState.timestamp).toLocaleTimeString()
        });

        // Simulate tab switching multiple times
        console.log('🔄 Starting tab switch simulation...');

        for (let i = 1; i <= 5; i++) {
            console.log(`\n🔄 Tab switch test ${i}/5`);

            // Simulate tab becoming hidden
            await page.evaluate(() => {
                Object.defineProperty(document, 'hidden', {
                    value: true,
                    writable: true
                });
                document.dispatchEvent(new Event('visibilitychange'));
            });

            await page.waitForTimeout(1000);

            // Simulate tab becoming visible
            await page.evaluate(() => {
                Object.defineProperty(document, 'hidden', {
                    value: false,
                    writable: true
                });
                document.dispatchEvent(new Event('visibilitychange'));
            });

            await page.waitForTimeout(2000);

            // Check auth state after tab switch
            const authState = await page.evaluate(() => {
                return {
                    token: localStorage.getItem('access_token'),
                    user: localStorage.getItem('user'),
                    timestamp: Date.now()
                };
            });

            console.log(`📊 Auth state after switch ${i}:`, {
                hasToken: !!authState.token,
                tokenChanged: authState.token !== initialAuthState.token,
                timestamp: new Date(authState.timestamp).toLocaleTimeString()
            });

            // Check if user is still authenticated
            const stillAuthenticated = await page.evaluate(() => {
                // Check if we're still on a protected page
                const protectedElements = document.querySelectorAll('[data-testid="userboard"], [data-testid="chat"], .userboard');
                return protectedElements.length > 0 || window.location.pathname.includes('/userboard');
            });

            if (!stillAuthenticated) {
                console.log(`❌ AUTO-LOGOUT DETECTED on switch ${i}!`);
                console.log('🔍 Checking if redirected to login...');

                const currentUrl = page.url();
                console.log('📍 Current URL:', currentUrl);

                if (currentUrl.includes('/login') || currentUrl.includes('/auth')) {
                    console.log('❌ FAILED: User was logged out during tab switching');
                    return false;
                }
            } else {
                console.log(`✅ Still authenticated after switch ${i}`);
            }

            // Wait before next switch
            await page.waitForTimeout(1000);
        }

        // Final auth check
        const finalAuthState = await page.evaluate(() => {
            return {
                token: localStorage.getItem('access_token'),
                user: localStorage.getItem('user'),
                timestamp: Date.now()
            };
        });

        console.log('\n📊 Final auth state:', {
            hasToken: !!finalAuthState.token,
            tokenChanged: finalAuthState.token !== initialAuthState.token,
            timestamp: new Date(finalAuthState.timestamp).toLocaleTimeString()
        });

        if (finalAuthState.token) {
            console.log('✅ SUCCESS: No auto-logout detected during tab switching!');
            return true;
        } else {
            console.log('❌ FAILED: Auto-logout still occurs during tab switching');
            return false;
        }

    } catch (error) {
        console.error('❌ Test failed with error:', error);
        return false;
    } finally {
        console.log('🔚 Closing browser...');
        await browser.close();
    }
}

// Run the test
testAutoLogout().then(result => {
    if (result) {
        console.log('\n🎉 AUTO-LOGOUT ISSUE IS RESOLVED!');
        process.exit(0);
    } else {
        console.log('\n💥 AUTO-LOGOUT ISSUE STILL EXISTS!');
        process.exit(1);
    }
}).catch(error => {
    console.error('💥 Test script failed:', error);
    process.exit(1);
}); 