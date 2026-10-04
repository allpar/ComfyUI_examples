"""Build image layers for the reel: graded base plate, tower cut-out (RGBA), and a clean plate
with the towers inpainted away (so the towers can move independently for parallax)."""
import cv2, numpy as np, sys, os

src = sys.argv[1] if len(sys.argv) > 1 else "src.png"
SUF = sys.argv[2] if len(sys.argv) > 2 else ""
img = cv2.imread(src)
k = img.shape[1] / 1672.0            # scale from original coords

# tower outlines in original 1672x941 coords
TOWERS = [
    [(602, 158), (668, 150), (670, 175), (716, 180), (718, 552), (606, 556)],
    [(776, 154), (796, 142), (875, 142), (877, 150), (902, 152), (903, 560), (782, 565)],
    [(960, 200), (1006, 198), (1006, 172), (1080, 170), (1082, 198), (1110, 200), (1112, 575), (965, 578)],
]
h, w = img.shape[:2]
mask = np.zeros((h, w), np.uint8)
for poly in TOWERS:
    pts = (np.array(poly, np.float32) * k).astype(np.int32)
    cv2.fillPoly(mask, [pts], 255, lineType=cv2.LINE_AA)

# fade the bottom of the cut-out into the podium so the seam is invisible
yy = np.arange(h, dtype=np.float32)[:, None] / k
fade = np.clip((585 - yy) / 40.0, 0, 1)
alpha = (cv2.GaussianBlur(mask, (0, 0), 0.8 * k).astype(np.float32) / 255.0) * fade
rgba = np.dstack([img, (alpha * 255).astype(np.uint8)])
cv2.imwrite(f"towers{SUF}.png", rgba)

# clean plate: inpaint a dilated version of the towers
dil = cv2.dilate(mask, np.ones((int(9 * k), int(9 * k)), np.uint8))
small = cv2.resize(img, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
msmall = cv2.resize(dil, (w // 2, h // 2), interpolation=cv2.INTER_NEAREST)
clean = cv2.inpaint(small, msmall, 12, cv2.INPAINT_TELEA)
clean = cv2.resize(clean, (w, h), interpolation=cv2.INTER_CUBIC)
tight = cv2.dilate(mask, np.ones((int(3 * k) | 1, int(3 * k) | 1), np.uint8))
m3 = (cv2.GaussianBlur(tight, (0, 0), 0.8 * k).astype(np.float32) / 255.0)[..., None]
clean = (img * (1 - m3) + clean * m3).astype(np.uint8)
cv2.imwrite(f"clean{SUF}.jpg", clean, [cv2.IMWRITE_JPEG_QUALITY, 95])

# mild sharpen for the base plate
blur = cv2.GaussianBlur(img, (0, 0), 1.2 * k)
sharp = cv2.addWeighted(img, 1.35, blur, -0.35, 0)
cv2.imwrite(f"base{SUF}.jpg", sharp, [cv2.IMWRITE_JPEG_QUALITY, 95])
print("layers", w, h, "k", k)
