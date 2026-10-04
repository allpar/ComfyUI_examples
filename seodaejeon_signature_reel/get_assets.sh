#!/usr/bin/env bash
# Fetch fonts, music and the EDSR model used to build the reel (all free licences).
set -e
mkdir -p fonts && cd fonts
npm pack pretendard@1.3.9 -q && tar xzf pretendard-1.3.9.tgz
cp package/dist/public/static/Pretendard-{Black,ExtraBold,Bold,SemiBold,Medium,Light,Thin}.otf . && rm -rf package pretendard-1.3.9.tgz
G=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -sSLo "NotoSerifKR[wght].ttf" "$G/notoserifkr/NotoSerifKR%5Bwght%5D.ttf"
curl -sSLo "PlayfairDisplay-Italic[wght].ttf" "$G/playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf"
curl -sSLo "Montserrat[wght].ttf" "$G/montserrat/Montserrat%5Bwght%5D.ttf"
cd ..
curl -sSLo EDSR_x2.pb https://raw.githubusercontent.com/Saafke/EDSR_Tensorflow/master/models/EDSR_x2.pb
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/0lhi/FreePD.git freepd
git -C freepd checkout HEAD -- "Epic/Release the Hybrids.mp3"
