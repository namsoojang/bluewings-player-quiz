from playwright.sync_api import sync_playwright,expect
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://localhost:5173');page.wait_for_load_state('networkidle')
    page.get_by_label('참가자 / 팀 이름').fill('빠른 팀')
    page.get_by_role('button',name='선수 맞히기 시작').click()
    expect(page.get_by_role('timer')).to_have_text('00:30')
    page.get_by_label('타이머 일시정지').click()
    frozen=page.get_by_role('timer').inner_text();before=page.locator('.elapsed-live b').inner_text()
    page.wait_for_timeout(1100)
    expect(page.get_by_role('timer')).to_have_text(frozen)
    assert before!=page.locator('.elapsed-live b').inner_text()
    page.reload();expect(page.get_by_role('timer')).to_have_text(frozen)
    assert page.locator('.elapsed-live b').inner_text()!=before
    for i in range(10):
        g=page.evaluate("JSON.parse(localStorage.getItem('bluewings-player-game-v3'))")
        r=g['rounds'][i]
        page.locator('.choices button').nth(r['choices'].index(r['playerId'])).click()
        if i==9:
            duration=page.locator('.elapsed-live b').inner_text()
            page.wait_for_timeout(1000)
            expect(page.locator('.elapsed-live b')).to_have_text(duration)
        page.get_by_role('button',name='결과 보기' if i==9 else '다음 선수',exact=True).click()
    expect(page.locator('.completion-time b')).to_have_text(duration)
    expect(page.locator('.leaderboard')).to_contain_text('빠른 팀')
    saved=page.evaluate("JSON.parse(localStorage.getItem('bluewings-records-v1'))")
    assert len(saved)==1 and saved[0]['score']==1000
    page.reload()
    assert len(page.evaluate("JSON.parse(localStorage.getItem('bluewings-records-v1'))"))==1
    expect(page.locator('.completion-time b')).to_have_text(duration)
    page.screenshot(path='test-results/completion-record.png',full_page=True)
    page.get_by_role('button',name='시작 화면으로').click()
    page.get_by_role('button',name='선수 맞히기 시작').click()
    page.once('dialog',lambda d:d.accept());page.get_by_role('button',name='게임 종료').click()
    assert len(page.evaluate("JSON.parse(localStorage.getItem('bluewings-records-v1'))"))==1
    assert not errors,errors
    browser.close();print('PASS: fixed 30 seconds; elapsed during pause/refresh; stop at last answer; record saved once; name retained; early exit excluded')
