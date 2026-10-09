from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright,expect
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://localhost:5173');page.wait_for_load_state('networkidle')
    page.get_by_label('참가자 / 팀 이름').fill('푸른 응원단')
    page.get_by_role('button',name='선수 맞히기 시작').click()
    def state():return page.evaluate("JSON.parse(localStorage.getItem('bluewings-player-game-v4'))")
    initial=state();r=initial['rounds'][0];wrong=next(i for i in r['choices'] if i!=r['playerId']);slot=r['choices'].index(wrong)
    old_name=page.locator('.choices button').nth(slot).inner_text()
    page.locator('.choices button').nth(slot).click()
    expect(page.locator('.wrong-feedback')).to_contain_text('오답')
    changed=state();assert changed['deadline']==initial['deadline'] and not changed['rounds'][0]['complete']
    assert wrong not in changed['rounds'][0]['choices'] and changed['rounds'][0]['wrongIds']==[wrong]
    assert page.locator('.choices button').nth(slot).inner_text()!=old_name
    expect(page.locator('.score-bar')).to_contain_text('85점')
    expect(page.get_by_role('button',name='다음 선수')).to_be_disabled()
    page.reload();expect(page.locator('.wrong-feedback')).to_be_visible()
    assert state()['rounds'][0]['choices']==changed['rounds'][0]['choices']
    page.evaluate('Math.random=()=>0');page.get_by_role('button',name='추가 힌트').click()
    expect(page.locator('.score-bar')).to_contain_text('70점')
    r=state()['rounds'][0];page.locator('.choices button').nth(r['choices'].index(r['playerId'])).click()
    expect(page.locator('.football-answer')).to_contain_text('+70점')
    page.get_by_role('button',name='다음 선수').click()
    page.evaluate("()=>{const g=JSON.parse(localStorage.getItem('bluewings-player-game-v4'));g.deadline=Date.now()-1;localStorage.setItem('bluewings-player-game-v4',JSON.stringify(g));}")
    page.reload();expect(page.locator('.football-answer')).to_contain_text('시간 종료')
    page.get_by_role('button',name='다음 선수').click()
    for i in range(2,10):
        r=state()['rounds'][i];page.locator('.choices button').nth(r['choices'].index(r['playerId'])).click()
        page.get_by_role('button',name='결과 보기' if i==9 else '다음 선수',exact=True).click()
    expect(page.locator('.result-summary h1')).to_have_text('870점')
    expect(page.get_by_role('button',name='이미지 저장')).to_be_enabled(timeout=60000)
    expect(page.locator('.share-preview')).to_be_visible()
    with page.expect_download() as dl:page.get_by_role('button',name='이미지 저장').click()
    dl.value.save_as('test-results/fan-report.png')
    image=Image.open('test-results/fan-report.png')
    assert image.width==1080 and image.height>1400
    assert len(image.getcolors(maxcolors=1000000))>10000
    page.evaluate('navigator.canShare=()=>false')
    with page.expect_download() as dl:page.get_by_role('button',name='공유하기').click()
    expect(page.locator('.result-card-section')).to_contain_text('첨부해 공유')
    # Simulate native sharing without sending to any external application.
    page.evaluate("()=>{navigator.canShare=()=>true;navigator.share=async(data)=>{window.sharedFileCount=data.files.length;window.sharedFileType=data.files[0].type};}")
    page.get_by_role('button',name='공유하기').click()
    assert page.evaluate('window.sharedFileCount')==1 and page.evaluate('window.sharedFileType')=='image/png'
    page.reload();expect(page.get_by_role('button',name='이미지 저장')).to_be_enabled(timeout=60000)
    assert state()['rounds'][0]['wrongIds']==[wrong]
    page.set_viewport_size({'width':320,'height':740});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert not errors,errors
    browser.close();print('PASS: retry -15, replaced option, rejected name never reused, timer unchanged, refresh, score 870, one-page PNG, save/share fallback/native payload, 320px, no JS errors')
