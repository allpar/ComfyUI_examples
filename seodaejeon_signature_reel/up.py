import cv2, time
sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel("EDSR_x2.pb"); sr.setModel("edsr", 2)
img = cv2.imread("src.png"); t=time.time()
out = sr.upsample(img); cv2.imwrite("src_x2.png", out); print("done", out.shape, time.time()-t)
