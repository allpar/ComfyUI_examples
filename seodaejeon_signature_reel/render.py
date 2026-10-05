import asyncio, base64, os, sys, subprocess, time, pathlib
from playwright.async_api import async_playwright
HERE = pathlib.Path(__file__).parent.resolve()
CHROME = os.environ.get("CHROME_PATH", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
async def main():
    mode = sys.argv[1]; hi = os.environ.get("HI") == "1"
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, args=["--allow-file-access-from-files", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        VERT = os.environ.get("VERT") == "1"
        pg = await b.new_page(viewport={"width": 1080, "height": 1920} if VERT else {"width": 1920, "height": 1080})
        pg.on("console", lambda m: print("console:", m.text)); pg.on("pageerror", lambda e: print("pageerror:", e))
        await pg.goto((HERE / ("reel_v.html" if VERT else "reel.html")).as_uri() + ("?hi=1" if hi else ""))
        await pg.evaluate("window.ready")
        if mode == "stills":
            for t in map(float, sys.argv[2:]):
                d = await pg.evaluate(f"frame({t})")
                (HERE / f"s{'v' if VERT else ''}_{t:05.2f}.png").write_bytes(base64.b64decode(d.split(",")[1]))
        else:
            fps = int(sys.argv[2]); out = sys.argv[3]; n = 15 * fps
            ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
                                   "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
            t0 = time.time()
            for i in range(n):
                d = await pg.evaluate(f"frame({i / fps})")
                ff.stdin.write(base64.b64decode(d.split(",")[1]))
                if i % 60 == 0: print(i, round(time.time() - t0, 1), flush=True)
            ff.stdin.close(); ff.wait()
        await b.close()
asyncio.run(main())
