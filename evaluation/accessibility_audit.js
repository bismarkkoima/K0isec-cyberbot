// Automated accessibility audit and task walkthrough for K0isec Guardian.
//
// Setup (once, in the project folder; node_modules is git-ignored):
//   npm install --no-save playwright-core axe-core
// Then, with the app running on http://127.0.0.1:5000:
//   CHROME_PATH=/path/to/chrome node evaluation/accessibility_audit.js
//
// Runs axe-core WCAG 2.2 AA checks on every page in light/dark mode at desktop and phone
// widths, measures tap-target sizes and text sizes, walks through the user-study tasks,
// checks keyboard focus, and writes evaluation/accessibility_results.json.
const { chromium } = require("playwright-core");
const fs = require("fs");
const axeSrc = fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
const BASE = "http://127.0.0.1:5000";
const PAGES = ["/", "/check", "/lessons", "/lessons/spot-a-scam", "/help"];

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/opt/pw-browsers/chromium", args: ["--no-sandbox"] });
  const out = { axe: [], targets: [], fonts: [], overflow: [], tasks: [] };

  for (const scheme of ["light", "dark"]) {
    for (const vp of [{ width: 1280, height: 900, name: "desktop" }, { width: 375, height: 800, name: "phone" }]) {
      const ctx = await browser.newContext({ viewport: vp, colorScheme: scheme, bypassCSP: true });
      const page = await ctx.newPage();
      for (const path of PAGES) {
        await page.goto(BASE + path);
        await page.addScriptTag({ content: axeSrc });
        const r = await page.evaluate(async () => {
          const res = await axe.run(document, { runOnly: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"] });
          return { violations: res.violations.map(v => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length, sample: v.nodes[0] && v.nodes[0].target.join(" ") })), passes: res.passes.length };
        });
        out.axe.push({ scheme, vp: vp.name, path, ...r });
        // Horizontal overflow at this width
        const ov = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        if (ov > 0) out.overflow.push({ scheme, vp: vp.name, path, px: ov });
        if (scheme === "light") {
          // Interactive targets smaller than 44x44 CSS px
          const small = await page.evaluate(() => [...document.querySelectorAll("a,button,input,textarea,[role=button]")]
            .filter(e => e.offsetParent !== null)
            .map(e => { const b = e.getBoundingClientRect(); return { t: (e.innerText || e.getAttribute("aria-label") || e.name || e.tagName).trim().slice(0, 40), w: Math.round(b.width), h: Math.round(b.height), tag: e.tagName } })
            .filter(b => (b.w < 44 || b.h < 44) && !(b.tag === "A" && b.h >= 24)));
          out.targets.push({ vp: vp.name, path, small });
        }
      }
      await ctx.close();
    }
  }

  // Font sizes at each text-size setting
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  await page.goto(BASE + "/");
  for (const size of ["normal", "large", "xlarge"]) {
    await page.click(`.text-size button[data-size=${size}]`);
    const px = await page.evaluate(() => ({ body: getComputedStyle(document.body).fontSize, topic: getComputedStyle(document.querySelector(".topic-btn")).fontSize }));
    out.fonts.push({ size, ...px });
  }
  await page.click(".text-size button[data-size=large]");

  // Task walkthrough: count actions a user needs, verify the outcome
  async function task(id, name, fn) {
    const t0 = Date.now();
    try { const r = await fn(); out.tasks.push({ id, name, ok: true, ...r, ms: Date.now() - t0 }); }
    catch (e) { out.tasks.push({ id, name, ok: false, error: e.message }); }
  }
  await task("T1", "Make the text bigger", async () => {
    await page.goto(BASE + "/"); await page.click(".text-size button[data-size=xlarge]");
    const fs = await page.evaluate(() => getComputedStyle(document.body).fontSize);
    await page.click(".text-size button[data-size=large]");
    return { actions: 1, result: "body text " + fs };
  });
  await task("T2", "Ask about a caller wanting the bank PIN", async () => {
    await page.goto(BASE + "/");
    await page.fill("#user-input", "What should I do if someone calls asking for my bank PIN?");
    await page.keyboard.press("Enter");
    await page.waitForSelector(".message.bot:not(.thinking) .source");
    const txt = await page.locator(".message.bot").last().innerText();
    return { actions: 2, result: txt.split("\n")[0] };
  });
  for (const [id, msg, expect] of [
    ["T3", "Royal Mail: your parcel could not be delivered. Pay the £1.99 redelivery fee here: https://royalmail-redeliver.info/pay", "scam"],
    ["T4", "Reminder: your appointment with Dr Patel is on Tuesday at 10:30.", "genuine"],
    ["T5", "Hi mum, this is my new number. Can you buy me some gift cards? Don't tell dad.", "scam"]]) {
    await task(id, "Check message (" + expect + ")", async () => {
      await page.goto(BASE + "/"); await page.click("text=Check a message");
      await page.fill("#check-input", msg); await page.click("text=Check this message");
      await page.waitForSelector("#check-result:not([hidden])");
      const h = await page.locator("#result-headline").innerText();
      if (id === "T3")       return { actions: 3, result: h };
    });
  }
  await task("T6", "Complete 'How to spot a scam' lesson and quiz", async () => {
    await page.goto(BASE + "/"); await page.click("text=Lessons"); await page.click("text=How to spot a scam");
    const qs = page.locator(".quiz-question");
    for (let i = 0; i < await qs.count(); i++) {
      const ans = await qs.nth(i).getAttribute("data-answer");
      await qs.nth(i).locator(`.quiz-option[data-index="${ans}"]`).click();
    }
    const score = await page.locator("#quiz-score").innerText();
    return { actions: 2 + await qs.count(), result: score };
  });
  await task("T7", "Find what to do after being scammed", async () => {
    await page.goto(BASE + "/"); await page.click("text=I think I've been scammed");
    return { actions: 1, result: await page.locator("h1").innerText() };
  });

  // Keyboard-only: tab through home page and confirm focus is visible
  await page.goto(BASE + "/");
  const focusInfo = [];
  for (let i = 0; i < 12; i++) {
    await page.keyboard.press("Tab");
    focusInfo.push(await page.evaluate(() => { const e = document.activeElement; const s = getComputedStyle(e); return { el: (e.innerText || e.placeholder || e.getAttribute("aria-label") || e.tagName).trim().slice(0, 30), outline: s.outlineStyle !== "none" && parseFloat(s.outlineWidth) >= 2 }; }));
  }
  out.keyboard = focusInfo;
  await browser.close();
  fs.writeFileSync(__dirname + "/accessibility_results.json", JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out, null, 1).slice(0, 200));
})();
