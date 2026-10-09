import { useEffect, useState } from 'react';
import { Download, Share2 } from 'lucide-react';
import type { Game } from './player-game';
import { createShareCard } from './share-card';
export default function ResultCard({game}:{game:Game}){
 const [image,setImage]=useState<{url:string;blob:Blob}|null>(null);const [message,setMessage]=useState('');const [error,setError]=useState('');
 useEffect(()=>{let active=true,url='';setImage(null);createShareCard(game).then(blob=>{if(active){url=URL.createObjectURL(blob);setImage({url,blob});}}).catch(e=>{if(active)setError(e instanceof Error?e.message:'공유 이미지 생성 실패');});return()=>{active=false;if(url)URL.revokeObjectURL(url);};},[game]);
 function download(){if(!image)return;const a=document.createElement('a');a.href=image.url;a.download=`블루윙즈-팬심성적표-${game.date}.png`;a.click();}
 async function share(){if(!image)return;const file=new File([image.blob],`블루윙즈-팬심성적표-${game.date}.png`,{type:'image/png'});if(navigator.canShare?.({files:[file]})&&navigator.share){try{await navigator.share({files:[file],title:'나의 블루윙즈 팬심 성적표'});}catch(e){if(!(e instanceof Error&&e.name==='AbortError'))setMessage('공유하지 못했습니다. 이미지 저장 버튼을 이용해 주세요.');}}else{download();setMessage('이미지를 저장했습니다. 원하는 앱에 첨부해 공유해 주세요.');}}
 return <section className="result-card-section"><h2>오늘의 팬심, 한 장에 담았어요!</h2><p>전체 선수 모자이크 · 점수 · 시간 · 정답과 오답 기록</p>{image?<img className="share-preview" src={image.url} alt={`${game.name}의 선수 맞히기 결과 공유 카드. 총점, 소요시간, 선수별 색상 점수와 맞힌 선수 및 오답 시도 선수 명단.`}/>:<div className="share-loading" role="status">{error||'선수 얼굴을 모아 성적표를 만드는 중…'}</div>}<div className="share-actions"><button className="football-primary" disabled={!image} onClick={download}><Download size={19}/> 이미지 저장</button><button className="football-primary" disabled={!image} onClick={share}><Share2 size={19}/> 공유하기</button></div>{message&&<p role="status">{message}</p>}<p>저장하면 화면에 보이는 카드만 한 장의 PNG로 내려받습니다.</p></section>;
}
