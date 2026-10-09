import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')
    page.get_by_role('button',name='선수 도감').click()
    expect(page.locator('.roster-grid article')).to_have_count(40)
    # All forty local photographs must load, not merely render fallback cards.
    page.wait_for_function("Array.from(document.querySelectorAll('.roster-grid img')).every(i=>i.complete&&i.naturalWidth>0)")
    page.get_by_role('button',name='골키퍼').click()
    expect(page.locator('.roster-grid article')).to_have_count(4)
    page.get_by_role('button',name='전체',exact=False).click()
    page.get_by_label('선수 이름 검색').fill('김주찬')
    expect(page.locator('.roster-grid article')).to_have_count(1)
    expect(page.locator('.roster-grid')).to_contain_text('김주찬')
    page.get_by_role('button',name='시작 화면').click()
    page.get_by_role('button',name='제한 없음',exact=True).click()
    page.get_by_role('button',name='선수 맞히기 시작').click()
    def state(): return page.evaluate("JSON.parse(localStorage.getItem('bluewings-player-game-v2'))")
    def pick(correct=True):
        g=state();r=g['rounds'][g['index']]
        chosen=r['playerId'] if correct else next(i for i in r['choices'] if i!=r['playerId'])
        index=r['choices'].index(chosen)
        page.locator('.choices button').nth(index).click()
    expect(page.locator('.photo-tag')).to_have_text('얼굴 1/64칸 공개')
    expect(page.locator('.face-cell.opened')).to_have_count(1)
    assert page.locator('.face-window img').evaluate('(i)=>i.complete&&i.naturalWidth>0')
    for i in range(66):
        page.get_by_role('button',name='추가 힌트').click()
        assert len(state()['rounds'][0]['hints'])==i+1
    expect(page.locator('.photo-tag')).to_have_text('얼굴 64/64칸 공개')
    expect(page.get_by_role('button',name='모든 힌트를 공개했어요')).to_be_disabled()
    expect(page.locator('.revealed-hints span')).to_have_count(3)
    assert state()['rounds'][0]['photoStage']==63
    page.reload()
    expect(page.locator('.photo-tag')).to_have_text('얼굴 64/64칸 공개')
    expect(page.locator('.revealed-hints span')).to_have_count(3)
    pick()
    expect(page.locator('.football-answer')).to_contain_text('+10점')
    for button in page.locator('.choices button').all(): expect(button).to_be_disabled()
    page.get_by_role('button',name='다음 선수',exact=True).click()
    pick(False)
    expect(page.locator('.football-answer')).to_contain_text('오답')
    assert state()['rounds'][1]['earned']==0
    page.get_by_role('button',name='다음 선수',exact=True).click()
    pick()
    expect(page.locator('.football-answer')).to_contain_text('+100점')
    page.once('dialog',lambda d:d.accept())
    page.get_by_role('button',name='게임 종료').click()
    expect(page.locator('.football-results h1')).to_have_text('110점')
    expect(page.locator('.football-results')).to_contain_text('미응답 7문제')
    page.get_by_role('button',name='시작 화면으로').click()
    page.get_by_role('button',name='전체 40명',exact=True).click()
    page.get_by_role('button',name='선수 맞히기 시작').click()
    assert len(set(r['playerId'] for r in state()['rounds']))==40
    for i in range(40):
        r=state()['rounds'][i]
        assert len(set(r['choices']))==4 and r['playerId'] in r['choices']
        assert page.locator('.face-window img').evaluate('(img)=>img.complete&&img.naturalWidth>0')
        if i==0:
            page.screenshot(path='test-results/football-eyes-verified.png',full_page=True)
        pick()
        page.get_by_role('button',name='결과 보기' if i==39 else '다음 선수',exact=True).click()
    expect(page.locator('.football-results h1')).to_have_text('4000점')
    expect(page.locator('.football-stats')).to_contain_text('100%')
    page.screenshot(path='test-results/football-results.png',full_page=True)
    # Real pause/resume and expiration recovery.
    page.get_by_role('button',name='시작 화면으로').click()
    page.get_by_role('button',name='30초',exact=True).click()
    page.get_by_role('button',name='선수 맞히기 시작').click()
    page.get_by_label('타이머 일시정지').click()
    frozen=page.get_by_role('timer').inner_text()
    page.wait_for_timeout(1100)
    expect(page.get_by_role('timer')).to_have_text(frozen)
    page.reload()
    expect(page.get_by_role('timer')).to_have_text(frozen)
    page.get_by_label('타이머 재개').click()
    page.evaluate("()=>{const g=JSON.parse(localStorage.getItem('bluewings-player-game-v2'));g.deadline=Date.now()-1000;localStorage.setItem('bluewings-player-game-v2',JSON.stringify(g))}")
    page.reload()
    expect(page.locator('.football-answer')).to_contain_text('시간 종료')
    assert state()['rounds'][0]['earned']==0
    # Broken image still allows information hints and choices.
    page.get_by_role('button',name='다음 선수',exact=True).click()
    page.route('**/images/players/*.png',lambda route:route.abort())
    page.reload()
    expect(page.locator('.photo-fallback')).to_be_visible()
    expect(page.locator('.choices button').first).to_be_enabled()
    page.set_viewport_size({'width':320,'height':740})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.set_viewport_size({'width':1440,'height':1000})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert not errors,errors
    browser.close()
    print('PASS: all 40 photos, roster/search/filter, 66 nonduplicate hints, 10/100/0 scoring, refresh, 40 rounds/4000 points, timer, fallback, mobile/desktop, no JS errors')
