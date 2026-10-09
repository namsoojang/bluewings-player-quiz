import { describe, expect, it } from 'vitest';
import { defaultQuestions } from './data';
import { remainingTime, score, shuffle, validateQuestions, type Game } from './game';
const game=():Game=>({questions:defaultQuestions,index:0,scores:{},revealed:{},remaining:60,deadline:null,duration:60,finished:false});
describe('게임 상태',()=>{
 it('30문제와 고유 ID 및 난이도를 제공한다',()=>{expect(validateQuestions(defaultQuestions)).toHaveLength(30);expect(new Set(defaultQuestions.map(q=>q.id)).size).toBe(30);});
 it('순서를 섞어도 원본과 문제의 중복 여부를 유지한다',()=>{const original=defaultQuestions.map(q=>q.id);const result=shuffle(defaultQuestions);expect(result).not.toBe(defaultQuestions);expect(new Set(result.map(q=>q.id)).size).toBe(30);expect(defaultQuestions.map(q=>q.id)).toEqual(original);});
 it('실제 경과 시간과 종료 시각을 사용한다',()=>{const g={...game(),deadline:10000};expect(remainingTime(g,6500)).toBe(4);expect(remainingTime(g,12000)).toBe(0);expect(remainingTime(game(),20000)).toBe(60);});
 it('복구된 종료 시각도 동일하게 계산한다',()=>{const restored=JSON.parse(JSON.stringify({...game(),deadline:5000}));expect(remainingTime(restored,6000)).toBe(0);});
 it('정답 처리 후 중복 점수 및 수정 처리를 막는다',()=>{const first=score(game(),true);expect(Object.values(first.scores)).toEqual([true]);expect(score(first,false)).toBe(first);expect(first.deadline).toBeNull();});
 it('잘못된 JSON, 중복 ID, 외부 이미지 주소를 거부한다',()=>{expect(()=>validateQuestions([])).toThrow();expect(()=>validateQuestions([defaultQuestions[0],defaultQuestions[0]])).toThrow();expect(()=>validateQuestions([{...defaultQuestions[0],image:'https://example.com/a.png'}])).toThrow();});
});
