import json
from pathlib import Path

from scripts import convert_chunks_to_csat as conv


def test_empty_opt5(tmp_path):
    # Replace NLP with a lightweight stub to avoid spaCy dependency during tests
    class FakeDoc:
        pass

    class FakeNLP:
        def pipe(self, articles, batch_size=64):
            for _ in articles:
                yield FakeDoc()

        def __call__(self, text):
            return FakeDoc()

    conv._nlp = FakeNLP()

    data = [
        {
            "id": "test1.txt",
            "source": "race",
            "article": "",
            "questions": [
                {
                    "question": "What is X?",
                    "options": ["A", "B", "C", "D"],
                    "answer": "A",
                }
            ],
        }
    ]

    in_file = tmp_path / "chunks.json"
    out_file = tmp_path / "chunks_csat.json"
    in_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    conv.convert_file(tmp_path, in_file, out_file, use_llm=False, api_key="", workers=1, empty_opt5=True)

    out = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(out, list)
    assert out, "converted output should not be empty"
    first = out[0]
    assert first.get("p1_opt5") == "", f"Expected empty p1_opt5, got: {first.get('p1_opt5')!r}"
