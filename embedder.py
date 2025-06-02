from pathlib import Path
from sentence_transformers import SentenceTransformer, models

MODEL_PATH = Path("local_models/intfloat/multilingual-e5-small")

# Проверка файлов
REQUIRED = ["config.json", "tokenizer_config.json", "pytorch_model.bin", "sentencepiece.bpe.model", "modules.json"]
missing = [f for f in REQUIRED if not (MODEL_PATH / f).exists()]
if missing:
    raise RuntimeError(f"❌ Отсутствуют файлы: {missing}")

# Загрузка модулей вручную
print("📦 Загружаем SentenceTransformer напрямую из модулей:", MODEL_PATH)
word_embedding_model = models.Transformer(str(MODEL_PATH), do_lower_case=True)
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())

model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

def generate_embedding(text: str) -> list:
    return model.encode(f"passage: {text}").tolist()
