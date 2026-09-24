"""检查连续阅读、锚点定位与响应式布局。"""

from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json

from playwright.sync_api import sync_playwright


@contextmanager
def local_page_server(directory):
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:%s" % server.server_port
    finally:
        server.shutdown()
        server.server_close()


def inspect_learning_page():
    root = Path(__file__).resolve().parents[1]
    shots = root / "_shots"
    shots.mkdir(exist_ok=True)
    with local_page_server(root) as base, sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(base + "/index.html")
        page.wait_for_load_state("load")
        page.wait_for_timeout(500)
        assert page.locator(".home-choice").count() == 2
        order = page.locator("[data-reading-module]").evaluate_all("nodes => nodes.map(n => n.id)")
        assert order == ["m1", "m2", "m3", "m4", "m9", "m5", "m6", "m7", "m8", "m10", "m11", "m13", "m12"], order
        assert page.locator(".chapter-practice").count() == 11
        assert page.locator("#learningReference").get_attribute("open") is None
        baseline = page.locator(".demo").count()
        assert baseline >= 72
        assert page.locator("#stModReady").text_content() == "10"
        assert page.locator("#stModWip").text_content() == "2"
        page.locator('[data-tool-check="evidence"]').click()
        assert "完整命令" in page.locator("#toolChecklistOut").text_content()
        page.locator('[data-tool-diff="secret"]').click()
        assert "停止提交" in page.locator("#toolDiffOut").text_content()
        # M7 表设计三步建模：三步全选对后展示 schema
        page.locator('[data-sd-step="0"]').click()
        page.locator('#sdChoices .sd-opt').first.click()
        assert "✔" in page.locator("#sdOut").text_content()
        page.locator('[data-sd-step="1"]').click()
        page.locator('#sdChoices .sd-opt').first.click()
        page.locator('[data-sd-step="2"]').click()
        page.locator('#sdChoices .sd-opt').first.click()
        assert "三步全对" in page.locator("#sdOut").text_content()
        assert page.locator("#sdSchema").is_visible()
        # M12 提示词模式库：切到「修 Bug」出现证据链模板
        page.locator('[data-pm="bug"]').click()
        assert "复现" in page.locator("#pmPrompt").text_content()
        # M12 AI 翻车现场：点「看修法」出修法说明
        page.locator('[data-ac-fix="timer"]').click()
        assert "clearInterval" in page.locator('[data-ac-out="timer"]').text_content()
        page.screenshot(path=str(shots / "reading-home-desktop.png"))
        page.locator('.home-choice[href="#m1"]').click()
        page.wait_for_timeout(150)
        assert page.locator('#m1').bounding_box()["y"] >= 50
        page.locator('#m3PropsInput').fill('保留中的练习')
        page.locator('#sideMods [data-mod="m7"]').click()
        page.wait_for_timeout(150)
        assert page.locator('#sideMods [data-mod="m7"]').get_attribute('aria-current') == 'location'
        page.locator('#sideMods [data-mod="m3"]').click()
        page.wait_for_timeout(150)
        assert page.locator('#m3PropsInput').input_value() == '保留中的练习'
        assert page.locator('.demo').count() == baseline
        assert page.locator('.demo').evaluate_all("nodes => nodes.every(n => getComputedStyle(n).display !== 'none')")
        page.go_back()
        page.wait_for_timeout(200)
        assert page.url.endswith('#m7')
        page.reload()
        page.wait_for_timeout(300)
        assert abs(page.locator('#m7').bounding_box()['y'] - 66) < 5
        page.goto(base + '/index.html#practice-m6')
        page.wait_for_timeout(200)
        assert page.locator('#practice-m6').get_attribute('open') is not None
        page.goto(base + '/index.html#starter')
        page.wait_for_timeout(200)
        assert page.locator('#learningReference').get_attribute('open') is not None
        page.goto(base + '/project.html')
        page.wait_for_url('**/index.html#projectTrack')
        page.wait_for_timeout(200)
        assert abs(page.locator('#projectTrack').bounding_box()['y'] - 66) < 5
        reports = []
        for width in [1440, 768, 375]:
            page.set_viewport_size({"width": width, "height": 900})
            page.goto(base + '/index.html')
            page.wait_for_timeout(300)
            measure = page.evaluate("() => ({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})")
            assert measure["scrollWidth"] <= width, measure
            assert page.locator(".home-choice").nth(1).bounding_box()["y"] < 600
            reports.append({"width": width, "scrollWidth": measure["scrollWidth"]})
            page.screenshot(path=str(shots / ('reading-home-%s.png' % width)))
            page.goto(base + '/index.html#m7')
            page.wait_for_timeout(200)
            page.screenshot(path=str(shots / ('reading-data-%s.png' % width)))
            if width < 1100:
                page.locator('#navBurger').click()
                page.locator('#sideMods [data-mod="m12"]').click()
                page.wait_for_timeout(200)
                assert page.locator('#navBurger').get_attribute('aria-expanded') == 'false'
            page.locator('#themeBtn').click()
            page.screenshot(path=str(shots / ('reading-dark-%s.png' % width)))
            page.locator('#themeBtn').click()
        print(json.dumps({"chapters": order, "demos": baseline, "errors": errors, "viewports": reports}, ensure_ascii=False))
        assert not errors, errors
        browser.close()


if __name__ == '__main__':
    inspect_learning_page()
