#!/usr/bin/env python3
"""
Task 2: math_deck.csv generator
高校数学（基礎解析）100問の Cloze + MathJax カードを生成する。

- 指数・対数: 20問
- 三角関数: 40問
- 複素数・n乗根: 10問
- 微分・極限: 30問
"""

import csv
import re

from math_explanations import EXPLANATIONS

# (Text with Cloze + MathJax, Tag)
_RAW_CARDS = [
    # ── 1. 指数計算・指数関数・対数関数（20問） ──
    (r"[$]a^{-n} = {{c1::\frac{1}{a^n}}}[/$]（$a \neq 0$）", "指数"),
    (r"[$]a^0 = {{c1::1}}[/$]（$a \neq 0$）", "指数"),
    (r"[$]a^{\frac{1}{2}} = {{c1::\sqrt{a}}}[/$]（$a \geq 0$）", "指数"),
    (r"[$]a^m \cdot a^n = {{c1::a^{m+n}}}[/$]（$a>0$）", "指数"),
    (r"[$](a^m)^n = {{c1::a^{mn}}}[/$]（$a>0$）", "指数"),
    (r"[$](ab)^n = {{c1::a^n b^n}}[/$]（$a>0,\; b>0$）", "指数"),
    (r"[$]\frac{a^m}{a^n} = {{c1::a^{m-n}}}[/$]（$a>0$）", "指数"),
    (r"[$]\sqrt[n]{b^m} = {{c1::b^{\frac{m}{n} }}}[/$]（$b>0$。$n$ が偶数なら被開方数 $\geq 0$）", "指数"),
    (r"[$]\sqrt{(-6)^2} = {{c1::6}}[/$]（偶数乗根の注意）", "指数"),
    (r"[$]\sqrt[3]{-27} = {{c1::-3}}[/$]（奇数乗根は負の数も取れる）", "指数"),
    (r"[$]a^x = b \;\Leftrightarrow\; x = {{c1::\log_a b}}[/$]（$a>0,\; a \neq 1,\; b>0$）", "対数"),
    (r"[$]\log_a(bc) = {{c1::\log_a b + \log_a c}}[/$]（$a>0,\; a\neq 1,\; b>0,\; c>0$）", "対数"),
    (r"[$]\log_a\!\left(\frac{b}{c}\right) = {{c1::\log_a b - \log_a c}}[/$]（$a>0,\; a\neq 1,\; b>0,\; c>0$）", "対数"),
    (r"[$]\log_a(b^n) = {{c1::n \log_a b}}[/$]（$a>0,\; a\neq 1,\; b>0$）", "対数"),
    (r"[$]\log_a b = \frac{\log_c b}{{{c1::\log_c a}}}[/$]（底の変換。$a>0,\; a\neq 1,\; b>0,\; c>0,\; c\neq 1,\; a\neq c$）", "対数"),
    (r"[$]\log_a a = {{c1::1}}[/$]（$a>0,\; a\neq 1$）", "対数"),
    (r"[$]\log_a 1 = {{c1::0}}[/$]（$a>0,\; a\neq 1$）", "対数"),
    (r"[$]\log_{10} 100 = {{c1::2}}[/$]（常用対数）", "対数"),
    (r"[$]10^n[/$]（$n$ は0以上の整数）の桁数は {{c1::n+1}} 桁", "対数"),
    (r"[$]N \geq 1[/$] の正の実数 $N$ の桁数は [$][\log_{10} N] + {{c1::1}}[/$]（$[\;]$ はガウス記号）", "対数"),

    # ── 2. 三角関数（40問） ──
    (r"[$]\tan\theta = {{c1::\frac{\sin\theta}{\cos\theta}}}[/$]（$\cos\theta \neq 0$）", "三角関数"),
    (r"[$]y = \tan\theta[/$] の定義域：[$]\theta \neq {{c1::\frac{\pi}{2} + n\pi}}[/$]（$n$ は整数）", "三角関数"),
    (r"[$]\sin(-\theta) = {{c1::-\sin\theta}}[/$]（奇関数）", "三角関数"),
    (r"[$]\cos(-\theta) = {{c1::\cos\theta}}[/$]（偶関数）", "三角関数"),
    (r"[$]\tan(-\theta) = {{c1::-\tan\theta}}[/$]（奇関数）", "三角関数"),
    (r"[$]y = \sin(k\theta)[/$] の周期は [$]{{c1::\frac{2\pi}{k}}}[/$]（$k>0$）", "三角関数"),
    (r"[$]y = \cos(k\theta)[/$] の周期は [$]{{c1::\frac{2\pi}{k}}}[/$]（$k>0$）", "三角関数"),
    (r"[$]y = \tan(k\theta)[/$] の周期は [$]{{c1::\frac{\pi}{k}}}[/$]（$k>0$）", "三角関数"),
    (r"[$]y = A\sin\theta[/$] の振幅は [$]{{c1::|A|}}[/$]", "三角関数"),
    (r"[$]y = \sin(\theta - a)[/$] のグラフは [$]y = \sin\theta[/$] を $\theta$ 軸方向に {{c1::$+a$}} だけ平行移動したもの", "三角関数"),
    (r"[$]\sin(\alpha + \beta) = {{c1::\sin\alpha\cos\beta + \cos\alpha\sin\beta}}[/$]", "加法定理"),
    (r"[$]\sin(\alpha - \beta) = {{c1::\sin\alpha\cos\beta - \cos\alpha\sin\beta}}[/$]", "加法定理"),
    (r"[$]\cos(\alpha + \beta) = {{c1::\cos\alpha\cos\beta - \sin\alpha\sin\beta}}[/$]", "加法定理"),
    (r"[$]\cos(\alpha - \beta) = {{c1::\cos\alpha\cos\beta + \sin\alpha\sin\beta}}[/$]", "加法定理"),
    (r"[$]\tan(\alpha + \beta) = \frac{\tan\alpha + \tan\beta}{{{c1::1 - \tan\alpha\tan\beta}}}[/$]（$\alpha+\beta \neq \frac{\pi}{2}+n\pi$）", "加法定理"),
    (r"[$]\sin 2\theta = {{c1::2\sin\theta\cos\theta}}[/$]（倍角の公式）", "倍角"),
    (r"[$]\cos 2\theta = {{c1::\cos^2\theta - \sin^2\theta}}[/$]（倍角の公式・第1形）", "倍角"),
    (r"[$]\cos 2\theta = {{c1::2\cos^2\theta - 1}}[/$]（倍角の公式・第2形）", "倍角"),
    (r"[$]\cos 2\theta = {{c1::1 - 2\sin^2\theta}}[/$]（倍角の公式・第3形）", "倍角"),
    (r"[$]\tan 2\theta = \frac{2\tan\theta}{{{c1::1 - \tan^2\theta}}}[/$]（倍角の公式。$2\theta \neq \frac{\pi}{2}+n\pi$）", "倍角"),
    (r"[$]\sin^2\frac{\theta}{2} = {{c1::\frac{1 - \cos\theta}{2}}}[/$]（半角の公式）", "半角"),
    (r"[$]\cos^2\frac{\theta}{2} = {{c1::\frac{1 + \cos\theta}{2}}}[/$]（半角の公式）", "半角"),
    (r"[$]a\sin\theta + b\cos\theta = R\sin(\theta + \alpha)[/$] において [$]R = {{c1::\sqrt{a^2 + b^2}}}[/$]", "合成"),
    (r"[$]a\sin\theta + b\cos\theta = R\sin(\theta + \alpha)[/$] において [$]\tan\alpha = {{c1::\frac{b}{a}}}[/$]（$a>0,\; a\neq 0$）", "合成"),
    (r"[$]\sin\alpha\cos\beta = \frac{1}{2}\bigl[\sin(\alpha+\beta) + {{c1::\sin(\alpha-\beta)}}\bigr][/$]（積和の公式）", "積和"),
    (r"[$]\cos\alpha\cos\beta = \frac{1}{2}\bigl[\cos(\alpha+\beta) + {{c1::\cos(\alpha-\beta)}}\bigr][/$]（積和の公式）", "積和"),
    (r"[$]\sin\alpha\sin\beta = -\frac{1}{2}\bigl[\cos(\alpha+\beta) - {{c1::\cos(\alpha-\beta)}}\bigr][/$]（積和の公式）", "積和"),
    (r"[$]\sin A + \sin B = 2\sin\frac{A+B}{2}{{c1::\cos\frac{A-B}{2}}}[/$]（和積の公式）", "和積"),
    (r"[$]\sin A - \sin B = 2\cos\frac{A+B}{2}{{c1::\sin\frac{A-B}{2}}}[/$]（和積の公式）", "和積"),
    (r"[$]\cos A + \cos B = 2\cos\frac{A+B}{2}{{c1::\cos\frac{A-B}{2}}}[/$]（和積の公式）", "和積"),
    (r"[$]\cos A - \cos B = -2\sin\frac{A+B}{2}{{c1::\sin\frac{A-B}{2}}}[/$]（和積の公式）", "和積"),
    (r"[$]\sin^2\theta + \cos^2\theta = {{c1::1}}[/$]（基本恒等式）", "三角関数"),
    (r"[$]1 + \tan^2\theta = {{c1::\frac{1}{\cos^2\theta}}}[/$]（基本恒等式。$\cos\theta \neq 0$）", "三角関数"),
    (r"[$]\sin\!\left(\frac{\pi}{2} - \theta\right) = {{c1::\cos\theta}}[/$]（余角の関係）", "三角関数"),
    (r"[$]\cos(\pi - \theta) = {{c1::-\cos\theta}}[/$]（対称性）", "三角関数"),
    (r"[$]\sin\frac{\pi}{6} = {{c1::\frac{1}{2}}}[/$]", "三角関数"),
    (r"[$]\cos\frac{\pi}{3} = {{c1::\frac{1}{2}}}[/$]", "三角関数"),
    (r"[$]\tan\frac{\pi}{4} = {{c1::1}}[/$]", "三角関数"),
    (r"[$]\sin\frac{\pi}{3} = {{c1::\frac{\sqrt{3}}{2}}}[/$]", "三角関数"),
    (r"[$]\cos\frac{\pi}{4} = {{c1::\frac{\sqrt{2}}{2}}}[/$]", "三角関数"),

    # ── 3. 複素数とn乗根（10問） ──
    (r"[$]i^2 = {{c1::-1}}[/$]（虚数単位）", "複素数"),
    (r"オイラーの公式：[$]e^{i\theta} = {{c1::\cos\theta + i\sin\theta}}[/$]", "複素数"),
    (r"ド・モアブルの定理：[$](\cos\theta + i\sin\theta)^n = {{c1::\cos(n\theta) + i\sin(n\theta)}}[/$]", "複素数"),
    (r"複素数 [$]z = a + bi[/$] の絶対値は [$]|z| = {{c1::\sqrt{a^2 + b^2}}}[/$]", "複素数"),
    (r"[$]z = a + bi[/$] の共役複素数は [$]\bar{z} = {{c1::a - bi}}[/$]", "複素数"),
    (r"極形式：[$]z = r(\cos\theta + i\sin\theta)[/$] のとき [$]r = {{c1::|z|}}[/$]、[$]\theta[/$] は偏角", "複素数"),
    (r"複素数 [$]z \neq 0[/$] の [$]n[/$] 乗根（$n$ は2以上の整数）は {{c1::$n$ 個}} 存在する", "複素数"),
    (r"[$]z^n = w[/$]（$z \neq 0$）の $n$ 乗根は複素数平面上で {{c1::正$n$角形}} の頂点に並ぶ", "複素数"),
    (r"[$](1 + i)^2 = {{c1::2i}}[/$]", "複素数"),
    (r"[$]z \cdot \bar{z} = {{c1::|z|^2}}[/$]（共役と絶対値の関係）", "複素数"),

    # ── 4. 微分と極限（30問） ──
    (r"[$]\lim_{x \to 0} \frac{\sin x}{x} = {{c1::1}}[/$]（基本極限）", "極限"),
    (r"[$]\lim_{x \to 0} \frac{\tan x}{x} = {{c1::1}}[/$]（基本極限）", "極限"),
    (r"[$]\lim_{x \to 0} \frac{1 - \cos x}{x^2} = {{c1::\frac{1}{2}}}[/$]", "極限"),
    (r"[$]1 - \cos x[/$] を含む極限では分子・分母に [$]{{c1::1 + \cos x}}[/$] を掛けて [$]\sin^2 x[/$] を作る", "極限"),
    (r"[$](\sin x)' = {{c1::\cos x}}[/$]", "微分"),
    (r"[$](\cos x)' = {{c1::-\sin x}}[/$]", "微分"),
    (r"[$](\tan x)' = {{c1::\frac{1}{\cos^2 x}}}[/$]（$\cos x \neq 0$）", "微分"),
    (r"[$](e^x)' = {{c1::e^x}}[/$]", "微分"),
    (r"[$](a^x)' = {{c1::a^x \ln a}}[/$]（$a>0,\; a \neq 1$）", "微分"),
    (r"[$](\ln x)' = {{c1::\frac{1}{x}}}[/$]（$x>0$）", "微分"),
    (r"[$](\log_a x)' = {{c1::\frac{1}{x \ln a}}}[/$]（$x>0$）", "微分"),
    (r"[$](\sin 2x)' = {{c1::2\cos 2x}}[/$]（合成関数の微分）", "微分"),
    (r"[$](\cos 3x)' = {{c1::-3\sin 3x}}[/$]（合成関数の微分）", "微分"),
    (r"[$](e^{2x})' = {{c1::2e^{2x}}}[/$]（合成関数の微分）", "微分"),
    (r"[$](\ln 2x)' = {{c1::\frac{1}{x}}}[/$]（$x>0$）", "微分"),
    (r"[$](\sin^2 x)' = {{c1::\sin 2x}}[/$]（合成関数の微分。$2\sin x\cos x$ でも可）", "微分"),
    (r"[$](\tan^2 x)' = {{c1::\frac{2\tan x}{\cos^2 x}}}[/$]", "微分"),
    (r"[$](x\sin x)' = {{c1::\sin x + x\cos x}}[/$]（積の微分）", "微分"),
    (r"[$](x^2 e^x)' = {{c1::e^x(x^2 + 2x)}}[/$]（積の微分）", "微分"),
    (r"[$](\sin x \cos x)' = {{c1::\cos 2x}}[/$]（積の微分。$\cos^2 x - \sin^2 x$ でも可）", "微分"),
    (r"[$]\left(\frac{1}{x}\right)' = {{c1::-\frac{1}{x^2}}}[/$]（$x \neq 0$）", "微分"),
    (r"[$](x^n)' = {{c1::nx^{n-1}}}[/$]（$n$ は定数、$x>0$）", "微分"),
    (r"[$](\sin^3 x)' = {{c1::3\sin^2 x \cos x}}[/$]（合成関数の微分）", "微分"),
    (r"[$]\lim_{x \to \infty}\left(1 + \frac{1}{x}\right)^x = {{c1::e}}[/$]（自然対数の底）", "極限"),
    (r"導関数の定義：[$]f'(x) = \lim_{h \to 0} \frac{{{c1::f(x+h) - f(x)}}}{h}[/$]", "微分"),
    (r"[$](\cos^2 x)' = {{c1::-\sin 2x}}[/$]（合成関数の微分。$-2\cos x\sin x$ でも可）", "微分"),
    (r"[$](e^{kx})' = {{c1::ke^{kx}}}[/$]（$k$ は定数）", "微分"),
    (r"[$]\lim_{x \to 0} \frac{\sin(ax)}{bx} = {{c1::\frac{a}{b}}}[/$]（$a,\; b$ は定数、$b \neq 0$）", "極限"),
    (r"[$](\sqrt{x})' = {{c1::\frac{1}{2\sqrt{x}}}}[/$]（$x>0$）", "微分"),
    (r"[$](\log_{10} x)' = {{c1::\frac{1}{x \ln 10}}}[/$]（$x>0$）", "微分"),
]

OUTPUT = "math_deck.csv"


def to_mathjax(text: str) -> str:
    """Anki MathJax 記法 \\(...\\) に統一（[$]...[/]$] や $...$ を変換）"""
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("[$$]", i):
            end = text.find("[/$$]", i)
            if end == -1:
                out.append(text[i:])
                break
            content = text[i + 4 : end]
            out.append(f"\\[{content}\\]")
            i = end + 5
        elif text.startswith("[$]", i):
            end = text.find("[/$]", i)
            if end == -1:
                out.append(text[i:])
                break
            content = text[i + 3 : end]
            out.append(f"\\({content}\\)")
            i = end + 4
        elif text[i] == "$":
            end = text.find("$", i + 1)
            if end == -1:
                out.append(text[i])
                i += 1
                continue
            content = text[i + 1 : end]
            out.append(f"\\({content}\\)")
            i = end + 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def fix_cloze_mathjax_spacing(text: str) -> str:
    """Cloze の }} と MathJax の \\) の衝突を防ぐ（Anki 公式ワークアラウンド）"""
    return re.sub(r"(?<![ \t])\}\}(\\\))", r" }}\1", text)


def latex_inline_to_plain(expr: str) -> str:
    """条件・注記用の簡易 LaTeX をプレーンテキストに変換"""
    expr = expr.strip()
    expr = expr.replace(r"\;", ", ")
    expr = expr.replace(r"\neq", "≠")
    expr = expr.replace(r"\geq", "≥")
    expr = expr.replace(r"\frac{\pi}{2}", "π/2")
    expr = expr.replace(r"\pi", "π")
    expr = expr.replace(r"\theta", "θ")
    expr = expr.replace(r"\alpha", "α")
    expr = expr.replace(r"\beta", "β")
    expr = expr.replace(r"\cos", "cos")
    expr = expr.replace(r"\sin", "sin")
    expr = expr.replace(r"\tan", "tan")
    expr = re.sub(r"\s+", " ", expr)
    return expr.strip()


def plainize_conditions(text: str) -> str:
    """メイン数式以外の \\(...\\) をプレーン化（Cloze 内の math は保持）"""
    # Protect cloze regions so their internal math isn't plainized
    cloze_markers = []
    def _protect(m):
        cloze_markers.append(m.group(0))
        return f"__CLOZE_PROTECT_{len(cloze_markers)-1}__"
    protected = re.sub(r"\{\{c\d+::.*?}}", _protect, text, flags=re.DOTALL)

    first_open = protected.find("\\(")
    if first_open == -1:
        return text
    first_close = protected.find("\\)", first_open)
    if first_close == -1:
        return text

    head = protected[: first_close + 2]
    tail = protected[first_close + 2 :]
    tail = re.sub(r"\\\((.*?)\\\)", lambda m: latex_inline_to_plain(m.group(1)), tail)
    restored = head + tail

    for i, orig in enumerate(cloze_markers):
        restored = restored.replace(f"__CLOZE_PROTECT_{i}__", orig)
    return restored


def finalize_card_text(text: str) -> str:
    text = to_mathjax(text)
    text = fix_cloze_mathjax_spacing(text)
    text = plainize_conditions(text)
    return text


assert len(EXPLANATIONS) == len(_RAW_CARDS), "解説数がカード数と一致しません"

CARDS = [
    (finalize_card_text(text), tag, extra)
    for (text, tag), extra in zip(_RAW_CARDS, EXPLANATIONS)
]


def validate_cards(cards):
    """カード数と Cloze 記法の基本チェック"""
    assert len(cards) == 100, f"カード数が100ではありません: {len(cards)}"

    topic_counts = {}
    for text, tag, extra in cards:
        assert "{{c1::" in text, f"Cloze記法がありません: {text[:60]}"
        assert extra.strip(), f"解説が空です: {text[:60]}"
        assert "\\(" in text or "\\[" in text, f"MathJax記法 \\(...\\) を確認: {text[:60]}"
        assert "[$]" not in text and "[/$]" not in text, f"LaTeX記法 [$] が残っています: {text[:60]}"
        assert "$" not in text, f"LaTeX記法 $...$ が残っています: {text[:60]}"
        assert not re.search(r"(?<![ \t])\}\}\\\)", text), (
            f"Cloze }} と MathJax \\) が衝突する可能性: {text[:60]}"
        )
        topic_counts[tag] = topic_counts.get(tag, 0) + 1

    print("トピック別内訳:")
    for tag, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {count}問")

    exp_log = sum(
        topic_counts.get(t, 0)
        for t in ("指数", "対数")
    )
    print(f"\n大分類:")
    print(f"  指数・対数: {exp_log}問")
    print(f"  三角関数系: {sum(topic_counts.get(t, 0) for t in ('三角関数', '加法定理', '倍角', '半角', '合成', '積和', '和積'))}問")
    print(f"  複素数: {topic_counts.get('複素数', 0)}問")
    print(f"  微分・極限: {sum(topic_counts.get(t, 0) for t in ('微分', '極限'))}問")


def main():
    validate_cards(CARDS)

    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Text", "Tag", "Extra"])
        for text, tag, extra in CARDS:
            writer.writerow([text, tag, extra])

    print(f"\n✓ {OUTPUT} を生成しました（{len(CARDS)}問）")


if __name__ == "__main__":
    main()