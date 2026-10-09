"""개발용: 내려받은 공식 사진에서 얼굴 좌표를 분석하고 로컬 선수 자료를 생성합니다."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path('.tools').resolve()))
import cv2
import numpy as np
from PIL import Image, ImageDraw

source = json.loads(Path('players-source.json').read_text(encoding='utf-8-sig'))
rows = sum(source['data'].values(), [])
detector = cv2.CascadeClassifier('.tools/cv2/data/haarcascade_frontalface_default.xml')
eye_detector = cv2.CascadeClassifier('.tools/cv2/data/haarcascade_eye.xml')
players = []
sheet = Image.new('RGB', (1000, 5 * 155), '#eaf2ff')
draw = ImageDraw.Draw(sheet)
for i, row in enumerate(rows):
    path = Path('public/images/players') / (row['kl_player_id'] + '.png')
    photo = Image.open(path).convert('RGBA')
    white = Image.new('RGBA', photo.size, 'white'); white.alpha_composite(photo)
    rgb = np.array(white.convert('RGB'))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    faces = detector.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4, minSize=(50,50))
    candidates = [f for f in faces if f[1] < photo.height * .35]
    if not candidates:
        raise RuntimeError('얼굴 검출 실패: ' + row['name'])
    x,y,w,h = map(int, max(candidates, key=lambda f:f[2]*f[3]))
    size = int(max(w,h)*1.35)
    crop_x=max(0,int(x+w/2-size/2)); crop_y=max(0,int(y+h/2-size/2))
    eyes = eye_detector.detectMultiScale(gray[y:y+int(h*.62),x:x+w],scaleFactor=1.05,minNeighbors=5)
    eye_y = y + (float(np.median([e[1]+e[3]/2 for e in eyes])) if len(eyes) else h*.36)
    eye_center = (eye_y-crop_y)/size
    face={'x':crop_x,'y':crop_y,'size':size,'imageWidth':photo.width,'imageHeight':photo.height,
          'eyeTop':max(.1,eye_center-.075),'eyeBottom':min(.65,eye_center+.075),
          'noseBottom':(y+h*.72-crop_y)/size,'mouthBottom':(y+h*.96-crop_y)/size}
    players.append({'id':row['kl_player_id'],'name':row['name'],'position':row['position'],
       'number':row['uniform_number'],'height':row['height'],'weight':row['weight'],
       'birthday':row['birthday'],'image':'/images/players/'+row['kl_player_id']+'.png',
       'sourceImage':row['list_img'],'face':face})
    thumb=white.crop((crop_x,crop_y,crop_x+size,crop_y+size)).resize((125,125)).convert('RGB')
    sheet.paste(thumb,((i%8)*125,(i//8)*155))
    top=(i//8)*155+int(face['eyeTop']*125);bottom=(i//8)*155+int(face['eyeBottom']*125)
    draw.rectangle(((i%8)*125,top,(i%8+1)*125-1,bottom),outline='red',width=2)
    draw.text(((i%8)*125,(i//8)*155+130),row['kl_player_id'],fill='black')
Path('src/players.json').write_text(json.dumps(players,ensure_ascii=False,indent=2),encoding='utf-8')
sheet.save('test-results/face-coordinates.png')
lines=['# 수원삼성 선수 사진 목록','', '공식 선수단 페이지: https://www.bluewings.kr/player/pro','', '수집 기준: 2026-10-09 · 공식 페이지에 등록된 전체 40명.','', '| 등번호 | 선수 | 포지션 | 생년월일 | 키 | 로컬 사진 |','|---|---|---|---|---|---|']
for row in players:
    lines.append(f"| {row['number']} | {row['name']} | {row['position']} | {row['birthday']} | {row['height']}cm | [사진](../public{row['image']}) |")
Path('docs').mkdir(exist_ok=True)
Path('docs/선수사진목록.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'{len(players)}명 얼굴 좌표와 선수 목록 생성 완료')
