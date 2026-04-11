import fs from "node:fs";
import path from "node:path";
import http from "node:http";
import { fileURLToPath } from "node:url";

import puppeteer from "puppeteer-core";
import { PNG } from "pngjs";
import gifenc from "gifenc";

const { GIFEncoder, quantize, applyPalette } = gifenc;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "..");

const args = parseArgs(process.argv.slice(2));
const siteDir = path.resolve(__dirname, args.siteDir ?? "./rollmydice_app");
const outputDir = path.resolve(__dirname, args.outputDir ?? "./outputs");
const outputName = args.outputName ?? defaultOutputName(args);
const outputPath = path.resolve(outputDir, outputName);
const viewportWidth = Number(args.width ?? 900);
const viewportHeight = Number(args.height ?? 1400);
const durationMs = Number(args.duration ?? 2400);
const fps = Number(args.fps ?? 16);
const maxAnimationWaitMs = Number(args.maxAnimationWait ?? 2000);
const timeoutMs = Number(args.timeout ?? 60000);
const frameDelay = Math.max(20, Math.round(1000 / fps));
const totalFrames = Math.max(1, Math.ceil(durationMs / frameDelay));
const browserPath = resolveBrowserPath(args.browser);
const platform = process.platform;
const diceType = args.diceType ?? "D6";
const diceCount = Number(args.count ?? 1);
const launchOptions = createLaunchOptions({
  browserPath,
  platform,
  timeoutMs,
  viewportWidth,
  viewportHeight,
});

if (!fs.existsSync(siteDir)) {
  throw new Error(`Site directory not found: ${siteDir}`);
}

if (!browserPath) {
  throw new Error("Could not find a local Edge/Chrome executable. Pass --browser=/path/to/browser.exe");
}

fs.mkdirSync(outputDir, { recursive: true });

const server = createStaticServer(siteDir);

try {
  const { port } = await listen(server);
  const baseUrl = `http://127.0.0.1:${port}/index.html`;
  const browser = await puppeteer.launch(launchOptions);

  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(timeoutMs);
    page.setDefaultNavigationTimeout(timeoutMs);
    attachPageDiagnostics(page);
    await page.goto(baseUrl, { waitUntil: "domcontentloaded", timeout: timeoutMs });
    await waitForDiceApp(page, timeoutMs);
    await configureDice(page, { diceType, diceCount });
    const clip = await getCaptureClip(page);
    const baselineFrame = await captureClipPng(page, clip);
    await triggerRoll(page);
    await waitForAnimationStart(page, clip, baselineFrame, maxAnimationWaitMs);
    const frames = await captureFrames(page, clip, totalFrames, frameDelay);
    await writeGif(frames, outputPath, frameDelay);
    const result = await readRollResults(page, diceCount);

    process.stdout.write(
      `${JSON.stringify({
        gif_path: outputPath,
        results: result.results,
        total: result.total,
        dice_type: diceType,
        dice_count: diceCount,
      })}\n`,
    );
  } finally {
    await browser.close();
  }
} finally {
  server.close();
}

function parseArgs(argv) {
  const parsed = {};
  for (const item of argv) {
    if (!item.startsWith("--")) continue;
    const [, key, rawValue] = item.match(/^--([^=]+)(?:=(.*))?$/) ?? [];
    parsed[key] = rawValue ?? "true";
  }
  return parsed;
}

function defaultOutputName(args) {
  const type = (args.diceType ?? "D6").toLowerCase();
  const count = Number(args.count ?? 1);
  return `${type}-${count}-${Date.now()}.gif`;
}

function resolveBrowserPath(explicitPath) {
  const candidates = [
    explicitPath,
    process.env.PUPPETEER_EXECUTABLE_PATH,
    process.env.BROWSER,
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/snap/bin/chromium",
  ].filter(Boolean);

  return candidates.find((candidate) => fs.existsSync(candidate));
}

function createLaunchOptions({
  browserPath,
  platform,
  timeoutMs,
  viewportWidth,
  viewportHeight,
}) {
  const args = [
    "--allow-file-access-from-files",
    "--autoplay-policy=no-user-gesture-required",
    "--disable-background-timer-throttling",
    "--disable-dev-shm-usage",
    "--disable-renderer-backgrounding",
    "--mute-audio",
  ];
  let headless = true;
  const hasDisplay = Boolean(process.env.DISPLAY || process.env.WAYLAND_DISPLAY);

  if (platform === "linux") {
    headless = hasDisplay ? false : true;
    args.push(
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--enable-webgl",
      "--enable-unsafe-swiftshader",
      "--ignore-gpu-blocklist",
      "--use-angle=swiftshader",
      "--use-gl=egl",
      "--disable-gpu-sandbox",
    );
    if (!hasDisplay) {
      args.push("--headless=chrome");
    }
  }

  return {
    executablePath: browserPath,
    headless,
    timeout: timeoutMs,
    dumpio: true,
    defaultViewport: {
      width: viewportWidth,
      height: viewportHeight,
      deviceScaleFactor: 1,
    },
    args,
  };
}

function createStaticServer(rootDir) {
  const mimeTypes = {
    ".css": "text/css; charset=utf-8",
    ".gif": "image/gif",
    ".html": "text/html; charset=utf-8",
    ".ico": "image/x-icon",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".manifest": "application/manifest+json; charset=utf-8",
    ".map": "application/json; charset=utf-8",
    ".mp3": "audio/mpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".webmanifest": "application/manifest+json; charset=utf-8",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
  };

  return http.createServer((req, res) => {
    const requestUrl = new URL(req.url, "http://127.0.0.1");
    let pathname = decodeURIComponent(requestUrl.pathname);
    if (pathname === "/") pathname = "/index.html";

    const absolutePath = path.resolve(rootDir, `.${pathname}`);
    if (!absolutePath.startsWith(rootDir)) {
      res.writeHead(403).end("Forbidden");
      return;
    }

    let finalPath = absolutePath;
    if (fs.existsSync(finalPath) && fs.statSync(finalPath).isDirectory()) {
      finalPath = path.join(finalPath, "index.html");
    }

    if (!fs.existsSync(finalPath)) {
      res.writeHead(404).end("Not found");
      return;
    }

    const extension = path.extname(finalPath).toLowerCase();
    res.writeHead(200, {
      "Content-Type": mimeTypes[extension] ?? "application/octet-stream",
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "no-store",
    });
    fs.createReadStream(finalPath).pipe(res);
  });
}

function listen(server) {
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      resolve(server.address());
    });
  });
}

async function waitForDiceApp(page, timeoutMs) {
  try {
    await page.waitForFunction(() => {
      const canvas = document.querySelector("canvas");
      const buttons = [...document.querySelectorAll("button")];
      return Boolean(canvas && buttons.some((button) => /roll/i.test(button.textContent || "")));
    }, { timeout: timeoutMs });
    await page.waitForSelector("canvas", { timeout: timeoutMs });
    await page.waitForFunction(() => {
      const canvas = document.querySelector("canvas");
      if (!canvas) return false;
      const rect = canvas.getBoundingClientRect();
      return rect.width > 100 && rect.height > 100;
    }, { timeout: timeoutMs });
  } catch (error) {
    const pageState = await collectPageState(page);
    throw new Error(
      `Dice app did not become ready within ${timeoutMs}ms. State: ${JSON.stringify(pageState)}`,
      { cause: error },
    );
  }

  await sleep(1000);
}

function attachPageDiagnostics(page) {
  page.on("console", (message) => {
    const type = message.type().toUpperCase();
    process.stderr.write(`[page:${type}] ${message.text()}\n`);
  });
  page.on("pageerror", (error) => {
    process.stderr.write(`[page:error] ${error.stack || error.message}\n`);
  });
  page.on("requestfailed", (request) => {
    process.stderr.write(
      `[page:requestfailed] ${request.method()} ${request.url()} ${request.failure()?.errorText || "unknown"}\n`,
    );
  });
}

async function collectPageState(page) {
  return page.evaluate(() => {
    const canvas = document.querySelector("canvas");
    const buttons = [...document.querySelectorAll("button")];
    const bodyText = (document.body?.innerText || "").trim().replace(/\s+/g, " ").slice(0, 300);
    const canvasRect = canvas?.getBoundingClientRect();

    return {
      title: document.title,
      readyState: document.readyState,
      buttonTexts: buttons.map((button) => (button.textContent || "").trim()).filter(Boolean),
      canvasCount: document.querySelectorAll("canvas").length,
      canvasRect: canvasRect
        ? {
            width: Math.round(canvasRect.width),
            height: Math.round(canvasRect.height),
          }
        : null,
      bodyText,
    };
  });
}

async function configureDice(page, { diceType, diceCount }) {
  await page.evaluate((label) => {
    const buttons = [...document.querySelectorAll("button")];
    const dieButton = buttons.find((button) => /^D\d+$/i.test((button.textContent || "").trim()));
    const directTarget = buttons.find((button) => (button.textContent || "").trim() === label);

    if (directTarget) {
      directTarget.click();
      return;
    }

    if (dieButton) {
      dieButton.click();
    }
  }, diceType);

  await page.waitForFunction((label) => {
    const buttons = [...document.querySelectorAll("button")];
    return buttons.some((button) => (button.textContent || "").trim() === label);
  }, {}, diceType);

  await page.evaluate((label) => {
    const buttons = [...document.querySelectorAll("button")];
    const target = buttons.find((button) => (button.textContent || "").trim() === label);
    target?.click();
  }, diceType);

  await page.waitForFunction((label) => {
    const buttons = [...document.querySelectorAll("button")];
    const dieButton = buttons.find((button) => /^D\d+$/i.test((button.textContent || "").trim()));
    return (dieButton?.textContent || "").trim() === label;
  }, {}, diceType);

  const currentCount = await page.evaluate(() => {
    const heading = [...document.querySelectorAll("h1")].find((node) => /^\d+\s+(Die|Dice)$/i.test((node.textContent || "").trim()));
    if (!heading) return 1;
    const match = (heading.textContent || "").match(/^\s*(\d+)/);
    return match ? Number(match[1]) : 1;
  });

  const diff = diceCount - currentCount;
  if (diff !== 0) {
    await page.evaluate((direction, steps) => {
      const heading = [...document.querySelectorAll("h1")].find((node) => /^\d+\s+(Die|Dice)$/i.test((node.textContent || "").trim()));
      const parent = heading?.parentElement;
      const buttons = parent ? [...parent.querySelectorAll("button")] : [];
      const target = direction > 0 ? buttons.at(-1) : buttons[0];

      for (let index = 0; index < steps; index += 1) {
        target?.click();
      }
    }, Math.sign(diff), Math.abs(diff));

    await page.waitForFunction((expectedCount) => {
      const heading = [...document.querySelectorAll("h1")].find((node) => /^\d+\s+(Die|Dice)$/i.test((node.textContent || "").trim()));
      if (!heading) return false;
      const match = (heading.textContent || "").match(/^\s*(\d+)/);
      return match ? Number(match[1]) === expectedCount : false;
    }, {}, diceCount);
  }

  await sleep(300);
}

async function getCaptureClip(page) {
  const box = await page.evaluate(() => {
    const canvas = document.querySelector("canvas");
    if (!canvas) return null;

    const rect = canvas.getBoundingClientRect();
    const top = Math.max(0, rect.top - 40);
    const left = Math.max(0, rect.left - 24);
    const right = Math.min(window.innerWidth, rect.right + 24);
    const bottom = Math.min(window.innerHeight, rect.bottom + 80);

    return {
      x: left,
      y: top,
      width: right - left,
      height: bottom - top,
    };
  });

  if (!box) {
    throw new Error("Could not locate dice canvas clip region");
  }

  return {
    x: Math.round(box.x),
    y: Math.round(box.y),
    width: Math.round(box.width),
    height: Math.round(box.height),
  };
}

async function triggerRoll(page) {
  await page.evaluate(() => {
    const buttons = [...document.querySelectorAll("button")];
    const rollButton = buttons.find((button) => /roll/i.test(button.textContent || ""));
    if (!rollButton) {
      throw new Error("Roll button not found");
    }
    rollButton.click();
  });
}

async function captureFrames(page, clip, totalFrames, delayMs) {
  const frames = [];
  for (let index = 0; index < totalFrames; index += 1) {
    frames.push(await captureClipPng(page, clip));
    if (index < totalFrames - 1) {
      await sleep(delayMs);
    }
  }
  return frames;
}

async function captureClipPng(page, clip) {
  const pngBuffer = await page.screenshot({
    type: "png",
    clip,
    captureBeyondViewport: false,
  });
  return PNG.sync.read(pngBuffer);
}

async function waitForAnimationStart(page, clip, baselineFrame, timeoutMs) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    await sleep(80);
    const currentFrame = await captureClipPng(page, clip);
    if (framesDifferEnough(baselineFrame, currentFrame)) {
      return;
    }
  }
}

function framesDifferEnough(firstFrame, secondFrame) {
  if (firstFrame.width !== secondFrame.width || firstFrame.height !== secondFrame.height) {
    return true;
  }

  const totalPixels = firstFrame.width * firstFrame.height;
  const sampleStride = Math.max(1, Math.floor(totalPixels / 2500));
  let changedSamples = 0;
  let totalSamples = 0;

  for (let pixelIndex = 0; pixelIndex < totalPixels; pixelIndex += sampleStride) {
    const offset = pixelIndex * 4;
    const delta =
      Math.abs(firstFrame.data[offset] - secondFrame.data[offset]) +
      Math.abs(firstFrame.data[offset + 1] - secondFrame.data[offset + 1]) +
      Math.abs(firstFrame.data[offset + 2] - secondFrame.data[offset + 2]) +
      Math.abs(firstFrame.data[offset + 3] - secondFrame.data[offset + 3]);

    totalSamples += 1;
    if (delta > 24) {
      changedSamples += 1;
    }
  }

  return changedSamples / Math.max(1, totalSamples) > 0.02;
}

async function writeGif(frames, outputFile, delayMs) {
  if (!frames.length) {
    throw new Error("No frames captured");
  }

  const width = frames[0].width;
  const height = frames[0].height;
  const encoder = GIFEncoder();

  for (const frame of frames) {
    const palette = quantize(frame.data, 256, { format: "rgba4444" });
    const index = applyPalette(frame.data, palette, { format: "rgba4444" });
    encoder.writeFrame(index, width, height, {
      palette,
      delay: Math.max(2, Math.round(delayMs / 10)),
    });
  }

  encoder.finish();
  fs.writeFileSync(outputFile, Buffer.from(encoder.bytes()));
}

async function readRollResults(page, diceCount) {
  await sleep(200);
  const result = await page.evaluate((expectedCount) => {
    const nodes = [...document.querySelectorAll("div, span, p, h1, h2")];
    const visible = nodes
      .map((node) => {
        const text = (node.textContent || "").trim();
        const style = getComputedStyle(node);
        const rect = node.getBoundingClientRect();
        return {
          text,
          display: style.display,
          visibility: style.visibility,
          opacity: Number(style.opacity || "1"),
          fontSize: Number.parseFloat(style.fontSize || "0"),
          fontWeight: Number.parseInt(style.fontWeight || "400", 10) || 400,
          top: rect.top,
          left: rect.left,
          width: rect.width,
          height: rect.height,
        };
      })
      .filter((item) => item.text && item.display !== "none" && item.visibility !== "hidden" && item.opacity > 0 && item.width > 0 && item.height > 0);

    const totalCandidate = visible
      .filter((item) => /^\d+$/.test(item.text) && item.fontWeight >= 600 && item.fontSize >= 28)
      .sort((a, b) => b.fontSize - a.fontSize || a.top - b.top)[0];

    const breakdownCandidate = visible
      .filter((item) => /^\d+(?:\s*\+\s*\d+)+$/.test(item.text) && item.fontWeight >= 600)
      .sort((a, b) => b.fontSize - a.fontSize || a.top - b.top)[0];

    let results = [];
    if (breakdownCandidate) {
      results = breakdownCandidate.text.split("+").map((part) => Number(part.trim())).filter((value) => Number.isFinite(value));
    }

    const total = totalCandidate ? Number(totalCandidate.text) : results.reduce((sum, value) => sum + value, 0);
    if (!results.length && Number.isFinite(total)) {
      results = [total];
    }

    if (results.length > expectedCount) {
      results = results.slice(0, expectedCount);
    }

    return {
      results,
      total,
    };
  }, diceCount);

  if (!Array.isArray(result.results) || !result.results.length) {
    throw new Error("Could not parse roll results from the page");
  }

  return result;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
