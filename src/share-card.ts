import { assetPath } from './assets';
import { comboStats, isNoHintCorrect, players, elapsedMs, formatElapsed, type Game } from './player-game';
export function scoreColor(score:number,played:boolean){return !played?'#718096':score>=85?'#d6a322':score>=55?'#199469':score>0?'#2b70cb':'#d64256';}
const imageCache=new Map<string,Promise<HTMLImageElement|null>>();
function loadImage(url:string){let cached=imageCache.get(url);if(!cached){cached=new Promise<HTMLImageElement|null>(resolve=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>resolve(null);img.src=assetPath(url);});imageCache.set(url,cached);}return cached;}
export async function createShareCard(game:Game):Promise<Blob>{
 await document.fonts.ready;
 const rounds=new Map(game.rounds.map(r=>[r.playerId,r]));
 const total=game.rounds.reduce((sum,r)=>sum+r.earned,0);
 const correct=game.rounds.filter(r=>r.complete&&r.selected===r.playerId);
 const missed=game.rounds.filter(r=>r.wrongIds.length>0||r.timedOut);
 const nameOf=(id:string)=>players.find(p=>p.id===id)?.name??'';
 const canvas=document.createElement('canvas');canvas.width=1080;
 const ctx=canvas.getContext('2d');if(!ctx)throw Error('이미지 생성을 지원하지 않는 브라우저입니다.');
 function font(size:number,weight=700){ctx!.font=`${weight} ${size}px "맑은 고딕", "Apple SD Gothic Neo", sans-serif`;}
 function wrap(text:string,width:number,size:number){font(size);const lines:string[]=[];let line='';for(const char of text){if(ctx!.measureText(line+char).width>width&&line){lines.push(line);line=char;}else line+=char;}if(line)lines.push(line);return lines.length?lines:['아직 없어요'];}
 const namesCorrect=correct.map(r=>nameOf(r.playerId)+(r.wrongIds.length?'(재도전)':'')).join(' · ');
 const namesMissed=missed.map(r=>nameOf(r.playerId)+(r.timedOut?'(시간 종료)':r.selected===r.playerId?'(재도전 정답)':'(미완료)')).join(' · ');
 const linesCorrect=wrap(namesCorrect,442,23),linesMissed=wrap(namesMissed,442,23);
 const listHeight=Math.max(linesCorrect.length,linesMissed.length)*35+105;
 const noHints=game.rounds.filter(isNoHintCorrect);const badgeLines=wrap(noHints.map(r=>nameOf(r.playerId)+(r.wrongIds.length?'(재도전)':'')).join(' · '),936,23);const badgeHeight=badgeLines.length*35+110;
 canvas.height=1350+listHeight+badgeHeight+20;
 function box(x:number,y:number,w:number,h:number,color:string,r=20){ctx!.fillStyle=color;ctx!.beginPath();ctx!.roundRect(x,y,w,h,r);ctx!.fill();}
 function text(content:string,x:number,y:number,size:number,color='#173c64',weight=700){font(size,weight);ctx!.fillStyle=color;ctx!.fillText(content,x,y);}
 ctx.fillStyle='#f4f8ff';ctx.fillRect(0,0,1080,canvas.height);
 ctx.fillStyle='#075bb8';ctx.fillRect(0,0,360,18);ctx.fillStyle='#fff';ctx.fillRect(360,0,360,18);ctx.fillStyle='#e22b3d';ctx.fillRect(720,0,360,18);
 const [logo,...photos]=await Promise.all([loadImage('/images/suwon-bluewings-logo.png'),...players.map(p=>loadImage(p.image))]);
 if(logo)ctx.drawImage(logo,930,49,74,102);
 text('BLUEWINGS FAN REPORT',48,72,22,'#075bb8',900);
 const name=game.name.slice(0,40);font(38,900);let nameSize=38;while(ctx.measureText(`${name}의 팬심 성적표`).width>850&&nameSize>20){nameSize--;font(nameSize,900);}text(`${name}의 팬심 성적표`,48,129,nameSize,'#13375f',900);
 text(`최대 ${comboStats(game.rounds).best}콤보 · 노힌트 선수 배지 ${noHints.length}개`,48,175,25,'#075bb8');
 box(48,205,610,165,'#075bb8');box(680,205,352,165,'#e5efff');
 text('종합 점수',73,244,22,'#cce4ff');text(String(total),73,325,75,'#fff',900);text(`/ ${game.rounds.length*100}점`,340,322,26,'#d9eaff');
 text(game.completedAt===null?'종료까지 걸린 시간':'전체 완료 시간',705,244,22,'#526e90');text(formatElapsed(elapsedMs(game)),705,306,38,'#075bb8',900);text(`정답 ${correct.length}/${game.rounds.length}명`,705,345,22,'#526e90');
 text('우리 팀 40명, 나의 팬심 모자이크',48,423,29,'#14385f',900);
 text('금빛 85~100 · 초록 55~84 · 파랑 10~54 · 빨강 시간 종료 · 회색 미출제/미응답',48,458,18,'#6d839a');
 const tile=112,gap=10,startX=57,startY=480;
 players.forEach((p,i)=>{const x=startX+(i%8)*(tile+gap),y=startY+Math.floor(i/8)*145;const r=rounds.get(p.id);const played=!!r?.complete;const color=scoreColor(r?.earned??0,played);box(x,y,tile,135,'#fff',10);const photo=photos[i];if(photo){ctx.save();ctx.beginPath();ctx.roundRect(x+4,y+4,tile-8,93,6);ctx.clip();ctx.drawImage(photo,p.face.x,p.face.y,p.face.size,p.face.size,x+4,y+4,tile-8,93);if(!played){ctx.fillStyle='#ffffffa6';ctx.fillRect(x+4,y+4,tile-8,93);}ctx.restore();}else{text('?',x+45,y+63,35,'#9cb1ca');}ctx.strokeStyle=color;ctx.lineWidth=4;ctx.beginPath();ctx.roundRect(x,y,tile,135,10);ctx.stroke();let size=18;font(size);while(ctx.measureText(p.name).width>102&&size>12){font(--size);}text(p.name,x+7,y+116,size,'#183c60',900);box(x+49,y+68,59,26,color,5);text(played?`${r!.earned}점`:r?'미응답':'미출제',x+54,y+87,14,'#fff',900);if(r&&isNoHintCorrect(r)){box(x+57,y+4,51,21,'#075bb8',4);text('노힌트',x+61,y+20,12,'#fff');}if(r?.wrongIds.length){box(x+4,y+4,48,21,'#d64256',4);text(`오답 ${r.wrongIds.length}`,x+8,y+20,12,'#fff');}});
 const listsY=1225;
 box(48,listsY,478,listHeight,'#e4f4ec');box(550,listsY,482,listHeight,'#fff0ee');
 text(`맞힌 선수 ${correct.length}명`,68,listsY+41,27,'#17664a',900);
 text(`오답 시도 / 놓친 선수 ${missed.length}명`,570,listsY+41,25,'#a83d4c',900);
 linesCorrect.forEach((line,i)=>text(line,68,listsY+81+i*35,23,'#2d6553',600));
 linesMissed.forEach((line,i)=>text(line,570,listsY+81+i*35,23,'#96525b',600));
 const badgeY=listsY+listHeight+20;box(48,badgeY,984,badgeHeight,'#fff4ce');text(`노힌트 선수 배지 ${noHints.length}명 · 최대 ${comboStats(game.rounds).best}콤보`,68,badgeY+41,27,'#78550b',900);badgeLines.forEach((line,i)=>text(line,68,badgeY+81+i*35,23,'#78550b',600));
 const footerY=badgeY+badgeHeight+36;text('재도전해서 맞힌 선수는 두 명단에 함께 표시됩니다.',48,footerY,19,'#74879c',500);
 text(`${game.date} · ${game.completedAt===null?'중도 종료':'30초 챌린지 완주'} · 누구게, 블루윙즈!`,48,footerY+38,22,'#075bb8',900);
 text('namsoojang.github.io/bluewings-player-quiz',48,footerY+70,19,'#74879c',500);
 return new Promise((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(Error('이미지를 만들지 못했습니다.')),'image/png'));
}
