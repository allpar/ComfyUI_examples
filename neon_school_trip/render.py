import asyncio, base64, os, sys, subprocess, time
from playwright.async_api import async_playwright
import pathlib
HERE = pathlib.Path(__file__).parent.resolve()
async def main(mode, times):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("CHROME_PATH"), args=["--allow-file-access-from-files","--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width":1920,"height":1080})
        pg.on("console", lambda m: print("console:", m.text))
        pg.on("pageerror", lambda e: print("pageerror:", e))
        await pg.goto((HERE/"index.html").as_uri())
        await pg.evaluate("window.ready")
        if mode == "stills":
            for t in times:
                d = await pg.evaluate(f"frame({t})")
                (HERE/f"still_{t:05.2f}.png").write_bytes(base64.b64decode(d.split(",")[1]))
        else:
            fps=30; n=15*fps
            ff = subprocess.Popen(["ffmpeg","-v","error","-y","-f","image2pipe","-framerate",str(fps),"-i","-",
                "-c:v","libx264","-preset","slow","-crf","16","-pix_fmt","yuv420p", str(HERE/"video_noaudio.mp4")], stdin=subprocess.PIPE)
            t0=time.time()
            for i in range(n):
                d = await pg.evaluate(f"frame({i/fps})")
                ff.stdin.write(base64.b64decode(d.split(",")[1]))
                if i%50==0: print(i, round(time.time()-t0,1), flush=True)
            ff.stdin.close(); ff.wait()
        await b.close()
mode=sys.argv[1]; asyncio.run(main(mode, [float(x) for x in sys.argv[2:]]))
