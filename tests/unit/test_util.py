"""Unit tests for util.py — the importable logic of the XML2RDF web UI."""
import util


def test_include_css_concatenates_into_style_tag(tmp_path):
    a = tmp_path / "a.css"
    b = tmp_path / "b.css"
    a.write_text("body{color:red}", encoding="utf-8")
    b.write_text(".x{margin:0}", encoding="utf-8")

    captured = {}

    class _FakeSt:
        def markdown(self, html, unsafe_allow_html=False):
            captured["html"] = html
            captured["unsafe"] = unsafe_allow_html

    util.include_css(_FakeSt(), [str(a), str(b)])
    assert captured["unsafe"] is True
    assert captured["html"].startswith("<style>")
    assert "body{color:red}" in captured["html"]
    assert ".x{margin:0}" in captured["html"]
